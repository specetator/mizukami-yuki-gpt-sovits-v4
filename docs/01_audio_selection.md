# 01. 原始音频筛选

目标：从大量角色原始音频里筛出一小批足够干净、句长合适、响度稳定的训练素材。

本次 yuki 流程中，原始文件位于：

```text
F:\AI_audio\yuki_voice\*.ogg
```

最终筛选出 Top 50，并生成：

```text
yuki_selected_50/
  selected_top50.csv
  selected_top50.txt
  yuki_voice_quality_scores.csv
  ogg/
  wavs_16k/
```

## 选择标准

优先选择：

- 单人声，无明显 BGM、爆音、重叠说话
- 2 到 15 秒之间
- 静音比例低
- RMS 不过低也不过爆
- Peak 不贴近 0 dB
- 内容和情绪有一定变化

脚本使用的质量评分包括：

- 时长接近 6.5 秒
- 静音比例低于约 28%
- RMS 接近 -19 dB
- Peak 接近 -3 dB
- 比特率较高
- 对削波、过短、过长进行扣分

## 运行筛选

```powershell
powershell -ExecutionPolicy Bypass -File scripts\select_voice.ps1 `
  -SourceDir "F:\AI_audio\yuki_voice" `
  -OutputDir "F:\AI_audio\yuki_selected_50" `
  -Top 50 `
  -Extension "*.ogg"
```

输出：

```text
voice_quality_scores.csv  # 所有候选音频的评分
selected_top.csv          # 最终入选文件及指标
selected_top.txt          # 最终入选文件名
selected_audio/           # 入选原始音频副本
```

## 转成训练用 wav

GPT-SoVITS 的流程通常会继续处理音频，但建议先生成稳定的 16 kHz 单声道 wav 作为 ASR 输入：

```powershell
powershell -ExecutionPolicy Bypass -File scripts\convert_selected_to_wav16k.ps1 `
  -InputDir "F:\AI_audio\yuki_selected_50\selected_audio" `
  -OutputDir "F:\AI_audio\yuki_selected_50\wavs_16k"
```

## 人工复核

评分只用于初筛。训练前至少人工听一遍 Top 50，剔除：

- 背景音乐明显的片段
- 重叠人声
- 音效压过人声
- 过多喘息、笑声、哭声导致文本无法准确转写的片段
- ASR 明显难以识别的短促语气音

少量高质量数据通常比大量脏数据更适合第一版角色模型。
