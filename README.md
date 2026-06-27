# Yuki GPT-SoVITS v4 Workflow

This repository documents and packages a GPT-SoVITS v4 character voice workflow for Yuki: audio selection, ASR, training notes, FastAPI deployment, and local emotion-reference mapping.

It includes the final v4 model weights and selected inference reference clips. It does not include the raw source audio or the full training dataset.

## Included Artifacts

- `model/yuki_v4-e15.ckpt` - GPT semantic model weights
- `model/yuki_v4_e8_s208_l32.pth` - SoVITS v4 LoRA weights
- `model/reference_yuki_001696.wav` - basic inference reference clip
- `model/reference_yuki_001696.txt` - transcript for the basic reference clip
- `configs/tts_infer_yuki_v4.yaml` - GPT-SoVITS v4 inference config
- `refs/selected/*.wav` - one final reference clip per emotion
- `refs/emotion_refs.json` - local emotion-to-reference mapping

Large model and audio artifacts are tracked with Git LFS.

## Yuki v4 Run Notes

- GPT-SoVITS version: v4 inference config, trained in a `GPT-SoVITS-v2pro-20250604` workspace
- Dataset: top 50 clips selected from `yuki_voice/*.ogg`
- SoVITS v4 LoRA: `yuki_v4_e8_s208_l32.pth`
- GPT weights: `yuki_v4-e15.ckpt`
- API port used locally: `9883`
- Language: Japanese (`ja`)
- Emotion labels: `neutral`, `happy`, `soft`, `sad`, `angry`, `surprised`, `excited`

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

## Requirements

- Git LFS
- GPT-SoVITS v4 runtime
- CUDA GPU recommended
- Python dependencies from `requirements.txt` for helper scripts

Install Git LFS before cloning:

```bash
git lfs install
git clone https://github.com/specetator/mizukami-yuki-gpt-sovits-v4.git
```

## Quick Start

1. Install and verify GPT-SoVITS v4.
2. Copy the model files into your GPT-SoVITS root:

```text
model/yuki_v4-e15.ckpt        -> GPT_weights_v4/yuki_v4-e15.ckpt
model/yuki_v4_e8_s208_l32.pth -> SoVITS_weights_v4/yuki_v4_e8_s208_l32.pth
configs/tts_infer_yuki_v4.yaml -> GPT_SoVITS/configs/tts_infer_yuki_v4.yaml
```

3. Start the API from the GPT-SoVITS root:

```bat
runtime\python.exe -u -I api_v2.py -a 0.0.0.0 -p 9883 -c GPT_SoVITS/configs/tts_infer_yuki_v4.yaml
```

4. Open the docs:

```text
http://127.0.0.1:9883/docs
```

5. Test a direct emotion reference request:

```bash
python scripts/test_tts_request.py --api http://127.0.0.1:9883 --emotion-json refs/emotion_refs.json --emotion soft --text "明日も一緒にいてくれる？" --out output/yuki_soft.wav
```

6. Optional: start the local emotion adapter:

```bash
python scripts/emotion_tts_adapter.py --refs refs/emotion_refs.json --gpt-sovits-api http://127.0.0.1:9883 --port 9893
```

Then send:

```json
{
  "emotion": "soft",
  "text": "明日も一緒にいてくれる？"
}
```

to:

```text
POST http://127.0.0.1:9893/tts
```

## Workflow Docs

- [Audio selection](docs/01_audio_selection.md)
- [GPT-SoVITS v4 training](docs/02_training_v4.md)
- [FastAPI deployment](docs/03_fastapi_deploy.md)
- [Local emotion mapping](docs/04_emotion_mapping.md)
- [Release checklist](docs/05_release_checklist.md)

## Notes

- `0.0.0.0` is a listening address. Use `127.0.0.1` locally.
- `ref_audio_path` must exist on the machine running GPT-SoVITS.
- The provided emotion JSON uses repository-relative paths; the Python helper scripts resolve them to absolute paths before calling GPT-SoVITS.
- Check the GPT-SoVITS license, pretrained model licenses, and rights for any training data before redistributing derived artifacts.
