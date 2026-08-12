import base64
import json
import threading
from pathlib import Path

from .model_files import MODEL_FILE


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


def mapped_state_dict(checkpoint: Path) -> tuple[dict, dict]:
    from safetensors import safe_open

    state = {}
    with safe_open(str(checkpoint), framework="pt", device="cpu") as reader:
        quant_map = mapped_quantization_map(reader.metadata() or {})
        for key in reader.keys():
            mapped = map_checkpoint_name(key)
            if mapped:
                state[mapped] = reader.get_tensor(key)
    return state, quant_map


class ModelRuntime:
    def __init__(self, model_dir: Path):
        self.model_dir = Path(model_dir)
        self._model = None
        self._tokenizer = None
        self._lock = threading.RLock()

    @property
    def loaded(self) -> bool:
        return self._model is not None

    def load(self):
        with self._lock:
            if self.loaded:
                return
            import torch
            from optimum.quanto import requantize
            from transformers import AutoTokenizer, Qwen3_5ForCausalLM, Qwen3_5TextConfig

            if not torch.cuda.is_available():
                raise RuntimeError("A CUDA-capable NVIDIA GPU is required for the 9B INT8 model.")
            with open(self.model_dir / "config.json", encoding="utf-8") as handle:
                config_data = json.load(handle)
            config = Qwen3_5TextConfig(**config_data.get("text_config", config_data))
            with torch.device("meta"):
                model = Qwen3_5ForCausalLM(config)
            state, quant_map = mapped_state_dict(self.model_dir / MODEL_FILE)
            requantize(model, state, quant_map, device=torch.device("cuda"))
            model.eval()
            tokenizer = AutoTokenizer.from_pretrained(self.model_dir, trust_remote_code=False)
            chat_template = self.model_dir / "chat_template.jinja"
            if chat_template.is_file():
                tokenizer.chat_template = chat_template.read_text(encoding="utf-8")
            self._model, self._tokenizer = model, tokenizer

    def generate(self, user_text: str, system_text: str, *, temperature: float, top_p: float, max_new_tokens: int = 1400) -> str:
        with self._lock:
            self.load()
            import torch

            messages = [{"role": "system", "content": system_text}, {"role": "user", "content": user_text}]
            prompt = self._tokenizer.apply_chat_template(messages, tokenize=False, add_generation_prompt=True, enable_thinking=False)
            inputs = self._tokenizer(prompt, return_tensors="pt").to("cuda")
            do_sample = temperature > 0.05
            with torch.inference_mode():
                output = self._model.generate(
                    **inputs,
                    max_new_tokens=max_new_tokens,
                    do_sample=do_sample,
                    temperature=max(temperature, 0.01),
                    top_p=top_p,
                    pad_token_id=self._tokenizer.eos_token_id,
                )
            generated = output[0, inputs.input_ids.shape[1]:]
            return self._tokenizer.decode(generated, skip_special_tokens=True).strip()
