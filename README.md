# Yuki GPT-SoVITS v4 Workflow

Languages: [中文](#中文) | [English](#english) | [日本語](#日本語)

---

## 中文

这个仓库整理并发布了一套水上由岐 / Yuki 的 GPT-SoVITS v4 角色语音工作流，覆盖原始音频筛选、ASR 转写、训练记录、FastAPI 部署，以及本地 7 种情绪参考音频映射。

仓库包含最终 v4 模型权重和少量推理参考音频；不包含原始音频或完整训练集。

### 已包含内容

- `model/yuki_v4-e15.ckpt` - GPT semantic model 权重
- `model/yuki_v4_e8_s208_l32.pth` - SoVITS v4 LoRA 权重
- `model/reference_yuki_001696.wav` - 基础推理参考音频
- `model/reference_yuki_001696.txt` - 基础参考音频文本
- `configs/tts_infer_yuki_v4.yaml` - GPT-SoVITS v4 推理配置
- `refs/selected/*.wav` - 每个情绪一个最终参考音频
- `refs/emotion_refs.json` - 本地情绪到参考音频的映射

大模型和 wav 音频通过 Git LFS 管理。

### 本次 yuki v4 记录

- GPT-SoVITS 版本：v4 推理配置，在 `GPT-SoVITS-v2pro-20250604` 工作区训练
- 数据集：从 `yuki_voice/*.ogg` 中筛选 Top 50
- SoVITS v4 LoRA：`yuki_v4_e8_s208_l32.pth`
- GPT 权重：`yuki_v4-e15.ckpt`
- 本地 API 端口：`9883`
- 语言：日语 (`ja`)
- 情绪标签：`neutral`, `happy`, `soft`, `sad`, `angry`, `surprised`, `excited`

### 快速开始

先安装 Git LFS：

```bash
git lfs install
git clone https://github.com/specetator/mizukami-yuki-gpt-sovits-v4.git
```

把文件复制到 GPT-SoVITS 根目录：

```text
model/yuki_v4-e15.ckpt         -> GPT_weights_v4/yuki_v4-e15.ckpt
model/yuki_v4_e8_s208_l32.pth  -> SoVITS_weights_v4/yuki_v4_e8_s208_l32.pth
configs/tts_infer_yuki_v4.yaml -> GPT_SoVITS/configs/tts_infer_yuki_v4.yaml
```

从 GPT-SoVITS 根目录启动 API：

```bat
runtime\python.exe -u -I api_v2.py -a 0.0.0.0 -p 9883 -c GPT_SoVITS/configs/tts_infer_yuki_v4.yaml
```

打开：

```text
http://127.0.0.1:9883/docs
```

直接测试情绪参考：

```bash
python scripts/test_tts_request.py --api http://127.0.0.1:9883 --emotion-json refs/emotion_refs.json --emotion soft --text "明日も一緒にいてくれる？" --out output/yuki_soft.wav
```

推荐的本地情绪链路是：GPT-SoVITS 原生 API 跑在内部端口，adapter 跑在对外端口。这样上游可以只发送 `text`，由 adapter 在本地判断情绪并选择参考音频；如果上游已经发送 `emotion`，adapter 会优先使用上游给出的标签。

```bat
scripts\start_full_local_service.bat C:\path\to\GPT-SoVITS
```

请求：

```json
{
  "text": "明日も一緒にいてくれる？"
}
```

发送到：

```text
POST http://127.0.0.1:9883/tts
```

### 文档

- [音频筛选](docs/01_audio_selection.md)
- [GPT-SoVITS v4 训练](docs/02_training_v4.md)
- [FastAPI 部署](docs/03_fastapi_deploy.md)
- [本地情绪映射](docs/04_emotion_mapping.md)
- [发布检查](docs/05_release_checklist.md)

---

## English

This repository documents and packages a GPT-SoVITS v4 character voice workflow for Mizukami Yuki / Yuki: audio selection, ASR transcription, training notes, FastAPI deployment, and local mapping for seven emotion reference clips.

It includes the final v4 model weights and selected inference reference clips. It does not include the raw source audio or the full training dataset.

### Included Artifacts

- `model/yuki_v4-e15.ckpt` - GPT semantic model weights
- `model/yuki_v4_e8_s208_l32.pth` - SoVITS v4 LoRA weights
- `model/reference_yuki_001696.wav` - basic inference reference clip
- `model/reference_yuki_001696.txt` - transcript for the basic reference clip
- `configs/tts_infer_yuki_v4.yaml` - GPT-SoVITS v4 inference config
- `refs/selected/*.wav` - one final reference clip per emotion
- `refs/emotion_refs.json` - local emotion-to-reference mapping

Large model and audio artifacts are tracked with Git LFS.

### Yuki v4 Run Notes

- GPT-SoVITS version: v4 inference config, trained in a `GPT-SoVITS-v2pro-20250604` workspace
- Dataset: top 50 clips selected from `yuki_voice/*.ogg`
- SoVITS v4 LoRA: `yuki_v4_e8_s208_l32.pth`
- GPT weights: `yuki_v4-e15.ckpt`
- Local API port: `9883`
- Language: Japanese (`ja`)
- Emotion labels: `neutral`, `happy`, `soft`, `sad`, `angry`, `surprised`, `excited`

### Quick Start

Install Git LFS before cloning:

```bash
git lfs install
git clone https://github.com/specetator/mizukami-yuki-gpt-sovits-v4.git
```

Copy the files into your GPT-SoVITS root:

```text
model/yuki_v4-e15.ckpt         -> GPT_weights_v4/yuki_v4-e15.ckpt
model/yuki_v4_e8_s208_l32.pth  -> SoVITS_weights_v4/yuki_v4_e8_s208_l32.pth
configs/tts_infer_yuki_v4.yaml -> GPT_SoVITS/configs/tts_infer_yuki_v4.yaml
```

Start the API from the GPT-SoVITS root:

```bat
runtime\python.exe -u -I api_v2.py -a 0.0.0.0 -p 9883 -c GPT_SoVITS/configs/tts_infer_yuki_v4.yaml
```

Open:

```text
http://127.0.0.1:9883/docs
```

Test a direct emotion reference request:

```bash
python scripts/test_tts_request.py --api http://127.0.0.1:9883 --emotion-json refs/emotion_refs.json --emotion soft --text "明日も一緒にいてくれる？" --out output/yuki_soft.wav
```

Recommended local emotion chain: run the raw GPT-SoVITS API on an internal port and expose the adapter port to your client. The adapter can infer an emotion locally from `text`; if the request already contains `emotion`, it uses that label instead.

```bat
scripts\start_full_local_service.bat C:\path\to\GPT-SoVITS
```

Then send:

```json
{
  "text": "明日も一緒にいてくれる？"
}
```

to:

```text
POST http://127.0.0.1:9883/tts
```

### Documentation

- [Audio selection](docs/01_audio_selection.md)
- [GPT-SoVITS v4 training](docs/02_training_v4.md)
- [FastAPI deployment](docs/03_fastapi_deploy.md)
- [Local emotion mapping](docs/04_emotion_mapping.md)
- [Release checklist](docs/05_release_checklist.md)

---

## 日本語

このリポジトリは、水上由岐 / Yuki 向けの GPT-SoVITS v4 キャラクターボイス制作ワークフローをまとめたものです。音声選別、ASR 文字起こし、学習メモ、FastAPI デプロイ、7 種類の感情リファレンス音声のローカルマッピングを含みます。

最終版の v4 モデル重みと推論用リファレンス音声を含みますが、元音声や完全な学習データセットは含みません。

### 含まれるもの

- `model/yuki_v4-e15.ckpt` - GPT semantic model の重み
- `model/yuki_v4_e8_s208_l32.pth` - SoVITS v4 LoRA 重み
- `model/reference_yuki_001696.wav` - 基本推論用リファレンス音声
- `model/reference_yuki_001696.txt` - 基本リファレンス音声のテキスト
- `configs/tts_infer_yuki_v4.yaml` - GPT-SoVITS v4 推論設定
- `refs/selected/*.wav` - 各感情につき 1 つの最終リファレンス音声
- `refs/emotion_refs.json` - 感情ラベルからリファレンス音声へのローカルマッピング

大きなモデルファイルと wav 音声は Git LFS で管理しています。

### yuki v4 の記録

- GPT-SoVITS バージョン：v4 推論設定、`GPT-SoVITS-v2pro-20250604` ワークスペースで学習
- データセット：`yuki_voice/*.ogg` から上位 50 クリップを選別
- SoVITS v4 LoRA：`yuki_v4_e8_s208_l32.pth`
- GPT 重み：`yuki_v4-e15.ckpt`
- ローカル API ポート：`9883`
- 言語：日本語 (`ja`)
- 感情ラベル：`neutral`, `happy`, `soft`, `sad`, `angry`, `surprised`, `excited`

### クイックスタート

クローン前に Git LFS を有効化します。

```bash
git lfs install
git clone https://github.com/specetator/mizukami-yuki-gpt-sovits-v4.git
```

GPT-SoVITS のルートディレクトリにファイルをコピーします。

```text
model/yuki_v4-e15.ckpt         -> GPT_weights_v4/yuki_v4-e15.ckpt
model/yuki_v4_e8_s208_l32.pth  -> SoVITS_weights_v4/yuki_v4_e8_s208_l32.pth
configs/tts_infer_yuki_v4.yaml -> GPT_SoVITS/configs/tts_infer_yuki_v4.yaml
```

GPT-SoVITS のルートディレクトリから API を起動します。

```bat
runtime\python.exe -u -I api_v2.py -a 0.0.0.0 -p 9883 -c GPT_SoVITS/configs/tts_infer_yuki_v4.yaml
```

ブラウザで開きます。

```text
http://127.0.0.1:9883/docs
```

感情リファレンスを直接テストします。

```bash
python scripts/test_tts_request.py --api http://127.0.0.1:9883 --emotion-json refs/emotion_refs.json --emotion soft --text "明日も一緒にいてくれる？" --out output/yuki_soft.wav
```

推奨されるローカル感情チェーンでは、GPT-SoVITS の生 API を内部ポートで起動し、adapter を外部向けポートにします。adapter は `text` からローカルで感情を推定できます。リクエストに `emotion` が含まれる場合は、そのラベルを優先します。

```bat
scripts\start_full_local_service.bat C:\path\to\GPT-SoVITS
```

次の JSON を送信します。

```json
{
  "text": "明日も一緒にいてくれる？"
}
```

送信先：

```text
POST http://127.0.0.1:9883/tts
```

### ドキュメント

- [音声選別](docs/01_audio_selection.md)
- [GPT-SoVITS v4 学習](docs/02_training_v4.md)
- [FastAPI デプロイ](docs/03_fastapi_deploy.md)
- [ローカル感情マッピング](docs/04_emotion_mapping.md)
- [リリースチェックリスト](docs/05_release_checklist.md)

---

## Repository Structure

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
  model/
    yuki_v4-e15.ckpt
    yuki_v4_e8_s208_l32.pth
    reference_yuki_001696.wav
    reference_yuki_001696.txt
  refs/
    selected/
      neutral.wav
      happy.wav
      soft.wav
      sad.wav
      angry.wav
      surprised.wav
      excited.wav
    emotion_refs.json
    emotion_refs.csv
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
```

## Notes / 注意事項

- `0.0.0.0` is a listening address. Use `127.0.0.1` locally.
- `ref_audio_path` must exist on the machine running GPT-SoVITS.
- `emotion_refs.json` uses repository-relative paths; the Python helper scripts resolve them to absolute paths before calling GPT-SoVITS.
- Check the GPT-SoVITS license, pretrained model licenses, and rights for any training data before redistributing derived artifacts.
