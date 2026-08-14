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

Object.assign(I18N.en, {
  draftSaved: "Draft saved", addToQueue: "Add to queue", runQueue: "Run queue", queue: "Queue", history: "History",
  queueTitle: "Queue", historyTitle: "History", selectAll: "Select all", deleteSelected: "Delete selected", delete: "Delete",
  restore: "Restore", emptyQueue: "The queue is empty.", emptyHistory: "No history yet.", queued: "Added to queue", queueRunning: "Queue is running...",
  queueComplete: "Queue complete", imageFile: "Image", failed: "Failed", dragReorder: "Drag to reorder"
});
Object.assign(I18N["zh-CN"], {
  draftSaved: "草稿已暂存", addToQueue: "加入队列", runQueue: "运行队列", queue: "队列", history: "历史记录",
  queueTitle: "队列", historyTitle: "历史记录", selectAll: "全选", deleteSelected: "删除所选", delete: "删除", restore: "恢复",
  emptyQueue: "队列为空。", emptyHistory: "暂无历史记录。", queued: "已加入队列", queueRunning: "队列运行中…", queueComplete: "队列完成", imageFile: "图片", failed: "失败", dragReorder: "拖拽排序"
});
Object.assign(I18N["zh-TW"], {
  draftSaved: "草稿已暫存", addToQueue: "加入佇列", runQueue: "執行佇列", queue: "佇列", history: "歷史記錄",
  queueTitle: "佇列", historyTitle: "歷史記錄", selectAll: "全選", deleteSelected: "刪除所選", delete: "刪除", restore: "還原",
  emptyQueue: "佇列為空。", emptyHistory: "暫無歷史記錄。", queued: "已加入佇列", queueRunning: "佇列執行中…", queueComplete: "佇列完成", imageFile: "圖片", failed: "失敗", dragReorder: "拖曳排序"
});

Object.assign(I18N.en, {
  storyboardView: "Storyboard workspace", storySource: "Source", uploadStoryboardImage: "Upload comic page or image",
  storyTaskType: "Task type", comicPanels: "Comic panels", viralVideo: "Viral video", creativeGoal: "Creative goal",
  storyGoalPlaceholder: "Describe pacing, audience, platform, or constraints.", outputLanguage: "Output language",
  detectedPanels: "Detected panels", shotTimeline: "Shot timeline", addShot: "Add shot", shotNumber: "Shot",
  startTime: "Start", shotDetails: "Shot details", noShots: "No shots yet", analyzeToBegin: "Analyze panels or add a shot to begin.",
  totalShots: "Total shots", storyDetails: "Story details", storyTitle: "Title", synopsis: "Synopsis",
  characters: "Characters", charactersPlaceholder: "One character per line", viralHook: "Opening hook",
  soundDesign: "Sound design", ending: "Ending", structuredOutput: "Structured output", visionModel: "Vision model",
  fastVisionModel: "Fast 2B", accurateVisionModel: "Accurate 8B", analyzePanels: "Analyze panels",
  generateStoryboard: "Generate storyboard", analyzingPanels: "Analyzing panels...", storyboardDone: "Storyboard generated",
  panel: "Panel", none: "None", shotSize: "Shot size", cameraMovement: "Camera movement", visualAction: "Visual action",
  dialogue: "Dialogue", sound: "Sound", transition: "Transition", visionFastOption: "Fast vision model (2B)",
  visionAccurateOption: "Accurate vision model (8B)"
});
I18N.en.help.storyboard = ["Storyboard workspace", "Detects comic panels locally, then uses the selected vision model to build an editable shot timeline. Comic mode preserves visible panel evidence; viral-video mode may create a story around the source-image identity anchor."];

