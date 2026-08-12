import base64
import json
import tempfile
import unittest
from pathlib import Path

from app.model_files import MODEL_SHA256, MODEL_SIZE, verify_model_file
from app.model_runtime import map_checkpoint_name, mapped_quantization_map


class ModelMappingTests(unittest.TestCase):
    def test_expected_checkpoint_identity_is_v2(self):
        self.assertEqual(8957488932, MODEL_SIZE)
        self.assertEqual("eb03df5ccba4536eb64cf096c08b068eb84cfd2d2aa798cd45f31a0f67e339e6", MODEL_SHA256)

    def test_checkpoint_verifier_rejects_wrong_size_before_hashing(self):
        with tempfile.TemporaryDirectory() as directory:
            checkpoint = Path(directory) / "checkpoint.safetensors"
            checkpoint.write_bytes(b"not the model")
            with self.assertRaisesRegex(RuntimeError, "size"):
                verify_model_file(checkpoint)

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


if __name__ == "__main__":
    unittest.main()
