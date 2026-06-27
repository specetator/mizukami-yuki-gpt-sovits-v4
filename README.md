# Yuki GPT-SoVITS v4 Workflow

这个仓库整理了一套从角色原始音频筛选、转写、GPT-SoVITS v4 训练、模型打包，到 FastAPI 部署和本地情绪映射的完整流程。它来自一次 yuki 声音训练实践，但脚本都尽量做成了可复用模板。

> 注意：本仓库默认不包含原始音频、训练集、参考音频和模型权重。公开发布前请确认训练素材、角色声音、模型权重和生成音频的授权范围。

## 当前 yuki v4 记录

- GPT-SoVITS 版本：v4 推理配置，基于 `GPT-SoVITS-v2pro-20250604` 工作区
- 训练集：从 `yuki_voice/*.ogg` 中按音频质量筛选 Top 50
- SoVITS v4 LoRA 权重：`yuki_v4_e8_s208_l32.pth`
- GPT 权重：`yuki_v4-e15.ckpt`
- 推理配置：`configs/tts_infer_yuki_v4.yaml`
- API 端口：`9883`
- 语言：`ja`
- 情绪标签：`neutral`, `happy`, `soft`, `sad`, `angry`, `surprised`, `excited`

## 仓库结构

```text
.
  configs/
    tts_infer_yuki_v4.yaml
  docs/
    01_audio_selection.md
    02_training_v4.md
    03_fastapi_deploy.md
    04_emotion_mapping.md
    05_release_checklist.md
  scripts/
    emotion_tts_adapter.py
    select_voice.ps1
    convert_selected_to_wav16k.ps1
    transcribe_faster_whisper.py
    classify_emotion_refs.py
    build_emotion_refs.py
    start_api_from_gpt_sovits_root.bat
    test_tts_request.py
  templates/
    emotion_prompt_text_template.csv
    emotion_refs.example.json
  model/
    README.md
  refs/
    README.md
  MODEL_CARD.md
```

## 快速开始

1. 安装并确认 GPT-SoVITS v4 能正常启动。
2. 把本仓库 `configs/tts_infer_yuki_v4.yaml` 复制到 GPT-SoVITS 根目录下的 `GPT_SoVITS/configs/`。
3. 把模型权重放到 GPT-SoVITS 根目录：

```text
model/yuki_v4-e15.ckpt              -> GPT_weights_v4/yuki_v4-e15.ckpt
model/yuki_v4_e8_s208_l32.pth       -> SoVITS_weights_v4/yuki_v4_e8_s208_l32.pth
```

4. 从 GPT-SoVITS 根目录启动 API：

```bat
scripts\start_api_from_gpt_sovits_root.bat
```

或者手动运行：

```bat
runtime\python.exe -u -I api_v2.py -a 0.0.0.0 -p 9883 -c GPT_SoVITS/configs/tts_infer_yuki_v4.yaml
```

5. 打开：

```text
http://127.0.0.1:9883/docs
```

6. 用参考音频调用 `/tts`：

```bash
python scripts/test_tts_request.py --api http://127.0.0.1:9883 --emotion-json refs/emotion_refs.json --emotion soft --text "明日も一緒にいてくれる？" --out output/yuki_soft.wav
```

7. 可选：启动本地情绪映射适配器，让上游只传 `emotion` 和 `text`：

```bash
python scripts/emotion_tts_adapter.py --refs refs/emotion_refs.json --gpt-sovits-api http://127.0.0.1:9883 --port 9893
```

然后请求：

```text
POST http://127.0.0.1:9893/tts
```

## 完整流程

按顺序阅读：

- [音频筛选](docs/01_audio_selection.md)
- [GPT-SoVITS v4 训练](docs/02_training_v4.md)
- [FastAPI 部署](docs/03_fastapi_deploy.md)
- [本地情绪映射](docs/04_emotion_mapping.md)
- [开源发布检查](docs/05_release_checklist.md)

## 关键约定

- 训练列表格式：`wav_path|speaker|lang|text`
- yuki 语言：`JA` / API 中使用 `ja`
- 参考音频推荐：mono、32000 Hz、PCM s16le wav
- `ref_audio_path` 必须是运行 GPT-SoVITS API 的机器能访问的本地路径
- 远程调用时只暴露 API 地址，不要把 Windows 本地路径发给客户端让它读取

## 授权提醒

GPT-SoVITS 本体、预训练模型、训练素材、角色声音和你训练出的权重可能分别受不同协议约束。公开仓库建议默认只开源流程脚本和文档；如需发布权重，请使用 Git LFS，并在 `MODEL_CARD.md` 中写明数据来源、授权、限制和禁止用途。
