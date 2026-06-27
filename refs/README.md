# Emotion References

This folder is for final reference clips and emotion mapping files.

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

Each final reference should be a mono 32000 Hz wav. Keep exactly one stable reference per emotion unless your application explicitly supports random selection.
