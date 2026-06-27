# Model Card: Yuki GPT-SoVITS v4

## Model Summary

- Model type: GPT-SoVITS v4 character voice model
- Speaker label: `yuki`
- Language: Japanese (`ja`)
- Output: speech waveform through GPT-SoVITS FastAPI
- Training data size in this run: 50 selected clips

## Artifacts

Published files:

```text
model/yuki_v4-e15.ckpt
model/yuki_v4_e8_s208_l32.pth
model/reference_yuki_001696.wav
model/reference_yuki_001696.txt
configs/tts_infer_yuki_v4.yaml
refs/selected/*.wav
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

Current release notes:

- Source of raw audio: user-curated Yuki character clips
- Published artifacts: final GPT-SoVITS v4 weights and selected inference reference clips
- Raw training clips: not included
- Full training set: not included
- Redistribution terms: repository owner asserts they have permission to publish these artifacts
- Prohibited uses: impersonation, deception, harassment, or use without respecting the original work and applicable rights
- Contact/takedown process: open a GitHub issue or contact the repository owner

## Safety Notes

Do not use this model to impersonate real people, bypass consent, or mislead listeners about the origin of generated audio.
