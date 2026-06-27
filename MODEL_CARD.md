# Model Card: Yuki GPT-SoVITS v4

## Model Summary

- Model type: GPT-SoVITS v4 character voice model
- Speaker label: `yuki`
- Language: Japanese (`ja`)
- Output: speech waveform through GPT-SoVITS FastAPI
- Training data size in this run: 50 selected clips

## Artifacts

Expected files when weights are published:

```text
model/yuki_v4-e15.ckpt
model/yuki_v4_e8_s208_l32.pth
configs/tts_infer_yuki_v4.yaml
refs/emotion_refs.json
```

## Intended Use

- Local experimentation with GPT-SoVITS v4 deployment
- Reproducible documentation of a character voice workflow
- Emotion-reference mapping for local applications

## Limitations

- Quality depends heavily on reference audio and exact `prompt_text`.
- Short, noisy, multi-speaker, or mistranscribed clips reduce stability.
- Emotion labels are reference-selection labels, not a true controllable emotion model.
- v4 LoRA/base-model loading can take one to two minutes on first start.

## Data and Rights

Fill this section before publishing weights:

- Source of raw audio:
- Permission/license for source audio:
- Permission/license for trained model redistribution:
- Prohibited uses:
- Contact/takedown process:

## Safety Notes

Do not use this model to impersonate real people, bypass consent, or mislead listeners about the origin of generated audio.
