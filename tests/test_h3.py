import unittest

from app import h3


class H3ContractTests(unittest.TestCase):
    def test_mode_names_are_only_fl2va_and_ref2va(self):
        self.assertEqual("fl2va", h3.normalize_mode("FL2VA"))
        self.assertEqual("ref2va", h3.normalize_mode("Ref2VA"))

    def test_fl2va_contract_and_header(self):
        text = "integrated_multimodal_description: [Shot 1] A.\noverall_soundscape: N/A\nnon_diegetic_music: N/A"
        output = h3.normalize_output(text, "fl2va")
        self.assertTrue(output.startswith(h3.FL2VA_HEADER))
        self.assertTrue(h3.audit(output, "fl2va")["valid"])

    def test_ref2va_requires_all_six_fields(self):
        text = "subject_definitions: x\nsummary: x\nretention_analysis: x\ndetailed_description: x\noverall_soundscape: N/A\nnon_diegetic_music: N/A"
        self.assertTrue(h3.audit(text, "ref2va")["valid"])

    def test_micro_edit_language_and_structure_guards(self):
        source = "integrated_multimodal_description: [Shot 1] 人物奔跑。\noverall_soundscape: N/A\nnon_diegetic_music: N/A"
        good = "integrated_multimodal_description: [Shot 1] A person runs.\noverall_soundscape: N/A\nnon_diegetic_music: N/A"
        bad = "integrated_multimodal_description: A person runs.\noverall_soundscape: N/A\nnon_diegetic_music: N/A"
        self.assertTrue(h3.has_untranslated_chinese(source))
        self.assertFalse(h3.has_untranslated_chinese(good))
        self.assertTrue(h3.contract_matches(source, good, "fl2va"))
        self.assertFalse(h3.contract_matches(source, bad, "fl2va"))

    def test_prompts_are_non_creative_where_required(self):
        self.assertIn("Never add, remove", h3.conversion_system("fl2va"))
        self.assertIn("Do not add, remove", h3.micro_edit_system("ref2va"))


if __name__ == "__main__":
    unittest.main()
