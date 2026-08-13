import base64
import gc
import json
import sys
import tempfile
import types
import unittest
from unittest.mock import patch
from pathlib import Path

from app.model_files import MODEL_SPECS, verify_model_file
from app.model_runtime import (
    JsonObjectStoppingCriteria,
    ModelRuntime,
    map_checkpoint_name,
    mapped_quantization_map,
    normalize_checkpoint_state,
    resolve_stop_token_ids,
)


class ModelMappingTests(unittest.TestCase):
    def test_release_unloads_model_and_clears_cuda_cache(self):
        runtime = ModelRuntime(Path("models"))
        runtime._model = object()
        runtime._tokenizer = object()
        fake_cuda = types.SimpleNamespace(is_available=lambda: True, empty_cache=lambda: None, ipc_collect=lambda: None)
        fake_torch = types.SimpleNamespace(cuda=fake_cuda)
        with patch.dict(sys.modules, {"torch": fake_torch}), \
             patch.object(fake_cuda, "empty_cache") as empty_cache, \
             patch.object(fake_cuda, "ipc_collect") as ipc_collect, \
             patch.object(gc, "collect") as collect:
            result = runtime.release()

        self.assertTrue(result["released"])
        self.assertFalse(runtime.loaded)
        collect.assert_called_once()
        empty_cache.assert_called_once()
        ipc_collect.assert_called_once()

    def test_release_is_safe_when_model_is_not_loaded(self):
        runtime = ModelRuntime(Path("models"))
        result = runtime.release()
        self.assertFalse(result["released"])
        self.assertFalse(result["loaded"])

    def test_switching_model_releases_the_loaded_runtime(self):
        runtime = ModelRuntime({"4b": Path("models/4b"), "9b": Path("models/9b")})
        runtime._model = object()
        runtime._tokenizer = object()
        with patch.object(runtime, "release", wraps=runtime.release) as release:
            runtime.select("4b")
        release.assert_called_once()
        self.assertEqual("4b", runtime.selected_model)

    def test_expected_checkpoint_identity_is_v2(self):
        self.assertEqual(8957488932, MODEL_SPECS["9b"].size)
        self.assertEqual("eb03df5ccba4536eb64cf096c08b068eb84cfd2d2aa798cd45f31a0f67e339e6", MODEL_SPECS["9b"].sha256)

    def test_expected_4b_checkpoint_identity(self):
        self.assertEqual(4844829456, MODEL_SPECS["4b"].size)
        self.assertEqual("3563d71540c755b3004dd4d514a2478c96d5f5e7ff29b4162a391b2d79a0071a", MODEL_SPECS["4b"].sha256)

    def test_checkpoint_verifier_rejects_wrong_size_before_hashing(self):
        with tempfile.TemporaryDirectory() as directory:
            checkpoint = Path(directory) / "checkpoint.safetensors"
            checkpoint.write_bytes(b"not the model")
            with self.assertRaisesRegex(RuntimeError, "size"):
                verify_model_file(checkpoint, MODEL_SPECS["9b"])

    def test_maps_root_modules(self):
        self.assertEqual("model.embed_tokens.weight._data", map_checkpoint_name("token_embd.weight._data"))
        self.assertEqual("model.norm.weight", map_checkpoint_name("output_norm.weight"))
        self.assertEqual("lm_head.weight._scale", map_checkpoint_name("output.weight._scale"))

    def test_maps_linear_and_full_attention_layers(self):
        self.assertEqual("model.layers.0.linear_attn.in_proj_qkv.weight._data", map_checkpoint_name("blk.0.attn_qkv.weight._data"))
        self.assertEqual("model.layers.0.linear_attn.A_log", map_checkpoint_name("blk.0.ssm_a"))
        self.assertEqual("model.layers.3.self_attn.q_proj.weight._scale", map_checkpoint_name("blk.3.attn_q.weight._scale"))
        self.assertEqual("model.layers.3.mlp.down_proj.weight._data", map_checkpoint_name("blk.3.ffn_down.weight._data"))

    def test_maps_quantization_metadata(self):
        raw = {"blk.0.attn_qkv": {"weights": "qint8", "activations": "none"}}
        metadata = {"quantization_map_base64": base64.b64encode(json.dumps(raw).encode()).decode()}
        mapped = mapped_quantization_map(metadata)
        self.assertIn("model.layers.0.linear_attn.in_proj_qkv", mapped)

    def test_4b_linear_attention_a_is_converted_to_transformers_log_form(self):
        import torch

        state = {"model.layers.0.linear_attn.A_log": torch.tensor([-1.0, -4.0])}
        converted = normalize_checkpoint_state(state, MODEL_SPECS["4b"])
        torch.testing.assert_close(converted["model.layers.0.linear_attn.A_log"], torch.tensor([0.0, 1.3862944]))

    def test_9b_v2_linear_attention_a_is_already_log_form(self):
        import torch

        original = torch.tensor([0.5, 1.5])
        state = {"model.layers.0.linear_attn.A_log": original}
        converted = normalize_checkpoint_state(state, MODEL_SPECS["9b"])
        self.assertIs(original, converted["model.layers.0.linear_attn.A_log"])

    def test_runtime_materializes_the_bf16_checkpoint_with_bf16_skeleton(self):
        runtime_source = (Path(__file__).parents[1] / "app" / "model_runtime.py").read_text(encoding="utf-8")
        self.assertIn("model = model.to(dtype=torch.bfloat16)", runtime_source)
        self.assertIn("if config.tie_word_embeddings", runtime_source)
        self.assertIn("model.tie_weights()", runtime_source)

    def test_runtime_stops_on_chat_and_model_end_tokens(self):
        tokenizer = types.SimpleNamespace(
            eos_token_id=248046,
            convert_tokens_to_ids=lambda token: {"<|im_end|>": 248046, "<|endoftext|>": 248044}[token],
        )
        model = types.SimpleNamespace(config=types.SimpleNamespace(eos_token_id=248044))
        self.assertEqual([248044, 248046], resolve_stop_token_ids(tokenizer, model))

    def test_json_stopping_criteria_stops_after_complete_root_object(self):
        class Tokenizer:
            @staticmethod
            def decode(token_ids, skip_special_tokens=False):
                return "".join(chr(token_id) for token_id in token_ids)

        criterion = JsonObjectStoppingCriteria(Tokenizer(), prompt_length=2)
        incomplete = [[1, 2] + [ord(char) for char in '{"shots":[{']]
        complete = [[1, 2] + [ord(char) for char in '{"shots":[]}']]
        quoted_brace = [[1, 2] + [ord(char) for char in '{"scene":"}"}']]
        self.assertFalse(criterion(incomplete, None))
        self.assertTrue(criterion(complete, None))
        self.assertTrue(criterion(quoted_brace, None))

    def test_runtime_prefers_available_gguf_backend(self):
        with tempfile.TemporaryDirectory() as directory:
            model = Path(directory) / "model.gguf"
            model.write_bytes(b"gguf")
            runtime = ModelRuntime({"4b": Path(directory), "9b": Path(directory)}, gguf_paths={"4b": model})
            runtime.select("4b")
            self.assertEqual("gguf", runtime.backend)
            runtime.select("9b")
            self.assertEqual("quanto", runtime.backend)


if __name__ == "__main__":
    unittest.main()
