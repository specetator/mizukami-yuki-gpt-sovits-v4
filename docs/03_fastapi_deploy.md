# 03. FastAPI 部署

目标：让 GPT-SoVITS v4 模型通过 `api_v2.py` 以 HTTP API 方式提供 TTS。

## 放置模型

把权重复制到 GPT-SoVITS 根目录：

```text
model/yuki_v4-e15.ckpt        -> GPT_weights_v4/yuki_v4-e15.ckpt
model/yuki_v4_e8_s208_l32.pth -> SoVITS_weights_v4/yuki_v4_e8_s208_l32.pth
```

把配置复制到：

```text
configs/tts_infer_yuki_v4.yaml -> GPT_SoVITS/configs/tts_infer_yuki_v4.yaml
```

配置核心字段：

```yaml
custom:
  device: cuda
  is_half: true
  t2s_weights_path: GPT_weights_v4/yuki_v4-e15.ckpt
  version: v4
  vits_weights_path: SoVITS_weights_v4/yuki_v4_e8_s208_l32.pth
```

## 端口检查

本次 yuki v4 使用 `9883`：

```powershell
python -c "import socket; s=socket.socket(); s.bind(('0.0.0.0',9883)); print('free'); s.close()"
```

如果提示端口占用，换一个端口，并同步更新启动脚本、FRP、本地客户端配置。

## 启动 API

在 GPT-SoVITS 根目录运行：

```bat
runtime\python.exe -u -I api_v2.py -a 0.0.0.0 -p 9883 -c GPT_SoVITS/configs/tts_infer_yuki_v4.yaml
```

或把 `scripts/start_api_from_gpt_sovits_root.bat` 放进 GPT-SoVITS 根目录的 `scripts/` 下运行。

启动成功后应看到类似：

```text
Uvicorn running on http://0.0.0.0:9883
```

本机打开：

```text
http://127.0.0.1:9883/docs
```

注意：`0.0.0.0` 是监听地址，不是浏览器访问地址。本机访问用 `127.0.0.1`，局域网访问用服务器 IP。

## 测试 TTS

```bash
python scripts/test_tts_request.py \
  --api http://127.0.0.1:9883 \
  --emotion-json refs/emotion_refs.json \
  --emotion neutral \
  --text "今日は少しだけ、あなたのそばにいてもいい？" \
  --out output/yuki_neutral.wav
```

请求体核心字段：

```json
{
  "text": "actual text",
  "text_lang": "ja",
  "ref_audio_path": "C:\\path\\to\\neutral.wav",
  "prompt_lang": "ja",
  "prompt_text": "reference transcript",
  "media_type": "wav",
  "streaming_mode": false
}
```

## Sakura FRP / Hermes

如果从外部服务调用本机 API：

- FRP local port 必须等于 API 端口，本次是 `9883`
- `ref_audio_path` 仍然是 API 机器上的本地路径
- 外部客户端只需要发送 `emotion` 和 `text`
- 本地适配层负责把 emotion 映射为 `ref_audio_path`、`prompt_text`

不要让远程客户端自行读取 Windows 本地参考音频路径。

## 本地情绪映射适配器

如果你希望 Hermes 或上游应用只发送：

```json
{
  "emotion": "soft",
  "text": "明日も一緒にいてくれる？"
}
```

启动适配器：

```bash
python scripts/emotion_tts_adapter.py \
  --refs refs/emotion_refs.json \
  --gpt-sovits-api http://127.0.0.1:9883 \
  --host 127.0.0.1 \
  --port 9893
```

适配器会读取 `emotion_refs.json`，补齐 `ref_audio_path`、`prompt_text`、`prompt_lang`，再转发到 GPT-SoVITS `/tts`。

测试：

```bash
curl -X POST http://127.0.0.1:9893/tts ^
  -H "Content-Type: application/json" ^
  -d "{\"emotion\":\"soft\",\"text\":\"明日も一緒にいてくれる？\"}" ^
  --output output.wav
```
