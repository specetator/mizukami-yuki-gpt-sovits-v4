# 04. 本地情绪映射

目标：为每个情绪选一条稳定参考音频，并生成 `emotion_refs.json`，让本地 TTS 适配层按 emotion 选择参考。

## 情绪标签

固定使用：

```text
neutral   normal conversation
happy     cheerful, light, smiling
soft      gentle, quiet, intimate, soothing
sad       hurt, low, disappointed
angry     forceful, urgent, annoyed
surprised surprised, questioning, rising tone
excited   high-energy, thrilled
```

## 生成候选

先用已校对的训练 list 生成候选目录：

```bash
python scripts/classify_emotion_refs.py \
  --list F:\AI_audio\yuki_selected_50\asr\yuki.list \
  --out-dir F:\AI_audio\yuki_selected_50\emotion_reference_candidates
```

输出：

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

这个脚本只是候选排序，不是最终判断。最终必须人工听音频。

## 人工选择

每个情绪选一个最稳定的 clip：

- 音色清楚，背景干净
- 情绪表达明确但不过火
- 2 到 8 秒更容易稳定
- 文本能准确转写
- 避免哭喊、尖叫、重音效、长沉默

把选择结果填入：

```text
templates/emotion_prompt_text_template.csv
```

示例：

```csv
emotion,ref_audio_path,prompt_lang,prompt_text
soft,F:\AI_audio\refs_source\soft.wav,ja,ここに手で直した日本語テキスト
```

## 生成 refs

```bash
python scripts/build_emotion_refs.py \
  --prompt-csv templates/emotion_prompt_text_template.csv \
  --out-dir refs
```

脚本会：

- 将每个参考转为 mono 32000 Hz wav
- 写入 `refs/selected/<emotion>.wav`
- 生成 `refs/emotion_refs.json`
- 生成 `refs/emotion_refs.csv`

JSON schema：

```json
{
  "soft": {
    "ref_audio_path": "F:\\AI_audio\\...\\refs\\selected\\soft.wav",
    "prompt_lang": "ja",
    "prompt_text": "手动校对后的参考音频文本"
  }
}
```

## Hermes / 本地适配层契约

上游只需要提供：

```json
{
  "emotion": "soft",
  "text": "actual text to speak"
}
```

本地 TTS 适配层读取 `emotion_refs.json`，组装 GPT-SoVITS `/tts` 请求：

```json
{
  "text": "actual text to speak",
  "text_lang": "ja",
  "ref_audio_path": "F:\\AI_audio\\...\\soft.wav",
  "prompt_lang": "ja",
  "prompt_text": "reference audio transcript",
  "media_type": "wav",
  "streaming_mode": false
}
```

本仓库提供了 `scripts/emotion_tts_adapter.py`，它就是这个本地适配层的最小实现。

## 编码注意

现有历史文件中出现过日文 mojibake 乱码。公开流程里建议：

- 所有 `.list`、`.csv`、`.json` 使用 UTF-8 或 UTF-8 with BOM
- Windows PowerShell 控制台先执行 `chcp 65001`
- ASR 输出后必须人工打开校对
- 不要把乱码 prompt_text 写入 `emotion_refs.json`

`prompt_text` 的准确性会直接影响 GPT-SoVITS 的音色和发音稳定性。