Object.assign(I18N["zh-CN"], {
  storyboardView: "分镜工作台", storySource: "素材", uploadStoryboardImage: "上传漫画分镜图或单张图片",
  storyTaskType: "任务类型", comicPanels: "漫画分镜", viralVideo: "爆款视频", creativeGoal: "创作目标",
  storyGoalPlaceholder: "填写节奏、受众、平台或必须遵守的约束。", outputLanguage: "输出语言",
  detectedPanels: "检测到的分格", shotTimeline: "镜头时间线", addShot: "新增镜头", shotNumber: "镜头",
  startTime: "起始", shotDetails: "镜头内容", noShots: "暂无镜头", analyzeToBegin: "分析分格或手动新增镜头后开始编辑。",
  totalShots: "镜头总数", storyDetails: "故事与结构化输出", storyTitle: "标题", synopsis: "梗概",
  characters: "角色", charactersPlaceholder: "每行一个角色", viralHook: "开场钩子",
  soundDesign: "声音设计", ending: "结尾", structuredOutput: "结构化输出", visionModel: "识图模型",
  fastVisionModel: "快速 2B", accurateVisionModel: "准确 8B", analyzePanels: "分析分格",
  generateStoryboard: "生成分镜", analyzingPanels: "正在分析分格…", storyboardDone: "分镜已生成",
  panel: "分格", none: "无", shotSize: "景别", cameraMovement: "运镜", visualAction: "画面动作",
  dialogue: "对白", sound: "声音", transition: "转场", visionFastOption: "快速识图模型（2B）",
  visionAccurateOption: "准确识图模型（8B）"
});
I18N["zh-CN"].help.storyboard = ["分镜工作台", "先在本地检测漫画分格，再由所选视觉模型生成可编辑镜头时间线。漫画模式忠于画面证据；爆款视频模式可围绕原图人物和视觉锚点创作剧情。"];

Object.assign(I18N["zh-TW"], {
  storyboardView: "分鏡工作台", storySource: "素材", uploadStoryboardImage: "上傳漫畫分鏡圖或單張圖片",
  storyTaskType: "任務類型", comicPanels: "漫畫分鏡", viralVideo: "爆款影片", creativeGoal: "創作目標",
  storyGoalPlaceholder: "填寫節奏、受眾、平台或必須遵守的約束。", outputLanguage: "輸出語言",
  detectedPanels: "偵測到的分格", shotTimeline: "鏡頭時間線", addShot: "新增鏡頭", shotNumber: "鏡頭",
  startTime: "起始", shotDetails: "鏡頭內容", noShots: "暫無鏡頭", analyzeToBegin: "分析分格或手動新增鏡頭後開始編輯。",
  totalShots: "鏡頭總數", storyDetails: "故事與結構化輸出", storyTitle: "標題", synopsis: "梗概",
  characters: "角色", charactersPlaceholder: "每行一個角色", viralHook: "開場鉤子",
  soundDesign: "聲音設計", ending: "結尾", structuredOutput: "結構化輸出", visionModel: "識圖模型",
  fastVisionModel: "快速 2B", accurateVisionModel: "準確 8B", analyzePanels: "分析分格",
  generateStoryboard: "生成分鏡", analyzingPanels: "正在分析分格…", storyboardDone: "分鏡已生成",
  panel: "分格", none: "無", shotSize: "景別", cameraMovement: "運鏡", visualAction: "畫面動作",
  dialogue: "對白", sound: "聲音", transition: "轉場", visionFastOption: "快速識圖模型（2B）",
  visionAccurateOption: "準確識圖模型（8B）"
});
I18N["zh-TW"].help.storyboard = ["分鏡工作台", "先在本機偵測漫畫分格，再由所選視覺模型生成可編輯鏡頭時間線。漫畫模式忠於畫面證據；爆款影片模式可圍繞原圖人物和視覺錨點創作劇情。"];

const storedLanguage = localStorage.getItem("faithful-h3-language");
let language = Object.prototype.hasOwnProperty.call(I18N, storedLanguage) ? storedLanguage : "en";
let mode = "fl2va";
let busyCount = 0;
let statusTimer = null;
let visionStatusTimer = null;
let progressTimer = null;
let toastTimer = null;
let visionImageDataUrl = "";
let visionImageName = "";
let currentView = "h3";
const workspaceStore = new FaithfulWorkspace.WorkspaceStore(new FaithfulWorkspace.IndexedDbWorkspaceBackend());
const draftTimers = new Map();
let workspaceDialogType = "queue";
let workspaceDialogWorkspace = "h3";
let queueRunning = false;
let storyboardUI = null;
const $ = id => document.getElementById(id);
const t = key => I18N[language][key] || I18N.en[key] || key;

