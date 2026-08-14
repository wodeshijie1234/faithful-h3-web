const I18N = {
  en: {
    language: "Language", mode: "Mode", sourceArea: "Prompt sources", sourcePrompt: "Source prompt",
    sourcePlaceholder: "Enter the original facts, shots, positions, actions, and dialogue to preserve.",
    simplePrompt: "Simple prompt", simplePlaceholder: "Enter a short prompt in any language.", creativeStrength: "Creative strength",
    enrichButton: "Enrich prompt", enrichedOutput: "Enriched prompt", moduleEditor: "H3 module editor",
    subjects: "Subject definitions", summary: "Summary", retention: "Retention analysis", scene: "Scene & continuity",
    scenePlaceholder: "Only facts that apply across shots.", shots: "Shot", duration: "Duration", startsAt: "Starts at",
    totalDuration: "Total duration", action: "Action & dialogue", camera: "Camera", soundscape: "Overall soundscape",
    soundPlaceholder: "Leave empty to infer supported sounds from actions and dialogue.", music: "Non-diegetic music",
    musicPlaceholder: "Leave empty for N/A or supported inference.", h3Output: "H3 output", convertButton: "Convert / update H3", directConvert: "Convert directly to H3",
    download: "Download model", releaseMemory: "Release memory", releasingMemory: "Releasing...",
    memoryReleased: "Memory and VRAM released", memoryAlreadyFree: "No loaded model to release", downloading: "Downloading model...",
    modelMissing: "Model not downloaded", modelReady: "Model ready", modelLoading: "Model loaded", working: "Working...",
    runtimeDone: "{backend} · {seconds}s",
    importDone: "Modules filled. Review them before conversion.", enrichDone: "Enrichment complete", convertDone: "H3 and editing modules updated", directConvertDone: "H3 generated from the source prompt",
    enterPrompt: "Enter a prompt first.", noModuleContent: "Fill or import at least one visual module first.", requestFailed: "Request failed", copied: "Copied",
    help: {
      model: ["Local model", "The model runs locally on the NVIDIA GPU."],
      release: ["Release memory", "Unloads this tool's model and clears its Python and CUDA caches."],
      mode: ["H3 mode", "FL2VA and Ref2VA expose their official module structures. The tool never inspects images."],
      sources: ["Prompt sources", "Import either the original prompt or the enriched result. Importing only distributes existing content into modules; it does not translate or expand it."],
      enrich: ["Prompt enrichment", "This is the only creative workflow. Its strength never affects faithful H3 conversion."],
      modules: ["H3 module editor", "This is the shared editing surface before and after conversion. Each shot defaults to 3 seconds. Change duration in 0.5-second steps; start times and total duration are calculated automatically."],
      output: ["Faithful English H3", "Visual values are translated literally and reviewed for invented details. Empty audio fields may be inferred from supported actions and dialogue."]
    }
  },
  "zh-CN": {
    language: "语言", mode: "模式", sourceArea: "提示词来源", sourcePrompt: "原始提示词",
    sourcePlaceholder: "输入必须保留的人物、镜头、站位、动作和对白。", simplePrompt: "简单提示词",
    simplePlaceholder: "输入任意语言的简短提示词。", creativeStrength: "创作强度", enrichButton: "丰富提示词",
    enrichedOutput: "丰富结果", moduleEditor: "H3 模块编辑器", subjects: "主体定义", summary: "摘要", retention: "保留分析",
    scene: "场景与连续性", scenePlaceholder: "只填写跨镜头持续成立的事实。", shots: "镜头", duration: "持续时长",
    startsAt: "起始时间", totalDuration: "总时长", action: "动作与对白", camera: "镜头机位", soundscape: "整体声音环境",
    soundPlaceholder: "留空时可根据动作和对白推断合理声音。", music: "非叙事音乐", musicPlaceholder: "留空时默认为 N/A 或根据原意推断。",
    h3Output: "H3 输出", convertButton: "转换 / 更新 H3", download: "下载模型", releaseMemory: "释放内存显存",
    releasingMemory: "正在释放...", memoryReleased: "已释放内存和显存", memoryAlreadyFree: "当前没有已加载模型",
    downloading: "正在下载模型...", modelMissing: "模型未下载", modelReady: "模型已就绪", modelLoading: "模型已加载",
    working: "处理中...", importDone: "模块已填充，请检查后再转换。", enrichDone: "提示词丰富完成",
    convertDone: "H3 与微调模块均已更新", enterPrompt: "请先输入提示词。", noModuleContent: "请先填写或导入至少一个视觉模块。",
    requestFailed: "请求失败", copied: "已复制",
    help: {
      model: ["本地模型", "模型在本机 NVIDIA GPU 上运行。"],
      release: ["释放内存显存", "卸载本工具模型并清理 Python 与 CUDA 缓存。"],
      mode: ["H3 模式", "FL2VA 与 Ref2VA 分别显示对应官方模块；工具不识别图片。"],
      sources: ["提示词来源", "原始提示词和丰富结果都可导入。导入只把现有文字分配到模块，不翻译、不扩写。"],
      enrich: ["提示词丰富", "这是唯一允许创作扩写的功能，创作强度不会影响忠实转换。"],
      modules: ["H3 模块编辑器", "转换前后共用这一套微调模块。每个镜头默认 3 秒，以 0.5 秒为步长调整；起始时间和总时长会自动计算。"],
      output: ["忠实英文 H3", "视觉内容只忠实翻译，并审查是否新增细节；空声音字段允许根据动作与对白推断。"]
    }
  },
  "zh-TW": {
    language: "語言", mode: "模式", sourceArea: "提示詞來源", sourcePrompt: "原始提示詞",
    sourcePlaceholder: "輸入必須保留的人物、鏡頭、站位、動作和對白。", simplePrompt: "簡單提示詞",
    simplePlaceholder: "輸入任意語言的簡短提示詞。", creativeStrength: "創作強度", enrichButton: "豐富提示詞",
    enrichedOutput: "豐富結果", moduleEditor: "H3 模組編輯器", subjects: "主體定義", summary: "摘要", retention: "保留分析",
    scene: "場景與連續性", scenePlaceholder: "只填寫跨鏡頭持續成立的事實。", shots: "鏡頭", duration: "持續時長",
    startsAt: "起始時間", totalDuration: "總時長", action: "動作與對白", camera: "鏡頭機位", soundscape: "整體聲音環境",
    soundPlaceholder: "留空時可根據動作和對白推斷合理聲音。", music: "非敘事音樂", musicPlaceholder: "留空時預設為 N/A 或根據原意推斷。",
    h3Output: "H3 輸出", convertButton: "轉換 / 更新 H3", download: "下載模型", releaseMemory: "釋放記憶體顯存",
    releasingMemory: "正在釋放...", memoryReleased: "已釋放記憶體和顯存", memoryAlreadyFree: "目前沒有已載入模型",
    downloading: "正在下載模型...", modelMissing: "模型未下載", modelReady: "模型已就緒", modelLoading: "模型已載入",
    working: "處理中...", importDone: "模組已填入，請檢查後再轉換。", enrichDone: "提示詞豐富完成",
    convertDone: "H3 與微調模組均已更新", enterPrompt: "請先輸入提示詞。", noModuleContent: "請先填寫或匯入至少一個視覺模組。",
    requestFailed: "請求失敗", copied: "已複製",
    help: {
      model: ["本機模型", "模型在本機 NVIDIA GPU 上執行。"],
      release: ["釋放記憶體顯存", "卸載本工具模型並清理 Python 與 CUDA 快取。"],
      mode: ["H3 模式", "FL2VA 與 Ref2VA 分別顯示對應官方模組；工具不辨識圖片。"],
      sources: ["提示詞來源", "原始提示詞和豐富結果都可匯入。匯入只把現有文字分配到模組，不翻譯、不擴寫。"],
      enrich: ["提示詞豐富", "這是唯一允許創作擴寫的功能，創作強度不會影響忠實轉換。"],
      modules: ["H3 模組編輯器", "轉換前後共用這套微調模組。每個鏡頭預設 3 秒，以 0.5 秒為步長調整；起始時間和總時長會自動計算。"],
      output: ["忠實英文 H3", "視覺內容只忠實翻譯，並審查是否新增細節；空聲音欄位允許根據動作與對白推斷。"]
    }
  }
};

