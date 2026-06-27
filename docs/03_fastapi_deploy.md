# 03. FastAPI Deployment

This project supports two API layers:

- Raw GPT-SoVITS API: receives complete `/tts` requests with `ref_audio_path` and `prompt_text`.
- Local TTS router: receives `emotion + text`, maps the emotion to local reference audio, and forwards a complete request to GPT-SoVITS.

The recommended setup is option B:

```text
AI agent / Hermes
  -> understands emotion with the main model
  -> sends emotion + text
  -> http://127.0.0.1:9883/tts  local_tts_router.py
  -> http://127.0.0.1:9884/tts  raw GPT-SoVITS API
```

`local_tts_router.py` does not provide large-model emotion understanding. It only routes a provided emotion label to local reference audio and `prompt_text`.

## Place Model Files

Copy the model files into your GPT-SoVITS root:

```text
model/yuki_v4-e15.ckpt         -> GPT_weights_v4/yuki_v4-e15.ckpt
model/yuki_v4_e8_s208_l32.pth  -> SoVITS_weights_v4/yuki_v4_e8_s208_l32.pth
configs/tts_infer_yuki_v4.yaml -> GPT_SoVITS/configs/tts_infer_yuki_v4.yaml
```

Key config fields:

```yaml
custom:
  device: cuda
  is_half: true
  t2s_weights_path: GPT_weights_v4/yuki_v4-e15.ckpt
  version: v4
  vits_weights_path: SoVITS_weights_v4/yuki_v4_e8_s208_l32.pth
```

## Raw GPT-SoVITS API

Start the raw API from the GPT-SoVITS root:

```bat
runtime\python.exe -u -I api_v2.py -a 0.0.0.0 -p 9884 -c GPT_SoVITS/configs/tts_infer_yuki_v4.yaml
```

Open:

```text
http://127.0.0.1:9884/docs
```

The raw API requires complete TTS fields:

```json
{
  "text": "actual text",
  "text_lang": "ja",
  "ref_audio_path": "C:\\path\\to\\soft.wav",
  "prompt_lang": "ja",
  "prompt_text": "reference transcript",
  "media_type": "wav",
  "streaming_mode": false
}
```

## Local TTS Router

Start the full local service:

```bat
scripts\start_full_local_service.bat C:\path\to\GPT-SoVITS
```

Or start the router manually after the raw API is already running:

```bash
python scripts/local_tts_router.py \
  --refs refs/emotion_refs.json \
  --gpt-sovits-api http://127.0.0.1:9884 \
  --host 0.0.0.0 \
  --port 9883
```

Your AI agent / Hermes should call the router:

```json
{
  "emotion": "soft",
  "text": "明日も一緒にいてくれる？"
}
```

Test with curl:

```bash
curl -X POST http://127.0.0.1:9883/tts ^
  -H "Content-Type: application/json" ^
  -d "{\"emotion\":\"soft\",\"text\":\"明日も一緒にいてくれる？\"}" ^
  --output output.wav
```

The router reads `refs/emotion_refs.json`, fills `ref_audio_path`, `prompt_text`, and `prompt_lang`, then forwards the request to the raw GPT-SoVITS API.

## Hermes / FRP Notes

- Point Hermes or your client at the router port, usually `9883`.
- Keep the raw GPT-SoVITS API as an internal service, usually `9884`.
- `ref_audio_path` remains a path on the machine running GPT-SoVITS.
- Remote clients should not read Windows local paths directly.