function setView(requestedView, updateHash = true) {
  const view = ["h3", "enrich", "vision", "storyboard"].includes(requestedView) ? requestedView : "h3";
  currentView = view;
  document.querySelectorAll(".view-tab").forEach(button => {
    const active = button.dataset.view === view;
    button.classList.toggle("active", active);
    button.setAttribute("aria-selected", String(active));
  });
  $("h3-view").hidden = view !== "h3";
  $("enrich-view").hidden = view !== "enrich";
  $("vision-view").hidden = view !== "vision";
  $("storyboard-view").hidden = view !== "storyboard";
  document.querySelector(".editor-workspace").classList.toggle("storyboard-active", view === "storyboard");
  document.querySelectorAll("[data-h3-control]").forEach(control => control.hidden = view === "vision" || view === "storyboard");
  if (view === "vision" || view === "storyboard") updateVisionStatus();
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
  const loadingText = currentView === "vision" || currentView === "storyboard" ? t("loadingVisionModel") : t("loadingModel");
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
    if (currentView === "vision" || currentView === "storyboard") await updateVisionStatus();
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
  if (storyboardUI) storyboardUI.apply(storyboardUI.payload());
  updateModelStatus();
  updateVisionStatus();
}

function updateDownloadOptions(data) {
  const states = Object.fromEntries(data.models.map(item => [item.id, item]));
  (data.vision_models || []).forEach(item => { states[`vision-${item.id}`] = item; });
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
    visionImageName = file.name || "";
    $("vision-preview").src = visionImageDataUrl;
    $("vision-preview").hidden = false;
    $("vision-dropzone").classList.add("has-preview");
    setStatus("vision-status", t("visionSelected"));
    scheduleDraftSave("vision");
    updateVisionStatus();
  });
  reader.addEventListener("error", () => setStatus("vision-status", t("invalidImage"), "error"));
  reader.readAsDataURL(file);
}

async function updateVisionStatus() {
  try {
    const data = await fetch("/api/status").then(response => response.json());
    const selectedId = currentView === "storyboard" ? ($("storyboard-model").value || "accurate") : ($("vision-model").value || "fast");
    const selected = (data.vision_models || []).find(item => item.id === selectedId) || {};
    const message = selected.downloading ? t("visionDownloading") : selected.loaded ? t("visionLoaded") : selected.ready ? t("visionReady") : t("visionMissing");
    if (currentView === "vision" || currentView === "storyboard") setTopStatus(selected.error || message, selected.error ? "error" : selected.ready ? "ready" : "neutral");
    $("vision-analyze").disabled = selectedId === $("vision-model").value && (selected.downloading || !selected.ready || !visionImageDataUrl);
    if (storyboardUI && currentView === "storyboard") storyboardUI.setModelAvailability(Boolean(selected.ready), Boolean(selected.downloading));
    if (selected.downloading && !visionStatusTimer) visionStatusTimer = setInterval(updateVisionStatus, 2000);
    if (!selected.downloading && visionStatusTimer) {
      clearInterval(visionStatusTimer);
      visionStatusTimer = null;
    }
  } catch (error) {
    if (currentView === "vision") setTopStatus(error.message, "error");
  }
}

const workspaceStatusIds = {h3: "source-status", enrich: "enrich-status", vision: "vision-status", storyboard: "storyboard-status"};
const workspaceActionIds = {h3: "convert-source", enrich: "enrich", vision: "vision-analyze", storyboard: "storyboard-generate"};

function workspacePayload(workspace) {
  if (workspace === "h3") return {mode, source: $("source-input").value, output: $("h3-output").value};
  if (workspace === "enrich") return {input: $("enrich-input").value, output: $("enrich-output").value, strength: Number($("strength").value)};
  if (workspace === "storyboard") return storyboardUI.payload();
  return {imageDataUrl: visionImageDataUrl, imageName: visionImageName, instruction: $("vision-instruction").value, output: $("vision-output").value, language, modelId: $("vision-model").value || "fast"};
}

