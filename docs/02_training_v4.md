# 02. GPT-SoVITS v4 训练

目标：把筛选后的 yuki 数据训练成 GPT-SoVITS v4 可加载的 GPT 权重和 SoVITS v4 LoRA 权重。

## 训练前准备

确认 GPT-SoVITS 根目录中存在：

```text
runtime\python.exe
runtime\ffmpeg.exe 或系统 ffmpeg
api_v2.py
GPT_SoVITS/
GPT_SoVITS/pretrained_models/
```

确认 v4 预训练模型存在：

```text
GPT_SoVITS/pretrained_models/s1v3.ckpt
GPT_SoVITS/pretrained_models/gsv-v4-pretrained/s2Gv4.pth
GPT_SoVITS/pretrained_models/chinese-roberta-wwm-ext-large
GPT_SoVITS/pretrained_models/chinese-hubert-base
```

## ASR 转写

使用 faster-whisper 生成 GPT-SoVITS list：

```powershell
runtime\python.exe F:\AI_audio\yuki-gpt-sovits-v4-workflow\scripts\transcribe_faster_whisper.py `
  --input-dir F:\AI_audio\yuki_selected_50\wavs_16k `
  --output-list F:\AI_audio\yuki_selected_50\asr\yuki.list `
  --model-dir F:\AI_audio\GPT-SOVITS\GPT-SoVITS-v2pro-20250604\tools\asr\models\faster-whisper-medium `
  --language ja `
  --speaker yuki
```

list 格式：

```text
F:\path\to\clip.wav|yuki|JA|ここに正しい文字起こし
```

重要：ASR 输出必须人工校对。GPT-SoVITS 对 reference prompt 和训练文本非常敏感，乱码、错字、漏字都会影响音色稳定性。

## 数据导入 GPT-SoVITS

在 GPT-SoVITS WebUI 或项目脚本中创建实验名，例如：

```text
yuki_v4
```

建议记录：

- 训练列表路径：`F:\AI_audio\yuki_selected_50\asr\yuki.list`
- 说话人：`yuki`
- 语言：`JA`
- 版本：`v4`
- 数据规模：50 clips

## 预处理

按 GPT-SoVITS v4 的常规顺序执行：

1. 音频切分/格式处理
2. 文本清洗
3. 语义 token 提取
4. SSL/CNHubert 特征提取

预处理结果通常写入：

```text
logs/yuki_v4/
```

如果你复用 v2Pro 的已清洗数据，也要确认 v4 训练脚本读取的是兼容的 wav、文本和特征目录。

## 训练 SoVITS v4

本次 yuki 产物：

```text
SoVITS_weights_v4/yuki_v4_e8_s208_l32.pth
```

含义可按本次记录理解为：

- `e8`：第 8 epoch
- `s208`：约 208 step
- `l32`：LoRA rank/相关训练标记，按 GPT-SoVITS v4 输出命名为准

v4 LoRA 加载时可能出现 base key 缺失或 LoRA key 提示；如果此前同版本模型可正常推理，且 API 能合成音频，这类日志不一定是致命错误。

## 训练 GPT semantic model

本次 yuki 产物：

```text
GPT_weights_v4/yuki_v4-e15.ckpt
```

本次采用第 15 epoch 作为最终 GPT 权重。建议保留 `e5/e10/e15` 等中间权重，推理试听后再决定发布哪一个。

## 打包

最小可部署包：

```text
model/yuki_v4-e15.ckpt
model/yuki_v4_e8_s208_l32.pth
configs/tts_infer_yuki_v4.yaml
refs/emotion_refs.json
MODEL_CARD.md
```

如果公开发布，建议权重使用 Git LFS；如果没有明确授权，只发布文档、脚本和配置模板。
