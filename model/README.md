# Model Artifacts

This folder contains the published yuki GPT-SoVITS v4 model artifacts.

Files:

```text
yuki_v4-e15.ckpt
yuki_v4_e8_s208_l32.pth
reference_yuki_001696.wav
reference_yuki_001696.txt
```

Copy targets inside a GPT-SoVITS root:

```text
model/yuki_v4-e15.ckpt        -> GPT_weights_v4/yuki_v4-e15.ckpt
model/yuki_v4_e8_s208_l32.pth -> SoVITS_weights_v4/yuki_v4_e8_s208_l32.pth
```

The reference wav/text pair can be used for a basic single-reference `/tts` request.