function applyWorkspacePayload(workspace, payload = {}) {
  if (workspace === "h3") {
    mode = payload.mode === "ref2va" ? "ref2va" : "fl2va";
    document.querySelectorAll(".segment").forEach(button => {
      const active = button.dataset.mode === mode;
      button.classList.toggle("active", active);
      button.setAttribute("aria-selected", String(active));
    });
    $("source-input").value = payload.source || "";
    $("h3-output").value = payload.output || "";
  } else if (workspace === "enrich") {
    $("enrich-input").value = payload.input || "";
    $("enrich-output").value = payload.output || "";
    $("strength").value = Number.isFinite(Number(payload.strength)) ? payload.strength : 40;
    $("strength-value").value = $("strength").value;
  } else if (workspace === "vision") {
    visionImageDataUrl = payload.imageDataUrl || "";
    visionImageName = payload.imageName || "";
    $("vision-instruction").value = payload.instruction || "";
    $("vision-output").value = payload.output || "";
    $("vision-model").value = payload.modelId || "fast";
    const preview = $("vision-preview");
    preview.src = visionImageDataUrl;
    preview.hidden = !visionImageDataUrl;
    $("vision-dropzone").classList.toggle("has-preview", Boolean(visionImageDataUrl));
  } else {
    storyboardUI.apply(payload);
  }
}

function scheduleDraftSave(workspace) {
  document.querySelectorAll(`[data-workspace-tools="${workspace}"] [data-draft-state]`).forEach(el => el.classList.add("saving"));
  if (draftTimers.has(workspace)) clearTimeout(draftTimers.get(workspace));
  draftTimers.set(workspace, setTimeout(async () => {
    try {
      await workspaceStore.saveDraft(workspace, workspacePayload(workspace));
    } catch (error) {
      setTopStatus(error.message, "error");
    } finally {
      document.querySelectorAll(`[data-workspace-tools="${workspace}"] [data-draft-state]`).forEach(el => el.classList.remove("saving"));
      draftTimers.delete(workspace);
    }
  }, 250));
}

async function refreshWorkspaceIndicators(workspace) {
  const [queue, history] = await Promise.all([workspaceStore.getQueue(workspace), workspaceStore.getHistory(workspace)]);
  document.querySelectorAll(`[data-workspace-tools="${workspace}"] [data-queue-count]`).forEach(el => el.textContent = queue.length);
  document.querySelectorAll(`[data-workspace-tools="${workspace}"] [data-history-count]`).forEach(el => el.textContent = history.length);
}

async function restoreWorkspaceDrafts() {
  for (const workspace of ["h3", "enrich", "vision", "storyboard"]) {
    applyWorkspacePayload(workspace, await workspaceStore.getDraft(workspace));
    await refreshWorkspaceIndicators(workspace);
  }
  updateVisionStatus();
}

function queueInput(workspace) {
  const payload = workspacePayload(workspace);
  if (workspace === "h3" && !payload.source.trim()) throw new Error(t("enterPrompt"));
  if (workspace === "enrich" && !payload.input.trim()) throw new Error(t("enterPrompt"));
  if (workspace === "vision" && !payload.imageDataUrl) throw new Error(t("selectImage"));
  if (workspace === "storyboard" && !payload.imageDataUrl) throw new Error(t("selectImage"));
  return payload;
}

function displayInput(workspace, payload) {
  if (workspace === "vision" || workspace === "storyboard") return payload.imageName || t("imageFile");
  return String(workspace === "h3" ? (payload.source || payload.input || "") : (payload.input || payload.source || "")).trim();
}