Object.assign(I18N.en, {
  visionTitle: "Image to prompt", optional: "Optional", chooseImage: "Choose an image",
  imageLimits: "PNG, JPEG or WebP, up to 12 MB", visionInstruction: "Focus or description requirement",
  visionInstructionPlaceholder: "Optional. For example: focus on subject positions and camera angle.",
  downloadVision: "Download vision model", analyzeImage: "Analyze image", visionOutput: "Reconstructed prompt",
  visionOutputPlaceholder: "The literal image description will appear here.", visionMissing: "Vision model not downloaded",
  visionReady: "Vision model ready", visionLoaded: "Vision model loaded", visionDownloading: "Downloading vision model...",
  visionSelected: "Image selected", visionDone: "Image analysis complete", visionToSource: "Placed in source prompt",
  invalidImage: "Choose a PNG, JPEG, or WebP image up to 12 MB.", selectImage: "Choose an image first.",
  emptyVisionOutput: "Analyze an image first."
});
I18N.en.help.vision = ["Image to prompt", "Uses a separate 2B abliterated vision model to describe only visible image facts. The result stays independent until you place it in the source prompt."];
I18N.en.help.mode = ["H3 mode", "FL2VA and Ref2VA expose their official module structures. H3 conversion is text-only; optional image analysis stays in its separate module."];

