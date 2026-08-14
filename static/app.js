const I18N = {
  en: {
    language: "Language", mode: "Mode", sourceArea: "Prompt sources", sourcePrompt: "Source prompt",
    sourcePlaceholder: "Enter the original facts, shots, positions, actions, and dialogue to preserve.",
    simplePrompt: "Simple prompt", simplePlaceholder: "Enter a short prompt in any language.", creativeStrength: "Creative strength",
    enrichButton: "Enrich prompt", enrichedOutput: "Enriched prompt",
    subjects: "Subject definitions", summary: "Summary", retention: "Retention analysis", scene: "Scene & continuity",
    scenePlaceholder: "Only facts that apply across shots.", shots: "Shot", duration: "Duration", startsAt: "Starts at",
    totalDuration: "Total duration", action: "Action & dialogue", camera: "Camera", soundscape: "Overall soundscape",
    soundPlaceholder: "Leave empty to infer supported sounds from actions and dialogue.", music: "Non-diegetic music",
    musicPlaceholder: "Leave empty for N/A or supported inference.", h3Output: "H3 output", convertButton: "Convert / update H3", directConvert: "Convert directly to H3",
    download: "Download models", releaseMemory: "Release memory", releasingMemory: "Releasing...",
    memoryReleased: "Memory and VRAM released", memoryAlreadyFree: "No loaded model to release", downloading: "Downloading model...",
    modelMissing: "Model not downloaded", modelReady: "Model ready", modelLoading: "Model loaded", loadingModel: "Loading model...", loadingVisionModel: "Loading vision model...", working: "Working...",
    memoryReleasedPrefix: "Released", memoryCurrent: "now", ramLabel: "RAM", vramLabel: "VRAM",
    runtimeDone: "{backend} · {seconds}s",
    enrichDone: "Enrichment complete", directConvertDone: "H3 generated from the source prompt",
    enterPrompt: "Enter a prompt first.", requestFailed: "Request failed", copied: "Copied",
    help: {
      model: ["Local model", "The model runs locally on the NVIDIA GPU."],
      release: ["Release memory", "Unloads this tool's model and clears its Python and CUDA caches."],
      mode: ["H3 mode", "Choose FL2VA or Ref2VA. The tool never inspects images during H3 conversion."],
      sources: ["Prompt sources", "Use the original prompt for faithful conversion, or enrich a short prompt first and place the result into the source field."],
      enrich: ["Prompt enrichment", "This is the only creative workflow. Its strength never affects faithful H3 conversion."],
      output: ["Faithful English H3", "Visual values are translated literally and reviewed for invented details. Empty audio fields may be inferred from supported actions and dialogue."]
    }
  },
  "zh-CN": {
    language: "语言", mode: "模式", sourceArea: "提示词来源", sourcePrompt: "原始提示词",
    sourcePlaceholder: "输入必须保留的人物、镜头、站位、动作和对白。", simplePrompt: "简单提示词",
    simplePlaceholder: "输入任意语言的简短提示词。", creativeStrength: "创作强度", enrichButton: "丰富提示词",
    enrichedOutput: "丰富结果",
    scene: "场景与连续性", scenePlaceholder: "只填写跨镜头持续成立的事实。", shots: "镜头", duration: "持续时长",
    startsAt: "起始时间", totalDuration: "总时长", action: "动作与对白", camera: "镜头机位", soundscape: "整体声音环境",
    soundPlaceholder: "留空时可根据动作和对白推断合理声音。", music: "非叙事音乐", musicPlaceholder: "留空时默认为 N/A 或根据原意推断。",
    h3Output: "H3 输出", convertButton: "转换 / 更新 H3", download: "下载模型", releaseMemory: "释放内存显存",
    releasingMemory: "正在释放...", memoryReleased: "已释放内存和显存", memoryAlreadyFree: "当前没有已加载模型",
    downloading: "正在下载模型...", modelMissing: "模型未下载", modelReady: "模型已就绪", modelLoading: "模型已加载", loadingModel: "正在加载模型", loadingVisionModel: "正在加载识图模型",
    memoryReleasedPrefix: "已释放", memoryCurrent: "当前", ramLabel: "内存", vramLabel: "显存",
    working: "处理中...", importDone: "模块已填充，请检查后再转换。", enrichDone: "提示词丰富完成",
    enterPrompt: "请先输入提示词。",
    requestFailed: "请求失败", copied: "已复制",
    help: {
      model: ["本地模型", "模型在本机 NVIDIA GPU 上运行。"],
      release: ["释放内存显存", "卸载本工具模型并清理 Python 与 CUDA 缓存。"],
      mode: ["H3 模式", "FL2VA 与 Ref2VA 分别显示对应官方模块；工具不识别图片。"],
      sources: ["提示词来源", "原始提示词和丰富结果都可导入。导入只把现有文字分配到模块，不翻译、不扩写。"],
      enrich: ["提示词丰富", "这是唯一允许创作扩写的功能，创作强度不会影响忠实转换。"],
      output: ["忠实英文 H3", "视觉内容只忠实翻译，并审查是否新增细节；空声音字段允许根据动作与对白推断。"]
    }
  },
  "zh-TW": {
    language: "語言", mode: "模式", sourceArea: "提示詞來源", sourcePrompt: "原始提示詞",
    sourcePlaceholder: "輸入必須保留的人物、鏡頭、站位、動作和對白。", simplePrompt: "簡單提示詞",
    simplePlaceholder: "輸入任意語言的簡短提示詞。", creativeStrength: "創作強度", enrichButton: "豐富提示詞",
    enrichedOutput: "豐富結果",
    scene: "場景與連續性", scenePlaceholder: "只填寫跨鏡頭持續成立的事實。", shots: "鏡頭", duration: "持續時長",
    startsAt: "起始時間", totalDuration: "總時長", action: "動作與對白", camera: "鏡頭機位", soundscape: "整體聲音環境",
    soundPlaceholder: "留空時可根據動作和對白推斷合理聲音。", music: "非敘事音樂", musicPlaceholder: "留空時預設為 N/A 或根據原意推斷。",
    h3Output: "H3 輸出", convertButton: "轉換 / 更新 H3", download: "下載模型", releaseMemory: "釋放記憶體顯存",
    releasingMemory: "正在釋放...", memoryReleased: "已釋放記憶體和顯存", memoryAlreadyFree: "目前沒有已載入模型",
    downloading: "正在下載模型...", modelMissing: "模型未下載", modelReady: "模型已就緒", modelLoading: "模型已載入", loadingModel: "正在載入模型", loadingVisionModel: "正在載入識圖模型",
    memoryReleasedPrefix: "已釋放", memoryCurrent: "目前", ramLabel: "記憶體", vramLabel: "顯存",
    working: "處理中...", importDone: "模組已填入，請檢查後再轉換。", enrichDone: "提示詞豐富完成",
    enterPrompt: "請先輸入提示詞。",
    requestFailed: "請求失敗", copied: "已複製",
    help: {
      model: ["本機模型", "模型在本機 NVIDIA GPU 上執行。"],
      release: ["釋放記憶體顯存", "卸載本工具模型並清理 Python 與 CUDA 快取。"],
      mode: ["H3 模式", "FL2VA 與 Ref2VA 分別顯示對應官方模組；工具不辨識圖片。"],
      sources: ["提示詞來源", "原始提示詞和豐富結果都可匯入。匯入只把現有文字分配到模組，不翻譯、不擴寫。"],
      enrich: ["提示詞豐富", "這是唯一允許創作擴寫的功能，創作強度不會影響忠實轉換。"],
      output: ["忠實英文 H3", "視覺內容只忠實翻譯，並審查是否新增細節；空聲音欄位允許根據動作與對白推斷。"]
    }
  }
};