async function callWorkspaceTask(workspace, payload) {
  if (workspace === "h3") return api("convert", payload.source, {mode: payload.mode});
  if (workspace === "enrich") return api("enrich", payload.input, {strength: Number(payload.strength)});
  if (workspace === "storyboard") {
    const response = await fetch("/api/storyboard/generate", {
      method: "POST", headers: {"Content-Type": "application/json"},
      body: JSON.stringify({
        image_data_url: payload.imageDataUrl, task_type: payload.taskType, goal: (payload.goal || "").trim(),
        language: payload.language || language, model_id: payload.modelId || "accurate", panel_boxes: payload.panelBoxes || [],
      }),
    });
    const data = await response.json();
    if (!response.ok) throw new Error(data.detail || t("requestFailed"));
    return data;
  }
  const response = await fetch("/api/vision/caption", {
    method: "POST", headers: {"Content-Type": "application/json"},
    body: JSON.stringify({image_data_url: payload.imageDataUrl, instruction: (payload.instruction || "").trim(), language: payload.language || language, model_id: payload.modelId || "fast"})
  });
  const data = await response.json();
  if (!response.ok) throw new Error(data.detail || t("requestFailed"));
  return data;
}

function applyTaskOutput(workspace, payload, output) {
  if (workspace === "h3") $("h3-output").value = output;
  else if (workspace === "enrich") $("enrich-output").value = output;
  else if (workspace === "vision") $("vision-output").value = output;
  else storyboardUI.applyGenerated(output);
}

async function runWorkspaceTask(workspace, payload, queueItem = null) {
  const statusId = workspaceStatusIds[workspace];
  const actionButton = $(workspaceActionIds[workspace]);
  if (workspace === "vision" || workspace === "storyboard") applyWorkspacePayload(workspace, payload);
  setStatus(statusId, t("working"), "loading");
  if (actionButton && !queueItem) setWorking(actionButton, true);
  const stopProgress = startProgressMonitor(statusId);
  try {
    const data = await callWorkspaceTask(workspace, payload);
    const output = data.output || "";
    applyTaskOutput(workspace, payload, output);
    const historyOutput = typeof output === "string" ? output : JSON.stringify(output);
    const historyEntry = {input: displayInput(workspace, payload), output: historyOutput, payload: {...payload, output}};
    if (queueItem) await workspaceStore.completeQueueItem(workspace, queueItem.id, historyEntry);
    else await workspaceStore.addHistory(workspace, historyEntry);
    await workspaceStore.saveDraft(workspace, {...payload, output});
    setStatus(statusId, runtimeMessage(data, workspace === "h3" ? t("directConvertDone") : workspace === "enrich" ? t("enrichDone") : workspace === "storyboard" ? t("storyboardDone") : t("visionDone")));
    await refreshWorkspaceIndicators(workspace);
    return true;
  } catch (error) {
    if (queueItem) await workspaceStore.failQueueItem(workspace, queueItem.id, error.message);
    setStatus(statusId, error.message, "error");
    await refreshWorkspaceIndicators(workspace);
    return false;
  } finally {
    await stopProgress();
    if (actionButton && !queueItem) setWorking(actionButton, false);
  }
}

async function runWorkspaceQueue(workspace) {
  if (queueRunning) return;
  const queue = await workspaceStore.getQueue(workspace);
  if (!queue.length) return setStatus(workspaceStatusIds[workspace], t("emptyQueue"), "error");
  queueRunning = true;
  setTopStatus(t("queueRunning"), "neutral");
  try {
    for (const item of queue) {
      applyWorkspacePayload(workspace, item.payload);
      await runWorkspaceTask(workspace, item.payload, item);
    }
    setStatus(workspaceStatusIds[workspace], t("queueComplete"));
  } finally {
    queueRunning = false;
    await refreshWorkspaceIndicators(workspace);
  }
}

function recordPreview(record, type) {
  if (type === "queue") return displayInput(workspaceDialogWorkspace, record.payload);
  return record.input || displayInput(workspaceDialogWorkspace, record.payload || {});
}