Object.assign(I18N["zh-CN"], {
  directConvert: "\u76f4\u63a5\u8f6c\u4e3a H3",
  directConvertDone: "\u5df2\u6839\u636e\u539f\u59cb\u63d0\u793a\u8bcd\u751f\u6210 H3",
  visionTitle: "\u8bc6\u56fe\u53cd\u63a8\u63d0\u793a\u8bcd", optional: "\u53ef\u9009", chooseImage: "\u9009\u62e9\u56fe\u7247",
  imageLimits: "PNG\u3001JPEG \u6216 WebP\uff0c\u6700\u5927 12 MB", visionInstruction: "\u5173\u6ce8\u70b9\u6216\u63cf\u8ff0\u8981\u6c42",
  visionInstructionPlaceholder: "\u53ef\u9009\uff0c\u4f8b\u5982\uff1a\u91cd\u70b9\u63cf\u8ff0\u4eba\u7269\u7ad9\u4f4d\u548c\u955c\u5934\u89d2\u5ea6\u3002",
  downloadVision: "\u4e0b\u8f7d\u8bc6\u56fe\u6a21\u578b", analyzeImage: "\u5206\u6790\u56fe\u7247", visionOutput: "\u53cd\u63a8\u63d0\u793a\u8bcd",
  visionOutputPlaceholder: "\u5fe0\u5b9e\u7684\u56fe\u7247\u63cf\u8ff0\u5c06\u663e\u793a\u5728\u8fd9\u91cc\u3002", visionMissing: "\u8bc6\u56fe\u6a21\u578b\u672a\u4e0b\u8f7d",
  visionReady: "\u8bc6\u56fe\u6a21\u578b\u5df2\u5c31\u7eea", visionLoaded: "\u8bc6\u56fe\u6a21\u578b\u5df2\u52a0\u8f7d", visionDownloading: "\u6b63\u5728\u4e0b\u8f7d\u8bc6\u56fe\u6a21\u578b...",
  visionSelected: "\u56fe\u7247\u5df2\u9009\u62e9", visionDone: "\u56fe\u7247\u5206\u6790\u5b8c\u6210", visionToSource: "\u5df2\u586b\u5165\u539f\u59cb\u63d0\u793a\u8bcd",
  invalidImage: "\u8bf7\u9009\u62e9 12 MB \u4ee5\u5185\u7684 PNG\u3001JPEG \u6216 WebP \u56fe\u7247\u3002", selectImage: "\u8bf7\u5148\u9009\u62e9\u56fe\u7247\u3002",
  emptyVisionOutput: "\u8bf7\u5148\u5206\u6790\u56fe\u7247\u3002"
});
I18N["zh-CN"].help.vision = ["\u8bc6\u56fe\u53cd\u63a8", "\u4f7f\u7528\u72ec\u7acb\u7684 2B \u65e0\u9650\u5236\u89c6\u89c9\u6a21\u578b\uff0c\u53ea\u63cf\u8ff0\u56fe\u7247\u4e2d\u771f\u5b9e\u53ef\u89c1\u7684\u4e8b\u5b9e\u3002\u7ed3\u679c\u5728\u4f60\u4e3b\u52a8\u586b\u5165\u539f\u59cb\u63d0\u793a\u8bcd\u524d\u4e0e H3 \u6d41\u7a0b\u72ec\u7acb\u3002"];
I18N["zh-CN"].help.mode = ["H3 \u6a21\u5f0f", "FL2VA \u548c Ref2VA \u5206\u522b\u663e\u793a\u5bf9\u5e94\u7684\u5b98\u65b9\u6a21\u5757\u3002H3 \u8f6c\u6362\u4ecd\u4e3a\u7eaf\u6587\u672c\u6d41\u7a0b\uff1b\u53ef\u9009\u8bc6\u56fe\u4fdd\u6301\u5728\u72ec\u7acb\u6a21\u5757\u4e2d\u3002"];
Object.assign(I18N["zh-TW"], {
  directConvert: "\u76f4\u63a5\u8f49\u70ba H3",
  directConvertDone: "\u5df2\u6839\u64da\u539f\u59cb\u63d0\u793a\u8a5e\u751f\u6210 H3",
  visionTitle: "\u8b58\u5716\u53cd\u63a8\u63d0\u793a\u8a5e", optional: "\u53ef\u9078", chooseImage: "\u9078\u64c7\u5716\u7247",
  imageLimits: "PNG\u3001JPEG \u6216 WebP\uff0c\u6700\u5927 12 MB", visionInstruction: "\u95dc\u6ce8\u9ede\u6216\u63cf\u8ff0\u8981\u6c42",
  visionInstructionPlaceholder: "\u53ef\u9078\uff0c\u4f8b\u5982\uff1a\u91cd\u9ede\u63cf\u8ff0\u4eba\u7269\u7ad9\u4f4d\u548c\u93e1\u982d\u89d2\u5ea6\u3002",
  downloadVision: "\u4e0b\u8f09\u8b58\u5716\u6a21\u578b", analyzeImage: "\u5206\u6790\u5716\u7247", visionOutput: "\u53cd\u63a8\u63d0\u793a\u8a5e",
  visionOutputPlaceholder: "\u5fe0\u5be6\u7684\u5716\u7247\u63cf\u8ff0\u5c07\u986f\u793a\u5728\u9019\u88e1\u3002", visionMissing: "\u8b58\u5716\u6a21\u578b\u672a\u4e0b\u8f09",
  visionReady: "\u8b58\u5716\u6a21\u578b\u5df2\u5c31\u7dd2", visionLoaded: "\u8b58\u5716\u6a21\u578b\u5df2\u8f09\u5165", visionDownloading: "\u6b63\u5728\u4e0b\u8f09\u8b58\u5716\u6a21\u578b...",
  visionSelected: "\u5716\u7247\u5df2\u9078\u64c7", visionDone: "\u5716\u7247\u5206\u6790\u5b8c\u6210", visionToSource: "\u5df2\u586b\u5165\u539f\u59cb\u63d0\u793a\u8a5e",
  invalidImage: "\u8acb\u9078\u64c7 12 MB \u4ee5\u5167\u7684 PNG\u3001JPEG \u6216 WebP \u5716\u7247\u3002", selectImage: "\u8acb\u5148\u9078\u64c7\u5716\u7247\u3002",
  emptyVisionOutput: "\u8acb\u5148\u5206\u6790\u5716\u7247\u3002"
});
I18N["zh-TW"].help.vision = ["\u8b58\u5716\u53cd\u63a8", "\u4f7f\u7528\u7368\u7acb\u7684 2B \u7121\u9650\u5236\u8996\u89ba\u6a21\u578b\uff0c\u53ea\u63cf\u8ff0\u5716\u7247\u4e2d\u771f\u5be6\u53ef\u898b\u7684\u4e8b\u5be6\u3002\u7d50\u679c\u5728\u4f60\u4e3b\u52d5\u586b\u5165\u539f\u59cb\u63d0\u793a\u8a5e\u524d\u8207 H3 \u6d41\u7a0b\u7368\u7acb\u3002"];
I18N["zh-TW"].help.mode = ["H3 \u6a21\u5f0f", "FL2VA \u548c Ref2VA \u5206\u5225\u986f\u793a\u5c0d\u61c9\u7684\u5b98\u65b9\u6a21\u7d44\u3002H3 \u8f49\u63db\u4ecd\u70ba\u7d14\u6587\u5b57\u6d41\u7a0b\uff1b\u53ef\u9078\u8b58\u5716\u4fdd\u6301\u5728\u7368\u7acb\u6a21\u7d44\u4e2d\u3002"];

