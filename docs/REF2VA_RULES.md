# MiniMax H3 Ref2VA 规则

Ref2VA 输出必须按以下六段顺序生成：

```text
subject_definitions:
summary:
retention_analysis:
detailed_description:
overall_soundscape:
non_diegetic_music:
```

同一个 sliding window 内六段之间不得插入空行；空行只用于分隔下一个窗口。`[Shot 1]` 不带时间戳，后续镜头使用严格递增的 `[Shot N] At MM:SS.mmm, ...`。

每个可复用标签都要有明确的定义行。若 Picture 只用于角色、场景、服装、风格或动作参考，应写在 `<Subject N>` 定义中，不得自动变成时间轴首帧；只有原文明确指定首帧、尾帧、关键帧或构图锚点时，才单独写 Picture 时间轴角色。

`<Subject N>` 表示目标视频实际复用的人物、动物、物体、环境、服装、风格或动作。角色或风格参考图应在 Subject 定义中引用 `<Picture N>`，除非原文明确指定首帧、尾帧、关键帧或构图锚点，否则不能把该图片写成时间轴帧。`<Video N>` 与 `<Audio N>` 独立编号，并在定义、摘要、保留分析和时间轴中保持同一含义。

`summary` 必须以实际任务类型开头，例如 `[reference generation]`、`[reference generation + audio reference]`、`[video editing + audio reuse]` 或 `[video continuation]`；仅提供参考视频/音频不自动等于编辑、续接或复制音频。

中文镜头标记如 `[镜头1]`、`[镜头2]：3秒`、`镜头3: 5秒` 必须归一化为 `[Shot 1]`、`[Shot 2] At 00:03.000, ...`、`[Shot 3] At 00:05.000, ...`，成品中不得残留中文镜头标签或相对秒数短语。

`retention_analysis` 每个引用标签一行：视觉使用 `fully_preserved`、`partially_preserved`、`attribute_transfer`、`weak_reference`；音频使用 `fully_copy`、`partially_copy`、`reference`、`weak_reference`。对白只写在 `<d>[Language] ...</d>` 中；跨镜头对白使用 `<scenetrans>`，仅在视频结尾截断时使用 `<cutoff>`。