async function renderWorkspaceDialog() {
  const list = $("workspace-record-list");
  const isQueue = workspaceDialogType === "queue";
  const records = isQueue ? await workspaceStore.getQueue(workspaceDialogWorkspace) : await workspaceStore.getHistory(workspaceDialogWorkspace);
  list.replaceChildren();
  $("workspace-empty").hidden = records.length > 0;
  $("workspace-empty").textContent = t(isQueue ? "emptyQueue" : "emptyHistory");
  records.forEach(record => {
    const row = document.createElement("article");
    row.className = "workspace-record";
    row.dataset.id = record.id;
    if (isQueue) {
      row.draggable = true;
      row.addEventListener("dragstart", () => { row.classList.add("dragging"); });
      row.addEventListener("dragend", () => { row.classList.remove("dragging"); row.classList.remove("drag-over"); });
      row.addEventListener("dragover", event => { event.preventDefault(); row.classList.add("drag-over"); });
      row.addEventListener("dragleave", () => row.classList.remove("drag-over"));
      row.addEventListener("drop", async event => {
        event.preventDefault();
        const dragged = list.querySelector(".dragging");
        row.classList.remove("drag-over");
        if (dragged && dragged !== row) {
          await workspaceStore.reorderQueue(workspaceDialogWorkspace, dragged.dataset.id, row.dataset.id);
          await renderWorkspaceDialog();
          await refreshWorkspaceIndicators(workspaceDialogWorkspace);
        }
      });
    }
    const checkbox = document.createElement("input");
    checkbox.type = "checkbox"; checkbox.className = "record-select"; checkbox.dataset.recordId = record.id; checkbox.setAttribute("aria-label", t("selectAll"));
    const main = document.createElement("div"); main.className = "record-main";
    const title = document.createElement("p"); title.className = "record-title"; title.textContent = record.status === "failed" ? `${t("failed")}: ${record.error || ""}` : recordPreview(record, workspaceDialogType);
    const preview = document.createElement("p"); preview.className = "record-preview"; preview.textContent = record.output || record.payload?.output || record.payload?.instruction || "";
    const meta = document.createElement("div"); meta.className = "record-meta"; meta.textContent = record.createdAt ? new Date(record.createdAt).toLocaleString() : "";
    if (record.error) meta.classList.add("record-error");
    main.append(title, preview, meta);
    const actions = document.createElement("div"); actions.className = "record-actions";
    if (isQueue) { const drag = document.createElement("span"); drag.className = "record-drag"; drag.textContent = "\u2630"; drag.title = t("dragReorder"); actions.append(drag); }
    const restore = document.createElement("button"); restore.type = "button"; restore.className = "icon-button"; restore.textContent = "\u21b6"; restore.title = t("restore"); restore.addEventListener("click", () => { applyWorkspacePayload(workspaceDialogWorkspace, record.payload || {}); scheduleDraftSave(workspaceDialogWorkspace); $("workspace-dialog").close(); setView(workspaceDialogWorkspace); });
    const remove = document.createElement("button"); remove.type = "button"; remove.className = "icon-button"; remove.textContent = "\u00d7"; remove.title = t("delete"); remove.addEventListener("click", async () => { await (isQueue ? workspaceStore.deleteQueue(workspaceDialogWorkspace, [record.id]) : workspaceStore.deleteHistory(workspaceDialogWorkspace, [record.id])); await renderWorkspaceDialog(); await refreshWorkspaceIndicators(workspaceDialogWorkspace); });
    actions.append(restore, remove);
    row.append(checkbox, main, actions); list.append(row);
  });
  $("workspace-select-all").checked = false;
  $("workspace-delete-selected").disabled = true;
}

async function openWorkspaceDialog(type) {
  workspaceDialogType = type; workspaceDialogWorkspace = currentView;
  $("workspace-dialog-title").textContent = `${t(type === "queue" ? "queueTitle" : "historyTitle")} · ${t(workspaceDialogWorkspace + "View")}`;
  await renderWorkspaceDialog();
  $("workspace-dialog").showModal();
}

storyboardUI = FaithfulStoryboardUI.create({
  t,
  onDraft: () => scheduleDraftSave("storyboard"),
  setStatus: (message, type = "") => setStatus("storyboard-status", message, type),
});