Object.assign(I18N.en, {
  h3View: "H3", enrichView: "Prompt enrichment", visionView: "Image to prompt", enrichTitle: "Prompt enrichment",
  chooseDownloads: "Choose models to download", downloadHint: "Select only the models you need. Downloads continue in the background and progress is printed in the startup console.",
  visionModelOption: "Image-to-prompt model", cancel: "Cancel", downloadSelected: "Download selected", selectDownload: "Select at least one model.",
  readyLabel: "Ready", downloadingLabel: "Downloading", notDownloadedLabel: "Not downloaded",
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
I18N.en.help.mode = ["H3 mode", "Choose FL2VA or Ref2VA. H3 conversion is text-only; optional image analysis stays in its separate view."];

Object.assign(I18N["zh-CN"], {
  h3View: "H3", enrichView: "丰富提示词", visionView: "图片反推", enrichTitle: "丰富提示词",
  chooseDownloads: "选择要下载的模型", downloadHint: "只勾选需要的模型。下载将在后台继续，详细进度显示在启动日志黑窗中。",
  visionModelOption: "图片反推模型", cancel: "取消", downloadSelected: "下载所选模型", selectDownload: "请至少选择一个模型。",
  readyLabel: "已就绪", downloadingLabel: "下载中", notDownloadedLabel: "未下载",
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
  h3View: "H3", enrichView: "豐富提示詞", visionView: "圖片反推", enrichTitle: "豐富提示詞",
  chooseDownloads: "選擇要下載的模型", downloadHint: "只勾選需要的模型。下載將在背景繼續，詳細進度顯示在啟動日誌視窗中。",
  visionModelOption: "圖片反推模型", cancel: "取消", downloadSelected: "下載所選模型", selectDownload: "請至少選擇一個模型。",
  readyLabel: "已就緒", downloadingLabel: "下載中", notDownloadedLabel: "未下載",
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
let busyCount = 0;
let statusTimer = null;
let visionStatusTimer = null;
let progressTimer = null;
let toastTimer = null;
let visionImageDataUrl = "";
let currentView = "h3";
const $ = id => document.getElementById(id);
const t = key => I18N[language][key] || I18N.en[key] || key;

function setView(requestedView, updateHash = true) {
  const view = ["h3", "enrich", "vision"].includes(requestedView) ? requestedView : "h3";
  currentView = view;
  document.querySelectorAll(".view-tab").forEach(button => {
    const active = button.dataset.view === view;
    button.classList.toggle("active", active);
    button.setAttribute("aria-selected", String(active));
  });
  $("h3-view").hidden = view !== "h3";
  $("enrich-view").hidden = view !== "enrich";
  $("vision-view").hidden = view !== "vision";
  document.querySelectorAll("[data-h3-control]").forEach(control => control.hidden = view === "vision");
  if (view === "vision") updateVisionStatus();
  else updateModelStatus();
  const hash = `#${view}`;
  if (updateHash && location.hash !== hash) history.replaceState(null, "", hash);
}

function setStatus(id, message, type = "") {
  const el = $(id);
  el.textContent = message;
  el.className = `feedback ${type}`;
}

function runtimeMessage(data, fallback) {
  if (!data.runtime) return fallback;
  const speed = Number(data.runtime.tokens_per_second || 0);
  const speedText = speed > 0 ? " · " + speed.toFixed(1) + " token/s" : "";
  return fallback + " · " + data.runtime.model.toUpperCase() + " " + data.runtime.backend.toUpperCase() + " · " + data.runtime.elapsed_seconds + "s" + speedText;
}

function setTopStatus(message, state = "neutral") {
  const el = $("model-status");
  el.textContent = message;
  el.className = `status status-${state}`;
}

function showToast(message, type = "") {
  const toast = $("release-toast");
  toast.textContent = message;
  toast.className = `toast ${type}`.trim();
  toast.hidden = false;
  if (toastTimer) clearTimeout(toastTimer);
  toastTimer = setTimeout(() => {
    toast.hidden = true;
    toastTimer = null;
  }, 7000);
}

function formatMib(value) {
  return (Number(value || 0) / 1024).toFixed(1) + " GB";
}

function formatReleaseSummary(data) {
  const parts = [];
  const memory = data.memory || {};
  [["vram", "vramLabel"], ["ram", "ramLabel"]].forEach(([key, labelKey]) => {
    const metric = memory[key];
    if (!metric) return;
    parts.push(`${t(labelKey)} ${formatMib(metric.released_mib)}, ${t("memoryCurrent")} ${formatMib(metric.used_mib)} / ${formatMib(metric.total_mib)}`);
  });
  const prefix = data.released ? t("memoryReleasedPrefix") : t("memoryAlreadyFree");
  return parts.length ? `${prefix}：${parts.join("；")}` : prefix;
}

function formatResourcePercent(value) {
  return Number.isFinite(Number(value)) ? Number(value).toFixed(1) + "%" : "--";
}

function formatResourceMemory(metric) {
  if (!metric) return {percent: "--", detail: "-- / -- GB"};
  return {
    percent: formatResourcePercent(metric.percent),
    detail: `${Number(metric.used_gib).toFixed(1)} / ${Number(metric.total_gib).toFixed(1)} GB`,
  };
}

async function updateResourceMonitor() {
  const monitor = $("resource-monitor");
  try {
    const response = await fetch("/api/resources");
    if (!response.ok) throw new Error("Resource monitor unavailable");
    const data = await response.json();
    const ram = formatResourceMemory(data.ram);
    const vram = formatResourceMemory(data.vram);
    $("resource-cpu").textContent = formatResourcePercent(data.cpu_percent);
    $("resource-ram").textContent = ram.percent;
    $("resource-ram-detail").textContent = ram.detail;
    $("resource-disk").textContent = data.disk
      ? `${Number(data.disk.read_mb_s).toFixed(1)} / ${Number(data.disk.write_mb_s).toFixed(1)} MB/s`
      : "-- / -- MB/s";
    $("resource-gpu").textContent = formatResourcePercent(data.gpu_percent);
    $("resource-vram").textContent = vram.percent;
    $("resource-vram-detail").textContent = vram.detail;
    monitor.classList.toggle("resource-unavailable", !data.available);
  } catch (error) {
    monitor.classList.add("resource-unavailable");
  }
}

function startProgressMonitor(statusId) {
  const loadingText = currentView === "vision" ? t("loadingVisionModel") : t("loadingModel");
  setStatus(statusId, loadingText, "loading");
  setTopStatus(loadingText, "neutral");
  const update = async () => {
    try {
      const data = await fetch("/api/progress").then(response => response.json());
      if (!data.active) return;
      if (data.phase === "loading") {
        const message = data.task === "vision" ? t("loadingVisionModel") : t("loadingModel");
        setStatus(statusId, message, "loading");
        setTopStatus(message, "neutral");
        return;
      }
      const elapsed = Number(data.elapsed_seconds || 0).toFixed(1);
      const speed = Number(data.tokens_per_second || 0).toFixed(1);
      setStatus(statusId, t("working") + " · " + elapsed + "s · " + speed + " token/s", "loading");
      setTopStatus(data.task === "vision" ? t("visionLoaded") : t("modelLoading"), "ready");
    } catch (error) {
      // The final request response remains authoritative if polling briefly fails.
    }
  };
  if (progressTimer) clearInterval(progressTimer);
  update();
  progressTimer = setInterval(update, 500);
  return async () => {
    if (progressTimer) clearInterval(progressTimer);
    progressTimer = null;
    if (currentView === "vision") await updateVisionStatus();
    else await updateModelStatus();
  };
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

function applyLanguage() {
  document.documentElement.lang = language;
  document.querySelectorAll("[data-i18n]").forEach(el => el.textContent = t(el.dataset.i18n));
  document.querySelectorAll("[data-i18n-placeholder]").forEach(el => el.placeholder = t(el.dataset.i18nPlaceholder));
  $("download-model").textContent = t("download");
  $("release-memory").textContent = t("releaseMemory");
  $("language").value = language;
  updateModelStatus();
  updateVisionStatus();
}

function updateDownloadOptions(data) {
  const states = Object.fromEntries(data.models.map(item => [item.id, item]));
  states.vision = {
    ready: data.vision_ready,
    downloading: data.vision_downloading,
    error: data.vision_error,
  };
  document.querySelectorAll('#download-dialog input[type="checkbox"]').forEach(input => {
    const state = states[input.value];
    input.checked = false;
    input.disabled = state.ready || state.downloading;
    const status = $("download-status-" + input.value);
    status.textContent = state.error || (state.ready ? t("readyLabel") : state.downloading ? t("downloadingLabel") : t("notDownloadedLabel"));
    status.classList.toggle("error", Boolean(state.error));
  });
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
    if (currentView === "vision") setTopStatus(data.error || message, data.error ? "error" : data.ready ? "ready" : "neutral");
    $("vision-analyze").disabled = data.downloading || !data.ready || !visionImageDataUrl;
    if (data.downloading && !visionStatusTimer) visionStatusTimer = setInterval(updateVisionStatus, 2000);
    if (!data.downloading && visionStatusTimer) {
      clearInterval(visionStatusTimer);
      visionStatusTimer = null;
    }
  } catch (error) {
    if (currentView === "vision") setTopStatus(error.message, "error");
  }
}

document.querySelectorAll(".segment").forEach(button => button.addEventListener("click", () => {
  mode = button.dataset.mode;
  document.querySelectorAll(".segment").forEach(item => {
    const active = item === button;
    item.classList.toggle("active", active);
    item.setAttribute("aria-selected", String(active));
  });
}));

document.querySelectorAll(".view-tab").forEach(button => button.addEventListener("click", () => {
  setView(button.dataset.view);
  window.scrollTo({top: 0, behavior: "smooth"});
}));
window.addEventListener("hashchange", () => setView(location.hash.slice(1), false));

$("strength").addEventListener("input", event => $("strength-value").value = event.target.value);
$("use-enriched").addEventListener("click", () => {
  const text = $("enrich-output").value.trim();
  if (!text) return setStatus("enrich-status", t("enterPrompt"), "error");
  $("source-input").value = text;
  setView("h3");
  $("source-heading").scrollIntoView({behavior: "smooth", block: "start"});
  $("source-input").focus();
});

$("convert-source").addEventListener("click", async () => {
  const text = $("source-input").value.trim();
  if (!text) return setStatus("source-status", t("enterPrompt"), "error");
  setStatus("source-status", t("working"), "loading");
  setWorking($("convert-source"), true);
  const stopProgress = startProgressMonitor("source-status");
  try {
    const data = await api("convert", text);
    $("h3-output").value = data.output;
    setStatus("source-status", runtimeMessage(data, t("directConvertDone")));
    $("result-heading").scrollIntoView({behavior: "smooth", block: "start"});
  } catch (error) {
    setStatus("source-status", error.message, "error");
  } finally {
    await stopProgress();
    setWorking($("convert-source"), false);
  }
});

$("enrich").addEventListener("click", async () => {
  const text = $("enrich-input").value.trim();
  if (!text) return setStatus("enrich-status", t("enterPrompt"), "error");
  setStatus("enrich-status", t("working"), "loading");
  setWorking($("enrich"), true);
  const stopProgress = startProgressMonitor("enrich-status");
  try {
    const data = await api("enrich", text);
    $("enrich-output").value = data.output;
    setStatus("enrich-status", runtimeMessage(data, t("enrichDone")));
  } catch (error) {
    setStatus("enrich-status", error.message, "error");
  } finally {
    await stopProgress();
    setWorking($("enrich"), false);
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
$("vision-analyze").addEventListener("click", async () => {
  if (!visionImageDataUrl) return setStatus("vision-status", t("selectImage"), "error");
  setStatus("vision-status", t("working"), "loading");
  setWorking($("vision-analyze"), true);
  const stopProgress = startProgressMonitor("vision-status");
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
    await stopProgress();
    setWorking($("vision-analyze"), false);
  }
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
    if (currentView !== "vision") {
      el.textContent = (data.downloading ? t("downloading") : data.loaded ? t("modelLoading") : data.ready ? t("modelReady") : t("modelMissing")) + backend;
      el.className = `status ${data.error ? "status-error" : data.ready ? "status-ready" : "status-neutral"}`;
      if (data.error) el.textContent = data.error;
    }
    const allReady = data.models.every(item => item.ready) && data.vision_ready;
    $("download-model").disabled = allReady;
    if (data.any_downloading && !statusTimer) statusTimer = setInterval(() => {
      updateModelStatus();
      updateVisionStatus();
    }, 2000);
    if (!data.any_downloading && statusTimer) {
      clearInterval(statusTimer);
      statusTimer = null;
    }
    return data;
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
  try {
    const data = await updateModelStatus();
    updateDownloadOptions(data);
    setStatus("download-feedback", "");
    $("download-dialog").showModal();
  } catch (error) {
    $("model-status").textContent = error.message;
  }
});
$("download-close").addEventListener("click", () => $("download-dialog").close());
$("download-cancel").addEventListener("click", () => $("download-dialog").close());
$("download-confirm").addEventListener("click", async () => {
  const models = [...document.querySelectorAll('#download-dialog input[type="checkbox"]:checked')].map(input => input.value);
  if (!models.length) return setStatus("download-feedback", t("selectDownload"), "error");
  const button = $("download-confirm");
  button.disabled = true;
  try {
    const response = await fetch("/api/download", {
      method: "POST",
      headers: {"Content-Type": "application/json"},
      body: JSON.stringify({models}),
    });
    const data = await response.json();
    if (!response.ok) throw new Error(data.detail || t("requestFailed"));
    $("download-dialog").close();
    updateModelStatus();
    updateVisionStatus();
  } catch (error) {
    setStatus("download-feedback", error.message, "error");
  } finally {
    button.disabled = false;
  }
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
    setTopStatus(data.released ? t("memoryReleased") : t("memoryAlreadyFree"), "ready");
    showToast(formatReleaseSummary(data));
  } catch (error) {
    setTopStatus(error.message, "error");
    showToast(error.message, "error");
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

setView(location.hash.slice(1));
applyLanguage();
updateResourceMonitor();
setInterval(updateResourceMonitor, 2000);
