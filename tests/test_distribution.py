import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent


class DistributionContractTests(unittest.TestCase):
    def test_published_sources_do_not_reference_a_host_project(self):
        forbidden = (("Wan2" + "GP").casefold(), ("Deep" + "BeepMeep").casefold())
        text_extensions = {".bat", ".html", ".js", ".json", ".md", ".py", ".txt"}
        for path in ROOT.rglob("*"):
            if not path.is_file() or path.suffix.lower() not in text_extensions:
                continue
            content = path.read_text(encoding="utf-8", errors="ignore").casefold()
            for marker in forbidden:
                self.assertNotIn(marker, content, str(path.relative_to(ROOT)))

    def test_frontend_is_utf8_localized_and_standalone(self):
        html = (ROOT / "static" / "index.html").read_text(encoding="utf-8")
        script = (ROOT / "static" / "app.js").read_text(encoding="utf-8")
        combined = html + script
        self.assertIn("&#31616;&#20307;&#20013;&#25991;", combined)
        self.assertIn("&#32321;&#39636;&#20013;&#25991;", combined)
        self.assertIn('"zh-CN"', combined)
        self.assertIn('"zh-TW"', combined)
        self.assertIn("Prompt enrichment", combined)
        self.assertNotIn("Wan2" + "GP", combined)
        self.assertNotIn("返回生成页", combined)
        self.assertEqual(5, html.count('class="help"'))
        self.assertEqual(3, html.count('class="copy output-copy"'))
        self.assertNotIn('class="copy output-copy" data-target="source-input"', html)

    def test_one_click_entrypoints_and_readme_exist(self):
        self.assertTrue((ROOT / "install-and-run.bat").is_file())
        self.assertTrue((ROOT / "run.bat").is_file())
        readme = (ROOT / "README.md").read_text(encoding="utf-8")
        self.assertIn("install-and-run.bat", readme)
        self.assertIn("FL2VA", readme)
        self.assertIn("Ref2VA", readme)


if __name__ == "__main__":
    unittest.main()
