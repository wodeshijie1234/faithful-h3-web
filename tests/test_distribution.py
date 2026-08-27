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
            # local-settings.bat is a machine-local, gitignored configuration
            # file and is never part of the public distribution.
            if path.name.lower() in {"local-settings.bat", "local-settings.example.bat"}:
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
        self.assertIn('rel="icon"', html)
        self.assertNotIn("Wan2" + "GP", combined)
        self.assertEqual(8, html.count('data-help='))
        self.assertIn('id="release-memory"', html)
        self.assertIn('id="model-select"', html)
        self.assertIn('id="download-dialog"', html)
        self.assertIn('value="4b"', html)
        self.assertIn('value="9b"', html)
        self.assertIn('value="vision-fast"', html)
        self.assertIn('value="vision-accurate"', html)
        self.assertIn('id="download-confirm"', html)
        self.assertNotIn('id="import-source"', html)
        self.assertIn('id="convert-source"', html)
        self.assertNotIn('id="import-enriched"', html)
        self.assertIn('id="use-enriched"', html)
        self.assertNotIn('id="shots-list"', html)
        self.assertNotIn('id="add-shot"', html)
        self.assertNotIn('id="total-duration"', html)
        self.assertNotIn('id="micro-input"', html)
        self.assertNotIn('id="micro-output"', html)
        self.assertIn('fetch("/api/release"', script)
        self.assertIn("releaseMemory", script)
        self.assertIn("enrich-output", script)
        self.assertNotIn("duration_seconds", script)
        self.assertNotIn("convert_modules", script)
        self.assertNotIn("decompose", script)
        self.assertNotIn("moduleEditor", script)
        self.assertIn('api("convert", payload.source', script)
        self.assertIn('row.draggable = true', script)
        self.assertIn('dragstart', script)
        self.assertNotIn('shot-module', script)
        self.assertIn('fetch("/api/model"', script)
        self.assertIn("scrollIntoView", script)
        self.assertIn('id="vision-section"', html)
        self.assertIn('id="vision-view"', html)
        self.assertEqual(4, html.count('data-workspace-tools='))
        self.assertIn('id="workspace-dialog"', html)
        self.assertIn('id="workspace-record-list"', html)
        self.assertIn('IndexedDbWorkspaceBackend', script)
        self.assertIn('saveDraft', script)
        self.assertIn('addHistory', script)
        self.assertIn('enqueue', script)
        self.assertIn('deleteHistory', script)
        self.assertIn('id="h3-view"', html)
        self.assertEqual(4, html.count('class="view-tab'))
        h3_tab = html.index('data-view="h3"')
        enrich_tab = html.index('data-view="enrich"')
        vision_tab = html.index('data-view="vision"')
        storyboard_tab = html.index('data-view="storyboard"')
        self.assertLess(h3_tab, enrich_tab)
        self.assertLess(enrich_tab, vision_tab)
        self.assertLess(vision_tab, storyboard_tab)
        self.assertIn('data-view="vision"', html)
        self.assertIn('data-view="storyboard"', html)
        self.assertIn('data-view="enrich"', html)
        self.assertIn('data-view="h3"', html)
        self.assertIn('id="h3-view" class="app-view"', html)
        self.assertIn('id="enrich-view" class="app-view" hidden', html)
        self.assertIn('id="vision-view" class="app-view" hidden', html)
        self.assertIn('id="storyboard-view" class="app-view" hidden', html)
        self.assertIn('class="view-tab active" data-view="h3"', html)
        enrich_view = html[html.index('id="enrich-view"'):html.index('id="vision-view"')]
        h3_view = html[html.index('id="h3-view"'):html.index('id="enrich-view"')]
        self.assertIn('id="enrich-input"', enrich_view)
        self.assertIn('id="enrich-output"', enrich_view)
        self.assertIn('id="target-length"', enrich_view)
        self.assertIn('id="target-length-value"', enrich_view)
        self.assertIn('target_length', script)
        self.assertNotIn('id="enrich-input"', h3_view)
        self.assertIn('location.hash', script)
        self.assertIn('id="vision-file"', html)
        self.assertIn('id="vision-preview"', html)
        self.assertIn('id="vision-instruction"', html)
        self.assertIn('id="vision-analyze"', html)
        self.assertIn('id="vision-output"', html)
        self.assertNotIn('id="vision-to-source"', html)
        self.assertIn('fetch("/api/status"', script)
        self.assertNotIn('id="vision-download"', html)
        self.assertNotIn('fetch("/api/vision/download"', script)
        self.assertIn('fetch("/api/vision/caption"', script)
        self.assertIn('fetch("/api/progress"', script)
        self.assertIn("tokens_per_second", script)
        self.assertIn("token/s", script)
        self.assertIn('id="release-toast"', html)
        self.assertNotIn('id="model-status" class="status status-neutral" data-h3-control', html)
        self.assertIn('data.phase === "loading"', script)
        self.assertIn("formatReleaseSummary", script)
        self.assertIn('id="storyboard-shot-list"', html)
        self.assertIn('id="storyboard-model"', html)
        self.assertIn('id="storyboard-generate"', html)
        self.assertIn('fetch("/api/storyboard/generate"', script)
        self.assertIn('/static/panel-detector.js?v=', html)
        self.assertIn('/static/storyboard-ui.js?v=', html)

        styles = (ROOT / "static" / "styles.css").read_text(encoding="utf-8")
        self.assertIn(".output-head { align-items: flex-start;", styles)
        self.assertIn(".toast {", styles)

        vision_markup = html[html.index('id="vision-section"'):html.index('</section>', html.index('id="vision-section"'))]
        left_pane = vision_markup[vision_markup.index('class="vision-input-pane"'):vision_markup.index('class="vision-output-pane"')]
        right_pane = vision_markup[vision_markup.index('class="vision-output-pane"'):]
        self.assertIn('id="vision-heading"', left_pane)
        self.assertIn('class="section-heading compact-heading vision-output-heading"', right_pane)
        self.assertIn(".vision-output-heading {", styles)

    def test_frontend_recovers_from_stale_client_state_and_uses_a_versioned_script(self):
        html = (ROOT / "static" / "index.html").read_text(encoding="utf-8")
        script = (ROOT / "static" / "app.js").read_text(encoding="utf-8")

        self.assertIn('/static/app.js?v=', html)
        self.assertIn('/static/styles.css?v=', html)
        self.assertIn('/static/mobile.css?v=', html)
        self.assertIn('Object.prototype.hasOwnProperty.call(I18N, storedLanguage)', script)

    def test_frontend_restores_model_status_after_progress_monitor_stops(self):
        script = (ROOT / "static" / "app.js").read_text(encoding="utf-8")

        cleanup = script[script.index("return async () => {"):script.index("function setWorking")]
        self.assertIn("await updateModelStatus();", cleanup)
        self.assertIn("await updateVisionStatus();", cleanup)
        self.assertEqual(1, script.count("await stopProgress();"))

    def test_resource_monitor_is_a_separate_top_strip(self):
        html = (ROOT / "static" / "index.html").read_text(encoding="utf-8")
        script = (ROOT / "static" / "app.js").read_text(encoding="utf-8")
        styles = (ROOT / "static" / "styles.css").read_text(encoding="utf-8")

        self.assertLess(html.index('id="resource-monitor"'), html.index('class="topbar"'))
        for metric_id in ("resource-cpu", "resource-ram", "resource-ram-detail", "resource-disk", "resource-gpu", "resource-vram", "resource-vram-detail"):
            self.assertIn(f'id="{metric_id}"', html)
        self.assertIn('fetch("/api/resources")', script)
        self.assertIn('setInterval(updateResourceMonitor, 2000)', script)
        self.assertIn('.resource-strip {', styles)
        self.assertIn('grid-template-columns: repeat(5, minmax(0, 1fr))', styles)

    def test_one_click_entrypoints_and_readme_exist(self):
        self.assertTrue((ROOT / "install-and-run.bat").is_file())
        self.assertTrue((ROOT / "run.bat").is_file())
        launcher = (ROOT / "run.bat").read_text(encoding="utf-8")
        self.assertIn("PYTHONNOUSERSITE=1", launcher)
        self.assertIn('if exist "local-settings.bat" call "local-settings.bat"', launcher)
        self.assertIn("FAITHFUL_H3_LLAMA_BIN", launcher)
        self.assertIn('scripts\\run_server.py', launcher)
        self.assertNotIn('-m uvicorn app.main:app', launcher)
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
