import unittest

from scripts.benchmark_h3 import count_output_shots


class BenchmarkH3Tests(unittest.TestCase):
    def test_fixed_header_reference_is_not_counted_as_an_output_shot(self):
        output = """For the target video, <Picture 1> (from [Shot 1]) is fully referenced.

integrated_multimodal_description: [Shot 1] One. [Shot 2] Two. [Shot 3] Three.
overall_soundscape: N/A
non_diegetic_music: N/A"""
        self.assertEqual(3, count_output_shots(output))


if __name__ == "__main__":
    unittest.main()
