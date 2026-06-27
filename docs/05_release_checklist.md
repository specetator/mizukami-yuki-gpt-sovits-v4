# 05. 开源发布检查

发布前按这个清单检查。

## 不应直接提交

- 原始游戏/动画/视频音频
- 未授权训练集
- 未授权参考音频
- 未授权模型权重
- 生成的大量测试音频
- 本机绝对路径里的隐私信息
- API 日志、缓存、临时目录

## 可以提交

- 流程文档
- 参数化脚本
- 推理配置模板
- `MODEL_CARD.md`
- 空的 `model/` 和 `refs/` README
- 示例 JSON/CSV 模板
- 小型、明确可授权的演示音频

## 如果发布权重

1. 确认有权发布权重和相关参考音频。
2. 启用 Git LFS：

```bash
git lfs install
git lfs track "*.ckpt" "*.pth" "*.wav"
```

3. 补全 `MODEL_CARD.md`：

```text
Source of raw audio
Permission/license
Redistribution terms
Prohibited uses
Contact/takedown process
```

4. 在 README 明确标注模型用途限制。

## 本地发布前自检

```powershell
rg "F:\\AI_audio" yuki-gpt-sovits-v4-workflow
rg "yuki_voice|yuki_selected_50|TEMP|hf_cache" yuki-gpt-sovits-v4-workflow
rg "銇|倝|仯|锛|鈥" yuki-gpt-sovits-v4-workflow
```

允许 README/docs 中出现 yuki 实战路径说明，但配置、脚本和模板不应依赖你的本机绝对路径。

## API 验证

- `http://127.0.0.1:9883/docs` 可打开
- `/tts` 请求返回 wav
- 每个 `emotion_refs.json` 中的 `ref_audio_path` 都存在
- 每个 `prompt_text` 都是人工校对后的正确日文
- FRP local port 与 API 端口一致

## 建议仓库描述

```text
Reproducible GPT-SoVITS v4 character voice workflow: audio selection, ASR, training notes, FastAPI deployment, and local emotion reference mapping.
```
