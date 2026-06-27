# Emotion References

This folder contains final reference clips and emotion mapping files.

Recommended structure:

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

Each final reference is a mono 32000 Hz wav. The JSON paths are repository-relative; the provided Python adapter resolves them to absolute paths before calling GPT-SoVITS.
