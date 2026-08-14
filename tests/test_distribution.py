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
            if path.parent == ROOT / "docs" and path.name.startswith("handoff_"):
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
        self.assertEqual(8, html.count('data-help='))
        self.assertIn('id="release-memory"', html)
        self.assertIn('id="model-select"', html)
        self.assertIn('id="import-source"', html)
        self.assertIn('id="convert-source"', html)
        self.assertIn('id="import-enriched"', html)
        self.assertIn('id="shots-list"', html)
        self.assertIn('id="add-shot"', html)
        self.assertNotIn('id="remove-shot"', html)
        self.assertIn('id="total-duration"', html)
        self.assertNotIn('id="micro-input"', html)
        self.assertNotIn('id="micro-output"', html)
        self.assertIn('fetch("/api/release"', script)
        self.assertIn("releaseMemory", script)
        self.assertIn("enrich-output", script)
        self.assertIn("duration_seconds", script)
        self.assertIn('type="number"', script)
        self.assertIn('step="0.5"', script)
        self.assertIn("convert_modules", script)
        self.assertIn('api("convert", text)', script)
        self.assertIn('draggable="true"', script)
        self.assertIn('"dragstart"', script)
        self.assertIn('"drop"', script)
        self.assertIn('fetch("/api/model"', script)
        self.assertIn("scrollIntoView", script)
        self.assertIn('id="vision-section"', html)
        self.assertIn('id="vision-file"', html)
        self.assertIn('id="vision-preview"', html)
        self.assertIn('id="vision-instruction"', html)
        self.assertIn('id="vision-analyze"', html)
        self.assertIn('id="vision-output"', html)
        self.assertIn('id="vision-to-source"', html)
        self.assertIn('fetch("/api/vision/status"', script)
        self.assertIn('fetch("/api/vision/download"', script)
        self.assertIn('fetch("/api/vision/caption"', script)

    def test_frontend_recovers_from_stale_client_state_and_uses_a_versioned_script(self):
        html = (ROOT / "static" / "index.html").read_text(encoding="utf-8")
        script = (ROOT / "static" / "app.js").read_text(encoding="utf-8")

        self.assertIn('/static/app.js?v=', html)
        self.assertIn('Object.prototype.hasOwnProperty.call(I18N, storedLanguage)', script)

    def test_one_click_entrypoints_and_readme_exist(self):
        self.assertTrue((ROOT / "install-and-run.bat").is_file())
        self.assertTrue((ROOT / "run.bat").is_file())
        launcher = (ROOT / "run.bat").read_text(encoding="utf-8")
        self.assertIn("PYTHONNOUSERSITE=1", launcher)
        self.assertIn('if exist "local-settings.bat" call "local-settings.bat"', launcher)
        self.assertIn("FAITHFUL_H3_LLAMA_BIN", launcher)
        self.assertNotIn("import torch", launcher)
        requirements = (ROOT / "requirements.txt").read_text(encoding="utf-8")
        self.assertIn("huggingface-hub==1.3.7", requirements)
        self.assertNotIn("torch", requirements)
        installer = (ROOT / "install-and-run.bat").read_text(encoding="utf-8")
        self.assertIn("scripts\\install_runtime.py", installer)
        self.assertIn("FH3_MODEL", installer)
        readme = (ROOT / "README.md").read_text(encoding="utf-8")
        self.assertIn("install-and-run.bat", readme)
        self.assertIn("FL2VA", readme)
        self.assertIn("Ref2VA", readme)
        changelog = (ROOT / "CHANGELOG.md").read_text(encoding="utf-8")
        self.assertIn("## 1.2.0 - 2026-08-13", changelog)
        self.assertIn("Release memory", changelog)

    def test_public_distribution_uses_liuliu_brand(self):
        public_files = [
            ROOT / "LICENSE",
            ROOT / "README.md",
            ROOT / "CHANGELOG.md",
            ROOT / "install-and-run.bat",
            ROOT / "run.bat",
            ROOT / "app" / "main.py",
            ROOT / "static" / "index.html",
        ]
        combined = "\n".join(path.read_text(encoding="utf-8") for path in public_files)
        self.assertIn("liuliu", combined)
        self.assertNotIn("liusheng", combined.lower())


if __name__ == "__main__":
    unittest.main()
