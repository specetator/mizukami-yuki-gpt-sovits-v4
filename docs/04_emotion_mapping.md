# 04. Emotion Reference Mapping

The goal is to choose one stable reference clip for each emotion and generate `emotion_refs.json`.

In the recommended option B architecture:

- AI agent / Hermes performs large-model emotion understanding.
- The agent sends `emotion + text`.
- `scripts/local_tts_router.py` maps `emotion` to local reference audio and `prompt_text`.
- GPT-SoVITS receives a complete `/tts` request.

`local_tts_router.py` is a router, not an emotion-recognition model.

## Emotion Labels

Use these stable labels:

```text
neutral   normal conversation
happy     cheerful, light, smiling
soft      gentle, quiet, intimate, soothing
sad       hurt, low, disappointed
angry     forceful, urgent, annoyed
surprised surprised, questioning, rising tone
excited   high-energy, thrilled
```

## Candidate Selection

You can generate candidate folders from a corrected GPT-SoVITS list:

```bash
python scripts/classify_emotion_refs.py \
  --list F:\AI_audio\yuki_selected_50\asr\yuki.list \
  --out-dir F:\AI_audio\yuki_selected_50\emotion_reference_candidates
```

This creates:

```text
emotion_reference_candidates/
  neutral/
  happy/
  soft/
  sad/
  angry/
  surprised/
  excited/
  emotion_candidates.csv
  summary.txt
```

This script only helps sort candidates. The final choice should be made by listening manually.

## Final Reference Rules

Choose one final clip per emotion:

- clear voice, minimal background noise
- stable character tone
- clear emotional color without being too extreme
- usually 2 to 8 seconds
- prompt text can be transcribed accurately

Avoid clips with heavy effects, overlapping voices, screaming, crying, or long silence.

## Generate `emotion_refs.json`

Fill:

```text
templates/emotion_prompt_text_template.csv
```

Then run:

```bash
python scripts/build_emotion_refs.py \
  --prompt-csv templates/emotion_prompt_text_template.csv \
  --out-dir refs
```

This produces:

```text
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
```

JSON schema:

```json
{
  "soft": {
    "ref_audio_path": "selected/soft.wav",
    "prompt_lang": "ja",
    "prompt_text": "reference transcript"
  }
}
```

## Router Contract

The AI agent / Hermes sends:

```json
{
  "emotion": "soft",
  "text": "actual text to speak"
}
```

The local router sends GPT-SoVITS:

```json
{
  "text": "actual text to speak",
  "text_lang": "ja",
  "ref_audio_path": "F:\\AI_audio\\...\\refs\\selected\\soft.wav",
  "prompt_lang": "ja",
  "prompt_text": "reference audio transcript",
  "media_type": "wav",
  "streaming_mode": false
}
```

## Encoding Notes

Use UTF-8 for `.list`, `.csv`, and `.json` files. Manually correct ASR output before using it as `prompt_text`; incorrect prompt text can reduce GPT-SoVITS stability and voice quality.
