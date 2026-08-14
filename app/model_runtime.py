import base64
import gc
import json
import threading
import time
from pathlib import Path

from .model_files import MODEL_SPECS, ModelSpec
from .gguf_runtime import GgufRuntime


def map_checkpoint_name(name: str) -> str | None:
    if name.startswith("mtp.") or name.startswith("v."):
        return None
    roots = {
        "token_embd": "model.embed_tokens",
        "output_norm": "model.norm",
        "output": "lm_head",
    }
    for source, target in roots.items():
        if name == source or name.startswith(source + "."):
            return target + name[len(source):]
    if not name.startswith("blk."):
        return name
    parts = name.split(".", 2)
    if len(parts) != 3:
        return name
    layer, suffix = parts[1], parts[2]
    mapping = {
        "attn_norm": "input_layernorm",
        "post_attention_norm": "post_attention_layernorm",
        "ffn_gate": "mlp.gate_proj",
        "ffn_up": "mlp.up_proj",
        "ffn_down": "mlp.down_proj",
        "attn_qkv": "linear_attn.in_proj_qkv",
        "attn_gate": "linear_attn.in_proj_z",
        "ssm_alpha": "linear_attn.in_proj_a",
        "ssm_beta": "linear_attn.in_proj_b",
        "ssm_out": "linear_attn.out_proj",
        "ssm_conv1d": "linear_attn.conv1d",
        "ssm_dt": "linear_attn.dt_bias",
        "ssm_a": "linear_attn.A_log",
        "ssm_norm": "linear_attn.norm",
        "attn_q": "self_attn.q_proj",
        "attn_k": "self_attn.k_proj",
        "attn_v": "self_attn.v_proj",
        "attn_output": "self_attn.o_proj",
        "attn_q_norm": "self_attn.q_norm",
        "attn_k_norm": "self_attn.k_norm",
    }
    for source, target in mapping.items():
        if suffix == source or suffix.startswith(source + "."):
            suffix = target + suffix[len(source):]
            break
    return f"model.layers.{layer}.{suffix}"


def mapped_quantization_map(metadata: dict) -> dict:
    encoded = metadata.get("quantization_map_base64", "")
    if not encoded:
        raise ValueError("Checkpoint has no Quanto quantization map.")
    raw = json.loads(base64.b64decode(encoded).decode("utf-8"))
    return {mapped: value for key, value in raw.items() if (mapped := map_checkpoint_name(key))}


def normalize_checkpoint_state(state: dict, spec: ModelSpec) -> dict:
    if spec.ssm_a_is_log:
        return state
    import torch

    for name, tensor in list(state.items()):
        if name.endswith(".linear_attn.A_log"):
            if torch.any(tensor >= 0):
                raise ValueError(f"Invalid non-log SSM A tensor in {spec.id}: expected negative values.")
            state[name] = torch.log(-tensor.float()).to(dtype=tensor.dtype)
    return state


def mapped_state_dict(checkpoint: Path, spec: ModelSpec = MODEL_SPECS["9b"]) -> tuple[dict, dict]:
    from safetensors import safe_open

    state = {}
    with safe_open(str(checkpoint), framework="pt", device="cpu") as reader:
        quant_map = mapped_quantization_map(reader.metadata() or {})
        for key in reader.keys():
            mapped = map_checkpoint_name(key)
            if mapped:
                state[mapped] = reader.get_tensor(key)
    return normalize_checkpoint_state(state, spec), quant_map


def resolve_stop_token_ids(tokenizer, model) -> list[int]:
    candidates = [
        getattr(getattr(model, "config", None), "eos_token_id", None),
        getattr(tokenizer, "eos_token_id", None),
    ]
    for token in ("<|im_end|>", "<|endoftext|>"):
        try:
            candidates.append(tokenizer.convert_tokens_to_ids(token))
        except (AttributeError, KeyError, TypeError, ValueError):
            pass
    return sorted({int(token_id) for token_id in candidates if token_id is not None and int(token_id) >= 0})


class JsonObjectStoppingCriteria:
    def __init__(self, tokenizer, prompt_length: int):
        self.tokenizer = tokenizer
        self.prompt_length = int(prompt_length)

    def __call__(self, input_ids, scores, **kwargs) -> bool:
        token_ids = input_ids[0][self.prompt_length:]
        if hasattr(token_ids, "tolist"):
            token_ids = token_ids.tolist()
        text = self.tokenizer.decode(token_ids, skip_special_tokens=False)
        depth = 0
        started = False
        in_string = False
        escaped = False
        for char in text:
            if in_string:
                if escaped:
                    escaped = False
                elif char == "\\":
                    escaped = True
                elif char == '"':
                    in_string = False
                continue
            if char == '"':
                in_string = True
            elif char == "{":
                started = True
                depth += 1
            elif char == "}" and started:
                depth -= 1
                if depth == 0:
                    return True
        return False