const storedLanguage = localStorage.getItem("faithful-h3-language");
let language = Object.prototype.hasOwnProperty.call(I18N, storedLanguage) ? storedLanguage : "en";
let mode = "fl2va";
let shotCount = 3;
let busyCount = 0;
let statusTimer = null;
let visionStatusTimer = null;
let visionImageDataUrl = "";
const $ = id => document.getElementById(id);
const t = key => I18N[language][key] || I18N.en[key] || key;

function setStatus(id, message, type = "") {
  const el = $(id);
  el.textContent = message;
  el.className = `feedback ${type}`;
}

function runtimeMessage(data, fallback) {
  if (!data.runtime) return fallback;
  return `${fallback} · ${data.runtime.model.toUpperCase()} ${data.runtime.backend.toUpperCase()} · ${data.runtime.elapsed_seconds}s`;
}

function setWorking(button, working) {
  button.disabled = working;
  button.setAttribute("aria-busy", String(working));
  busyCount = Math.max(0, busyCount + (working ? 1 : -1));
  $("release-memory").disabled = busyCount > 0;
}

async function api(action, text = "", extra = {}) {
  const response = await fetch("/api/generate", {
    method: "POST",
    headers: {"Content-Type": "application/json"},
    body: JSON.stringify({action, mode, text, strength: Number($("strength").value), ...extra})
  });
  const data = await response.json();
  if (!response.ok) throw new Error(data.detail || t("requestFailed"));
  return data;
}

