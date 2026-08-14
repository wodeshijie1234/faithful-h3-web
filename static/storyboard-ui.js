(function (root, factory) {
  const api = factory(root.FaithfulStoryboard, root.FaithfulPanelDetector);
  if (typeof module === "object" && module.exports) module.exports = api;
  if (root) root.FaithfulStoryboardUI = api;
})(typeof globalThis !== "undefined" ? globalThis : this, function (storyboard, panelDetector) {
  function create(options) {
    const byId = id => document.getElementById(id);
    const t = options.t;
    let state = emptyState();
    let draggingIndex = null;
    let modelReady = false;
    let modelDownloading = false;

    function emptyState() {
      return {
        imageDataUrl: "", imageName: "", taskType: "comic_panels", goal: "", language: "en",
        modelId: "accurate", panelBoxes: [], result: emptyResult(),
      };
    }

    function emptyResult() {
      return {title: "", synopsis: "", characters: [], shots: [], sound_design: "", viral_hook: "", ending: "", total_duration_seconds: 0};
    }

    function notifyDraft() {
      readInspector();
      options.onDraft();
    }

    function payload() {
      readInspector();
      state.result.shots = storyboard.recalculateShotTimes(state.result.shots);
      state.result.total_duration_seconds = storyboard.totalDuration(state.result.shots);
      return structuredClone(state);
    }

    function apply(payload = {}) {
      state = {
        ...emptyState(), ...payload,
        result: {...emptyResult(), ...(payload.result || payload.output || {})},
      };
      state.result.shots = storyboard.recalculateShotTimes(state.result.shots);
      byId("storyboard-goal").value = state.goal || "";
      byId("storyboard-language").value = state.language || "en";
      byId("storyboard-model").value = state.modelId || "accurate";
      document.querySelectorAll("[data-story-task]").forEach(button => {
        const active = button.dataset.storyTask === state.taskType;
        button.classList.toggle("active", active);
        button.setAttribute("aria-selected", String(active));
      });
      const preview = byId("storyboard-preview");
      preview.src = state.imageDataUrl || "";
      byId("storyboard-preview-wrap").hidden = !state.imageDataUrl;
      byId("storyboard-dropzone").classList.toggle("has-preview", Boolean(state.imageDataUrl));
      syncInspector();
      renderPanelOverlay();
      renderShots();
      updateActions();
    }

    function readInspector() {
      state.goal = byId("storyboard-goal").value;
      state.language = byId("storyboard-language").value;
      state.modelId = byId("storyboard-model").value;
      state.result.title = byId("storyboard-title").value;
      state.result.synopsis = byId("storyboard-synopsis").value;
      state.result.characters = byId("storyboard-characters").value.split(/\r?\n/).map(item => item.trim()).filter(Boolean);
      state.result.viral_hook = byId("storyboard-hook").value;
      state.result.sound_design = byId("storyboard-sound").value;
      state.result.ending = byId("storyboard-ending").value;
      updateJson();
    }

    function syncInspector() {
      byId("storyboard-title").value = state.result.title || "";
      byId("storyboard-synopsis").value = state.result.synopsis || "";
      byId("storyboard-characters").value = (state.result.characters || []).join("\n");
      byId("storyboard-hook").value = state.result.viral_hook || "";
      byId("storyboard-sound").value = state.result.sound_design || "";
      byId("storyboard-ending").value = state.result.ending || "";
      updateJson();
    }

    function updateJson() {
      const result = {...state.result, shots: storyboard.recalculateShotTimes(state.result.shots)};
      result.total_duration_seconds = storyboard.totalDuration(result.shots);
      byId("storyboard-json").value = JSON.stringify(result, null, 2);
    }

    function formatTime(seconds) {
      const minutes = Math.floor(seconds / 60);
      const remainder = seconds - minutes * 60;
      return `${String(minutes).padStart(2, "0")}:${remainder.toFixed(1).padStart(4, "0")}`;
    }

    function renderShots() {
      state.result.shots = storyboard.recalculateShotTimes(state.result.shots);
      const list = byId("storyboard-shot-list");
      list.replaceChildren();
      state.result.shots.forEach((shot, index) => list.append(createShotRow(shot, index)));
      byId("storyboard-empty-shots").hidden = state.result.shots.length > 0;
      byId("storyboard-shot-count").textContent = state.result.shots.length;
      const total = storyboard.totalDuration(state.result.shots);
      state.result.total_duration_seconds = total;
      byId("storyboard-total-duration").textContent = formatTime(total);
      updateJson();
    }

    function createShotRow(shot, index) {
      const row = document.createElement("article");
      row.className = "storyboard-shot-row";
      row.draggable = true;
      row.dataset.index = index;
      row.addEventListener("dragstart", () => { draggingIndex = index; row.classList.add("dragging"); });
      row.addEventListener("dragend", () => { draggingIndex = null; row.classList.remove("dragging"); });
      row.addEventListener("dragover", event => { event.preventDefault(); row.classList.add("drag-over"); });
      row.addEventListener("dragleave", () => row.classList.remove("drag-over"));
      row.addEventListener("drop", event => {
        event.preventDefault(); row.classList.remove("drag-over");
        if (draggingIndex === null || draggingIndex === index) return;
        const [moved] = state.result.shots.splice(draggingIndex, 1);
        state.result.shots.splice(index, 0, moved);
        renderShots(); notifyDraft();
      });

      const drag = element("span", "shot-drag", "⋮⋮"); drag.title = t("dragReorder");
      const number = element("strong", "shot-number", String(index + 1));
      const start = element("time", "shot-start", formatTime(shot.start_seconds));
      const duration = document.createElement("input");
      duration.className = "shot-duration"; duration.type = "number"; duration.min = "0.5"; duration.max = "15"; duration.step = "0.5"; duration.value = shot.duration_seconds;
      duration.setAttribute("aria-label", t("duration"));
      duration.addEventListener("change", () => { shot.duration_seconds = Number(duration.value); renderShots(); notifyDraft(); });

      const details = document.createElement("div"); details.className = "shot-details";
      const selectors = document.createElement("div"); selectors.className = "shot-selectors";
      selectors.append(
        makeSelect(shot, "panel_index", panelOptions(), value => value ? Number(value) : null, t("panel")),
        makeSelect(shot, "shot_size", ["Wide shot", "Medium shot", "Close-up", "Extreme close-up", "Low angle", "High angle"], String, t("shotSize")),
        makeSelect(shot, "camera_movement", ["Static", "Push in", "Pull out", "Pan", "Tilt", "Tracking", "Handheld"], String, t("cameraMovement")),
      );
      const action = makeTextarea(shot, "visual_action", t("visualAction"), 2);
      const secondary = document.createElement("div"); secondary.className = "shot-secondary";
      secondary.append(
        makeTextarea(shot, "dialogue", t("dialogue"), 2),
        makeTextarea(shot, "sound", t("sound"), 2),
        makeInput(shot, "transition", t("transition")),
      );
      details.append(selectors, action, secondary);
      const remove = document.createElement("button"); remove.type = "button"; remove.className = "icon-button shot-remove"; remove.textContent = "×"; remove.title = t("delete");
      remove.addEventListener("click", () => { state.result.shots.splice(index, 1); renderShots(); notifyDraft(); });
      row.append(drag, number, start, duration, details, remove);
      return row;
    }

    function panelOptions() {
      const count = Math.max(state.panelBoxes.length, ...state.result.shots.map(shot => Number(shot.panel_index) || 0));
      return [{value: "", label: t("none")}, ...Array.from({length: count}, (_, index) => ({value: String(index + 1), label: `${t("panel")} ${index + 1}`}))];
    }

    function makeSelect(target, key, values, coerce, label) {
      const select = document.createElement("select"); select.setAttribute("aria-label", label);
      values.forEach(item => {
        const value = typeof item === "object" ? item.value : item;
        const option = document.createElement("option"); option.value = value; option.textContent = typeof item === "object" ? item.label : item;
        select.append(option);
      });
      select.value = target[key] == null ? "" : String(target[key]);
      select.addEventListener("change", () => { target[key] = coerce(select.value); notifyDraft(); });
      return select;
    }

    function makeTextarea(target, key, placeholder, rows) {
      const input = document.createElement("textarea"); input.rows = rows; input.placeholder = placeholder; input.value = target[key] || "";
      input.addEventListener("input", () => { target[key] = input.value; notifyDraft(); });
      return input;
    }

    function makeInput(target, key, placeholder) {
      const input = document.createElement("input"); input.type = "text"; input.placeholder = placeholder; input.value = target[key] || "";
      input.addEventListener("input", () => { target[key] = input.value; notifyDraft(); });
      return input;
    }

    function element(tag, className, text) {
      const node = document.createElement(tag); node.className = className; node.textContent = text; return node;
    }

    async function detectPanels() {
      if (!state.imageDataUrl) throw new Error(t("selectImage"));
      const image = byId("storyboard-preview");
      if (!image.complete) await new Promise((resolve, reject) => { image.onload = resolve; image.onerror = reject; });
      state.panelBoxes = await panelDetector.detectPanelBoxes(image);
      if (!state.panelBoxes.length) state.panelBoxes = [{x: 0, y: 0, width: 1, height: 1}];
      if (!state.result.shots.length) {
        state.result.shots = state.panelBoxes.map((_, index) => ({
          panel_index: index + 1, duration_seconds: 2.5, shot_size: "Medium shot", camera_movement: "Static",
          visual_action: "", dialogue: "", sound: "", transition: "Cut",
        }));
      }
      renderPanelOverlay(); renderShots(); notifyDraft();
      return state.panelBoxes;
    }

    function renderPanelOverlay() {
      const layer = byId("storyboard-panel-layer"); layer.replaceChildren();
      (state.panelBoxes || []).forEach((box, index) => {
        const marker = element("span", "panel-marker", String(index + 1));
        marker.style.left = `${box.x * 100}%`; marker.style.top = `${box.y * 100}%`;
        marker.style.width = `${box.width * 100}%`; marker.style.height = `${box.height * 100}%`;
        layer.append(marker);
      });
      byId("storyboard-panel-count").textContent = state.panelBoxes.length;
    }

    function loadFile(file) {
      const allowed = ["image/png", "image/jpeg", "image/webp"];
      if (!file || !allowed.includes(file.type) || file.size < 1 || file.size > 12 * 1024 * 1024) throw new Error(t("invalidImage"));
      const reader = new FileReader();
      reader.addEventListener("load", () => {
        state.imageDataUrl = String(reader.result || ""); state.imageName = file.name || ""; state.panelBoxes = [];
        byId("storyboard-preview").src = state.imageDataUrl;
        byId("storyboard-preview-wrap").hidden = false;
        byId("storyboard-dropzone").classList.add("has-preview");
        renderPanelOverlay(); updateActions(); notifyDraft();
        options.setStatus(t("visionSelected"));
      });
      reader.addEventListener("error", () => options.setStatus(t("invalidImage"), "error"));
      reader.readAsDataURL(file);
    }

    function applyGenerated(result) {
      state.result = {...emptyResult(), ...(result || {})};
      state.result.shots = storyboard.recalculateShotTimes(state.result.shots);
      syncInspector(); renderShots(); notifyDraft();
    }

    function addShot() {
      state.result.shots.push({panel_index: null, duration_seconds: 3, shot_size: "Medium shot", camera_movement: "Static", visual_action: "", dialogue: "", sound: "", transition: "Cut"});
      renderShots(); notifyDraft();
    }

    function updateActions() {
      const enabled = Boolean(state.imageDataUrl);
      byId("storyboard-detect").disabled = !enabled;
      byId("storyboard-generate").disabled = !enabled || !modelReady || modelDownloading;
    }

    function setBusy(busy) {
      byId("storyboard-detect").disabled = busy || !state.imageDataUrl;
      byId("storyboard-generate").disabled = busy || !state.imageDataUrl || !modelReady || modelDownloading;
    }

    function setModelAvailability(ready, downloading) {
      modelReady = ready;
      modelDownloading = downloading;
      updateActions();
    }

    function init() {
      byId("storyboard-file").addEventListener("change", event => { try { loadFile(event.target.files[0]); } catch (error) { options.setStatus(error.message, "error"); } });
      const dropzone = byId("storyboard-dropzone");
      dropzone.addEventListener("dragover", event => { event.preventDefault(); dropzone.classList.add("drag-over"); });
      dropzone.addEventListener("dragleave", () => dropzone.classList.remove("drag-over"));
      dropzone.addEventListener("drop", event => { event.preventDefault(); dropzone.classList.remove("drag-over"); try { loadFile(event.dataTransfer.files[0]); } catch (error) { options.setStatus(error.message, "error"); } });
      document.querySelectorAll("[data-story-task]").forEach(button => button.addEventListener("click", () => {
        state.taskType = button.dataset.storyTask;
        document.querySelectorAll("[data-story-task]").forEach(item => { const active = item === button; item.classList.toggle("active", active); item.setAttribute("aria-selected", String(active)); });
        notifyDraft();
      }));
      byId("storyboard-add-shot").addEventListener("click", addShot);
      byId("storyboard-detect").addEventListener("click", async () => {
        setBusy(true); options.setStatus(t("analyzingPanels"), "loading");
        try { const boxes = await detectPanels(); options.setStatus(`${t("detectedPanels")}: ${boxes.length}`); }
        catch (error) { options.setStatus(error.message, "error"); }
        finally { setBusy(false); }
      });
      ["storyboard-goal", "storyboard-language", "storyboard-model", "storyboard-title", "storyboard-synopsis", "storyboard-characters", "storyboard-hook", "storyboard-sound", "storyboard-ending"].forEach(id => byId(id).addEventListener("input", notifyDraft));
      apply(state);
    }

    init();
    return {payload, apply, applyGenerated, detectPanels, setBusy, setModelAvailability, updateActions, outputText: () => byId("storyboard-json").value};
  }

  return {create};
});