class ModelRuntime:
    def __init__(self, model_dirs: Path | dict[str, Path], selected_model: str = "9b", gguf_paths: dict[str, Path] | None = None,
                 gguf_binary: Path | None = None):
        if isinstance(model_dirs, dict):
            self.model_dirs = {key: Path(value) for key, value in model_dirs.items()}
        else:
            self.model_dirs = {"9b": Path(model_dirs)}
        self.selected_model = selected_model
        self._model = None
        self._tokenizer = None
        self.gguf_paths = {key: Path(value) for key, value in (gguf_paths or {}).items()}
        self.gguf_binary = Path(gguf_binary) if gguf_binary else None
        self._gguf = None
        self._lock = threading.RLock()

    @property
    def loaded(self) -> bool:
        return self._model is not None or bool(self._gguf and self._gguf.loaded)

    @property
    def backend(self) -> str:
        return "gguf" if self.selected_model in self.gguf_paths and self.gguf_paths[self.selected_model].is_file() else "quanto"

    @property
    def progress(self) -> dict:
        if self._gguf:
            return self._gguf.progress
        return {
            "active": False,
            "generated_tokens": 0,
            "tokens_per_second": 0.0,
            "elapsed_seconds": 0.0,
        }

    @property
    def model_dir(self) -> Path:
        return self.model_dirs[self.selected_model]

    @property
    def spec(self) -> ModelSpec:
        return MODEL_SPECS[self.selected_model]

    def select(self, model_id: str) -> None:
        if model_id not in self.model_dirs or model_id not in MODEL_SPECS:
            raise ValueError(f"Unknown model: {model_id}")
        with self._lock:
            if model_id != self.selected_model:
                self.release()
                self.selected_model = model_id

    def _use_gguf(self) -> bool:
        return self.backend == "gguf"

    def load(self):
        with self._lock:
            if self.loaded:
                return
            import torch
            from optimum.quanto import requantize
            from transformers import AutoTokenizer, Qwen3_5ForCausalLM, Qwen3_5TextConfig

            if not torch.cuda.is_available():
                raise RuntimeError("A CUDA-capable NVIDIA GPU is required for the local INT8 model.")
            with open(self.model_dir / "config.json", encoding="utf-8") as handle:
                config_data = json.load(handle)
            config = Qwen3_5TextConfig(**config_data.get("text_config", config_data))
            with torch.device("meta"):
                model = Qwen3_5ForCausalLM(config)
            # The Quanto checkpoint stores scales and non-quantized weights in BF16.
            model = model.to(dtype=torch.bfloat16)
            state, quant_map = mapped_state_dict(self.model_dir / self.spec.filename, self.spec)
            requantize(model, state, quant_map, device=torch.device("cuda"))
            if config.tie_word_embeddings:
                model.tie_weights()
            model.eval()
            tokenizer = AutoTokenizer.from_pretrained(self.model_dir, trust_remote_code=False)
            chat_template = self.model_dir / "chat_template.jinja"
            if chat_template.is_file():
                tokenizer.chat_template = chat_template.read_text(encoding="utf-8")
            self._model, self._tokenizer = model, tokenizer

    def release(self) -> dict:
        with self._lock:
            released = self.loaded or self._tokenizer is not None
            had_quanto_model = self._model is not None or self._tokenizer is not None
            self._model = None
            self._tokenizer = None
            if self._gguf:
                self._gguf.stop()
                self._gguf = None
            gc.collect()
            if not had_quanto_model:
                return {"released": released, "loaded": False}
            try:
                import torch

                if torch.cuda.is_available():
                    torch.cuda.empty_cache()
                    torch.cuda.ipc_collect()
            except (ImportError, OSError):
                pass
            return {"released": released, "loaded": False}

    def generate(self, user_text: str, system_text: str, *, temperature: float, top_p: float, max_new_tokens: int = 1400, stop_on_json: bool = False) -> str:
        with self._lock:
            started = time.monotonic()
            if self._use_gguf():
                if not self._gguf:
                    self._gguf = GgufRuntime(self.gguf_paths[self.selected_model], binary=self.gguf_binary)
                result = self._gguf.generate(user_text, system_text, temperature=temperature, top_p=top_p,
                                              max_new_tokens=max_new_tokens, stop_on_json=stop_on_json)
                if not result or "�" in result or (result.count("?") > 3 and any("\u3400" <= c <= "\u9fff" for c in user_text)):
                    raise RuntimeError("The selected GGUF backend returned unreadable text; no H3 output was returned.")
                return result
            self.load()
            import torch

            messages = [{"role": "system", "content": system_text}, {"role": "user", "content": user_text}]
            prompt = self._tokenizer.apply_chat_template(messages, tokenize=False, add_generation_prompt=True, enable_thinking=False)
            inputs = self._tokenizer(prompt, return_tensors="pt").to("cuda")
            do_sample = temperature > 0.05
            stop_token_ids = resolve_stop_token_ids(self._tokenizer, self._model)
            stopping_criteria = None
            if stop_on_json:
                from transformers import StoppingCriteriaList

                stopping_criteria = StoppingCriteriaList([
                    JsonObjectStoppingCriteria(self._tokenizer, inputs.input_ids.shape[1])
                ])
            with torch.inference_mode():
                output = self._model.generate(
                    **inputs,
                    max_new_tokens=max_new_tokens,
                    do_sample=do_sample,
                    temperature=max(temperature, 0.01),
                    top_p=top_p,
                    eos_token_id=stop_token_ids,
                    pad_token_id=self._tokenizer.pad_token_id,
                    stopping_criteria=stopping_criteria,
                )
            generated = output[0, inputs.input_ids.shape[1]:]
            return self._tokenizer.decode(generated, skip_special_tokens=True).strip()