function escapeHtml(value) {
  return String(value).replace(/[&<>"']/g, char => ({"&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;"}[char]));
}

function normalizeDuration(value) {
  const numeric = Number.parseFloat(value);
  const safe = Number.isFinite(numeric) ? numeric : 3;
  return Math.round(Math.min(30, Math.max(0.5, safe)) * 2) / 2;
}

function formatTime(seconds) {
  const totalMs = Math.round(seconds * 1000);
  const minutes = Math.floor(totalMs / 60000);
  const remainder = totalMs % 60000;
  const wholeSeconds = Math.floor(remainder / 1000);
  const milliseconds = remainder % 1000;
  return `${String(minutes).padStart(2, "0")}:${String(wholeSeconds).padStart(2, "0")}.${String(milliseconds).padStart(3, "0")}`;
}

function shotTemplate(index, data = {}) {
  const duration = normalizeDuration(data.duration_seconds ?? 3);
  const removeDisabled = shotCount <= 1 ? "disabled" : "";
  return `<article class="shot-module" data-shot="${index}">
    <div class="shot-heading">
      <div class="shot-title"><span class="drag-handle" draggable="true" title="Drag to reorder" aria-hidden="true">&#8645;</span><strong>${t("shots")} ${index + 1}</strong></div>
      <div class="shot-timing">
        <span class="shot-start"><span>${t("startsAt")}</span><output class="shot-start-value">00:00.000</output></span>
        <label class="duration-control"><span>${t("duration")}</span><span class="duration-input"><input class="shot-duration" type="number" min="0.5" max="30" step="0.5" value="${duration.toFixed(1)}"><span>s</span></span></label>
        <button class="icon-button shot-remove" type="button" title="Remove shot" aria-label="Remove shot" ${removeDisabled}>&#8722;</button>
      </div>
    </div>
    <div class="shot-fields">
      <label><span>${t("action")}</span><textarea class="shot-action" rows="3">${escapeHtml(data.action || "")}</textarea></label>
      <label><span>${t("camera")}</span><textarea class="shot-camera" rows="3">${escapeHtml(data.camera || "")}</textarea></label>
    </div>
  </article>`;
}

function recalculateTimeline() {
  let elapsed = 0;
  document.querySelectorAll(".shot-module").forEach(shot => {
    shot.querySelector(".shot-start-value").textContent = formatTime(elapsed);
    elapsed += normalizeDuration(shot.querySelector(".shot-duration").value);
  });
  $("total-duration").textContent = `${elapsed.toFixed(1)}s`;
}

function renderShots(data = []) {
  shotCount = Math.max(1, data.length || shotCount);
  $("shots-list").innerHTML = Array.from({length: shotCount}, (_, index) => shotTemplate(index, data[index] || {})).join("");
  $("shot-count").textContent = String(shotCount);
  recalculateTimeline();
}

function collectModules() {
  const modules = {
    scene: $("scene").value.trim(),
    shots: [...document.querySelectorAll(".shot-module")].map(el => ({
      duration_seconds: normalizeDuration(el.querySelector(".shot-duration").value),
      action: el.querySelector(".shot-action").value.trim(),
      camera: el.querySelector(".shot-camera").value.trim()
    })),
    overall_soundscape: $("overall-soundscape").value.trim(),
    non_diegetic_music: $("non-diegetic-music").value.trim()
  };
  if (mode === "ref2va") Object.assign(modules, {
    subject_definitions: $("subject-definitions").value.trim(),
    summary: $("summary").value.trim(),
    retention_analysis: $("retention-analysis").value.trim()
  });
  return modules;
}

function fillModules(modules) {
  $("scene").value = modules.scene || "";
  $("overall-soundscape").value = modules.overall_soundscape || "";
  $("non-diegetic-music").value = modules.non_diegetic_music || "";
  if (mode === "ref2va") {
    $("subject-definitions").value = modules.subject_definitions || "";
    $("summary").value = modules.summary || "";
    $("retention-analysis").value = modules.retention_analysis || "";
  }
  renderShots(modules.shots?.length ? modules.shots : [{}, {}, {}]);
}

function hasVisualContent(modules) {
  return Boolean(modules.scene || modules.subject_definitions || modules.summary || modules.retention_analysis || modules.shots.some(shot => shot.action || shot.camera));
}

function applyLanguage() {
  const currentShots = collectModules().shots;
  document.documentElement.lang = language;
  document.querySelectorAll("[data-i18n]").forEach(el => el.textContent = t(el.dataset.i18n));
  document.querySelectorAll("[data-i18n-placeholder]").forEach(el => el.placeholder = t(el.dataset.i18nPlaceholder));
  $("download-model").textContent = t("download");
  $("release-memory").textContent = t("releaseMemory");
  $("language").value = language;
  renderShots(currentShots);
  updateModelStatus();
  updateVisionStatus();
}

function loadVisionFile(file) {
  const allowed = ["image/png", "image/jpeg", "image/webp"];
  if (!file || !allowed.includes(file.type) || file.size < 1 || file.size > 12 * 1024 * 1024) {
    return setStatus("vision-status", t("invalidImage"), "error");
  }
  const reader = new FileReader();
  reader.addEventListener("load", () => {
    visionImageDataUrl = String(reader.result || "");
    $("vision-preview").src = visionImageDataUrl;
    $("vision-preview").hidden = false;
    $("vision-dropzone").classList.add("has-preview");
    setStatus("vision-status", t("visionSelected"));
    updateVisionStatus();
  });
  reader.addEventListener("error", () => setStatus("vision-status", t("invalidImage"), "error"));
  reader.readAsDataURL(file);
}

async function updateVisionStatus() {
  try {
    const data = await fetch("/api/vision/status").then(response => response.json());
    const message = data.downloading ? t("visionDownloading") : data.loaded ? t("visionLoaded") : data.ready ? t("visionReady") : t("visionMissing");
    setStatus("vision-status", data.error || message, data.error ? "error" : data.downloading ? "loading" : "");
    $("vision-download").disabled = data.downloading || data.ready;
    $("vision-analyze").disabled = data.downloading || !data.ready || !visionImageDataUrl;
    if (data.downloading && !visionStatusTimer) visionStatusTimer = setInterval(updateVisionStatus, 2000);
    if (!data.downloading && visionStatusTimer) {
      clearInterval(visionStatusTimer);
      visionStatusTimer = null;
    }
  } catch (error) {
    setStatus("vision-status", error.message, "error");
  }
}

async function importToModules(text, statusId, button) {
  if (!text.trim()) return setStatus(statusId, t("enterPrompt"), "error");
  setStatus(statusId, t("working"), "loading");
  setWorking(button, true);
  try {
    const data = await api("decompose", text);
    fillModules(data.modules);
    setStatus(statusId, runtimeMessage(data, t("importDone")));
    $("module-heading").scrollIntoView({behavior: "smooth", block: "start"});
  } catch (error) {
    setStatus(statusId, error.message, "error");
  } finally {
    setWorking(button, false);
  }
}

document.querySelectorAll(".segment").forEach(button => button.addEventListener("click", () => {
  mode = button.dataset.mode;
  document.querySelectorAll(".segment").forEach(item => {
    const active = item === button;
    item.classList.toggle("active", active);
    item.setAttribute("aria-selected", String(active));
  });
  $("ref-modules").hidden = mode !== "ref2va";
}));

$("strength").addEventListener("input", event => $("strength-value").value = event.target.value);
$("shots-list").addEventListener("input", event => {
  if (event.target.classList.contains("shot-duration")) recalculateTimeline();
});
$("shots-list").addEventListener("change", event => {
  if (!event.target.classList.contains("shot-duration")) return;
  event.target.value = normalizeDuration(event.target.value).toFixed(1);
  recalculateTimeline();
});
$("add-shot").addEventListener("click", () => {
  const data = collectModules().shots;
  data.push({duration_seconds: 3});
  renderShots(data);
});
$("shots-list").addEventListener("click", event => {
  const remove = event.target.closest(".shot-remove");
  if (!remove || shotCount <= 1) return;
  const shot = remove.closest(".shot-module");
  const data = collectModules().shots;
  data.splice(Number(shot.dataset.shot), 1);
  renderShots(data);
});

let draggedShotIndex = null;
$("shots-list").addEventListener("dragstart", event => {
  const handle = event.target.closest(".drag-handle");
  if (!handle) return;
  const shot = handle.closest(".shot-module");
  draggedShotIndex = Number(shot.dataset.shot);
  shot.classList.add("shot-dragging");
  event.dataTransfer.effectAllowed = "move";
  event.dataTransfer.setData("text/plain", String(draggedShotIndex));
});
$("shots-list").addEventListener("dragover", event => {
  const shot = event.target.closest(".shot-module");
  if (!shot || draggedShotIndex === null) return;
  event.preventDefault();
  document.querySelectorAll(".shot-module.drag-over").forEach(item => item.classList.remove("drag-over"));
  shot.classList.add("drag-over");
});
$("shots-list").addEventListener("drop", event => {
  const target = event.target.closest(".shot-module");
  if (!target || draggedShotIndex === null) return;
  event.preventDefault();
  const targetIndex = Number(target.dataset.shot);
  const data = collectModules().shots;
  const [moved] = data.splice(draggedShotIndex, 1);
  const insertionIndex = draggedShotIndex < targetIndex ? targetIndex - 1 : targetIndex;
  data.splice(insertionIndex, 0, moved);
  draggedShotIndex = null;
  renderShots(data);
});
$("shots-list").addEventListener("dragend", () => {
  draggedShotIndex = null;
  document.querySelectorAll(".shot-module.shot-dragging, .shot-module.drag-over").forEach(item => item.classList.remove("shot-dragging", "drag-over"));
});
$("import-source").addEventListener("click", () => importToModules($("source-input").value, "source-status", $("import-source")));
$("import-enriched").addEventListener("click", () => importToModules($("enrich-output").value, "enrich-status", $("import-enriched")));

$("convert-source").addEventListener("click", async () => {
  const text = $("source-input").value.trim();
  if (!text) return setStatus("source-status", t("enterPrompt"), "error");
  setStatus("source-status", t("working"), "loading");
  setWorking($("convert-source"), true);
  try {
    const data = await api("convert", text);
    $("h3-output").value = data.output;
    setStatus("source-status", runtimeMessage(data, t("directConvertDone")));
    $("result-heading").scrollIntoView({behavior: "smooth", block: "start"});
  } catch (error) {
    setStatus("source-status", error.message, "error");
  } finally {
    setWorking($("convert-source"), false);
  }
});

$("enrich").addEventListener("click", async () => {
  const text = $("enrich-input").value.trim();
  if (!text) return setStatus("enrich-status", t("enterPrompt"), "error");
  setStatus("enrich-status", t("working"), "loading");
  setWorking($("enrich"), true);
  try {
    const data = await api("enrich", text);
    $("enrich-output").value = data.output;
    setStatus("enrich-status", runtimeMessage(data, t("enrichDone")));
  } catch (error) {
    setStatus("enrich-status", error.message, "error");
  } finally {
    setWorking($("enrich"), false);
  }
});

$("convert-modules").addEventListener("click", async () => {
  const modules = collectModules();
  if (!hasVisualContent(modules)) return setStatus("convert-status", t("noModuleContent"), "error");
  setStatus("convert-status", t("working"), "loading");
  setWorking($("convert-modules"), true);
  try {
    const data = await api("convert_modules", "modules", {modules});
    $("h3-output").value = data.output;
    fillModules(data.modules);
    setStatus("convert-status", runtimeMessage(data, t("convertDone")));
  } catch (error) {
    setStatus("convert-status", error.message, "error");
  } finally {
    setWorking($("convert-modules"), false);
  }
});

$("vision-file").addEventListener("change", event => loadVisionFile(event.target.files[0]));
$("vision-dropzone").addEventListener("dragover", event => {
  event.preventDefault();
  $("vision-dropzone").classList.add("drag-over");
});
$("vision-dropzone").addEventListener("dragleave", () => $("vision-dropzone").classList.remove("drag-over"));
$("vision-dropzone").addEventListener("drop", event => {
  event.preventDefault();
  $("vision-dropzone").classList.remove("drag-over");
  loadVisionFile(event.dataTransfer.files[0]);
});
$("vision-download").addEventListener("click", async () => {
  try {
    const response = await fetch("/api/vision/download", {method: "POST"});
    const data = await response.json();
    if (!response.ok) throw new Error(data.detail || t("requestFailed"));
    updateVisionStatus();
  } catch (error) {
    setStatus("vision-status", error.message, "error");
  }
});
$("vision-analyze").addEventListener("click", async () => {
  if (!visionImageDataUrl) return setStatus("vision-status", t("selectImage"), "error");
  setStatus("vision-status", t("working"), "loading");
  setWorking($("vision-analyze"), true);
  try {
    const response = await fetch("/api/vision/caption", {
      method: "POST",
      headers: {"Content-Type": "application/json"},
      body: JSON.stringify({
        image_data_url: visionImageDataUrl,
        instruction: $("vision-instruction").value.trim(),
        language,
      }),
    });
    const data = await response.json();
    if (!response.ok) throw new Error(data.detail || t("requestFailed"));
    $("vision-output").value = data.output;
    setStatus("vision-status", runtimeMessage(data, t("visionDone")));
  } catch (error) {
    setStatus("vision-status", error.message, "error");
  } finally {
    setWorking($("vision-analyze"), false);
  }
});
$("vision-to-source").addEventListener("click", () => {
  const text = $("vision-output").value.trim();
  if (!text) return setStatus("vision-status", t("emptyVisionOutput"), "error");
  $("source-input").value = text;
  setStatus("vision-status", t("visionToSource"));
  $("source-heading").scrollIntoView({behavior: "smooth", block: "start"});
  $("source-input").focus();
});

document.querySelectorAll(".copy").forEach(button => button.addEventListener("click", async () => {
  await navigator.clipboard.writeText($(button.dataset.target).value);
  const old = button.title;
  button.title = t("copied");
  setTimeout(() => button.title = old, 1200);
}));
document.querySelectorAll(".download").forEach(button => button.addEventListener("click", () => {
  const blob = new Blob([$(button.dataset.target).value], {type: "text/plain;charset=utf-8"});
  const anchor = document.createElement("a");
  anchor.href = URL.createObjectURL(blob);
  anchor.download = "faithful-h3-prompt.txt";
  anchor.click();
  URL.revokeObjectURL(anchor.href);
}));

$("language").addEventListener("change", event => {
  language = event.target.value;
  localStorage.setItem("faithful-h3-language", language);
  applyLanguage();
});

async function updateModelStatus() {
  try {
    const data = await fetch("/api/status").then(response => response.json());
    const el = $("model-status");
    $("model-select").value = data.selected_model;
    const backend = data.backend ? ` · ${data.backend.toUpperCase()}` : "";
    el.textContent = (data.downloading ? t("downloading") : data.loaded ? t("modelLoading") : data.ready ? t("modelReady") : t("modelMissing")) + backend;
    el.className = `status ${data.error ? "status-error" : data.ready ? "status-ready" : "status-neutral"}`;
    if (data.error) el.textContent = data.error;
    $("download-model").disabled = data.downloading || data.ready;
    if (data.downloading && !statusTimer) statusTimer = setInterval(updateModelStatus, 2000);
    if (!data.downloading && statusTimer) {
      clearInterval(statusTimer);
      statusTimer = null;
    }
  } catch (error) {
    $("model-status").textContent = error.message;
    $("model-status").className = "status status-error";
  }
}

$("model-select").addEventListener("change", async event => {
  try {
    const response = await fetch("/api/model", {
      method: "POST",
      headers: {"Content-Type": "application/json"},
      body: JSON.stringify({model_id: event.target.value}),
    });
    const data = await response.json();
    if (!response.ok) throw new Error(data.detail || "Model selection failed");
    await updateModelStatus();
  } catch (error) {
    $("model-status").textContent = error.message;
    $("model-status").className = "status status-error";
  }
});

$("download-model").addEventListener("click", async () => {
  await fetch("/api/download", {method: "POST"});
  updateModelStatus();
});
$("release-memory").addEventListener("click", async () => {
  const button = $("release-memory");
  const old = t("releaseMemory");
  button.disabled = true;
  button.textContent = t("releasingMemory");
  try {
    const response = await fetch("/api/release", {method: "POST"});
    const data = await response.json();
    if (!response.ok) throw new Error(data.detail || t("requestFailed"));
    $("model-status").textContent = data.released ? t("memoryReleased") : t("memoryAlreadyFree");
  } catch (error) {
    $("model-status").textContent = error.message;
  } finally {
    button.textContent = old;
    button.disabled = busyCount > 0;
  }
});

document.querySelectorAll(".help").forEach(button => button.addEventListener("click", () => {
  const item = I18N[language].help[button.dataset.help];
  $("help-title").textContent = item[0];
  $("help-body").textContent = item[1];
  $("help-dialog").showModal();
}));
$("help-close").addEventListener("click", () => $("help-dialog").close());

renderShots([{duration_seconds: 3}, {duration_seconds: 3}, {duration_seconds: 3}]);
applyLanguage();