document.querySelectorAll(".segment").forEach(button => button.addEventListener("click", () => {
  mode = button.dataset.mode;
  document.querySelectorAll(".segment").forEach(item => {
    const active = item === button;
    item.classList.toggle("active", active);
    item.setAttribute("aria-selected", String(active));
  });
  scheduleDraftSave("h3");
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
  scheduleDraftSave("h3");
  setView("h3");
  $("source-heading").scrollIntoView({behavior: "smooth", block: "start"});
  $("source-input").focus();
});

$("convert-source").addEventListener("click", async () => {
  try { await runWorkspaceTask("h3", queueInput("h3")); $("result-heading").scrollIntoView({behavior: "smooth", block: "start"}); }
  catch (error) { setStatus("source-status", error.message, "error"); }
});

$("enrich").addEventListener("click", async () => {
  try { await runWorkspaceTask("enrich", queueInput("enrich")); }
  catch (error) { setStatus("enrich-status", error.message, "error"); }
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
  try { await runWorkspaceTask("vision", queueInput("vision")); }
  catch (error) { setStatus("vision-status", error.message, "error"); }
});
$("storyboard-generate").addEventListener("click", async () => {
  try { await runWorkspaceTask("storyboard", queueInput("storyboard")); }
  catch (error) { setStatus("storyboard-status", error.message, "error"); }
});

["source-input", "h3-output"].forEach(id => $(id).addEventListener("input", () => scheduleDraftSave("h3")));
["enrich-input", "enrich-output", "strength"].forEach(id => $(id).addEventListener("input", () => scheduleDraftSave("enrich")));
$("vision-instruction").addEventListener("input", () => scheduleDraftSave("vision"));
$("vision-output").addEventListener("input", () => scheduleDraftSave("vision"));
$("vision-model").addEventListener("change", () => { scheduleDraftSave("vision"); updateVisionStatus(); });
$("storyboard-model").addEventListener("change", updateVisionStatus);

document.querySelectorAll("[data-workspace-action]").forEach(button => button.addEventListener("click", async () => {
  const workspace = button.closest("[data-workspace-tools]").dataset.workspaceTools;
  const action = button.dataset.workspaceAction;
  if (action === "queue") return openWorkspaceDialog("queue");
  if (action === "history") return openWorkspaceDialog("history");
  if (action === "run") return runWorkspaceQueue(workspace);
  button.disabled = true;
  try {
    await workspaceStore.enqueue(workspace, queueInput(workspace));
    await refreshWorkspaceIndicators(workspace);
    setStatus(workspaceStatusIds[workspace], t("queued"));
  } catch (error) {
    setStatus(workspaceStatusIds[workspace], error.message, "error");
  } finally {
    button.disabled = false;
  }
}));

$("workspace-dialog-close").addEventListener("click", () => $("workspace-dialog").close());
$("workspace-select-all").addEventListener("change", event => {
  $("workspace-record-list").querySelectorAll(".record-select").forEach(input => input.checked = event.target.checked);
  $("workspace-delete-selected").disabled = !event.target.checked;
});
$("workspace-record-list").addEventListener("change", event => {
  if (!event.target.classList.contains("record-select")) return;
  const selected = $("workspace-record-list").querySelectorAll(".record-select:checked").length;
  $("workspace-delete-selected").disabled = selected === 0;
});
$("workspace-delete-selected").addEventListener("click", async () => {
  const ids = [...$("workspace-record-list").querySelectorAll(".record-select:checked")].map(input => input.dataset.recordId);
  if (!ids.length) return;
  if (workspaceDialogType === "queue") await workspaceStore.deleteQueue(workspaceDialogWorkspace, ids);
  else await workspaceStore.deleteHistory(workspaceDialogWorkspace, ids);
  await renderWorkspaceDialog();
  await refreshWorkspaceIndicators(workspaceDialogWorkspace);
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
    if (currentView !== "vision" && currentView !== "storyboard") {
      el.textContent = (data.downloading ? t("downloading") : data.loaded ? t("modelLoading") : data.ready ? t("modelReady") : t("modelMissing")) + backend;
      el.className = `status ${data.error ? "status-error" : data.ready ? "status-ready" : "status-neutral"}`;
      if (data.error) el.textContent = data.error;
    }
    const allReady = data.models.every(item => item.ready) && (data.vision_models || []).every(item => item.ready);
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
restoreWorkspaceDrafts().catch(error => setTopStatus(error.message, "error"));
updateResourceMonitor();
setInterval(updateResourceMonitor, 2000);
