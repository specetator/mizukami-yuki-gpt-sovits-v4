import argparse
import json
import os
from pathlib import Path
from typing import Any, Optional

import requests
import uvicorn
from fastapi import FastAPI, HTTPException
from fastapi.responses import Response
from pydantic import BaseModel, Field


class TTSRequest(BaseModel):
    text: str = Field(..., min_length=1)
    emotion: Optional[str] = None
    text_lang: str = "ja"
    text_split_method: str = "cut5"
    batch_size: int = 1
    media_type: str = "wav"
    streaming_mode: bool = False
    extra: Optional[dict[str, Any]] = None


def load_refs(path: Path) -> dict[str, dict[str, str]]:
    if not path.exists():
        raise FileNotFoundError(f"emotion refs not found: {path}")
    refs = json.loads(path.read_text(encoding="utf-8"))
    if "neutral" not in refs:
        raise ValueError("emotion refs must include a neutral fallback")
    base_dir = path.resolve().parent
    for ref in refs.values():
        audio_path = Path(ref["ref_audio_path"])
        if not audio_path.is_absolute():
            ref["ref_audio_path"] = str((base_dir / audio_path).resolve())
    return refs


def classify_emotion(text: str, available: set[str]) -> str:
    normalized = text.strip().lower()

    # Keep this local and dependency-free. It is a lightweight routing heuristic,
    # not a replacement for a full emotion model.
    scores = {
        "neutral": 0,
        "happy": 0,
        "soft": 0,
        "sad": 0,
        "angry": 0,
        "surprised": 0,
        "excited": 0,
    }

    if any(mark in text for mark in ["!", "！"]):
        scores["excited"] += 2
        scores["angry"] += 1
    if any(mark in text for mark in ["?", "？", "の?", "かな", "でしょうか"]):
        scores["surprised"] += 2
    if any(mark in text for mark in ["...", "…", "。", "、"]):
        scores["soft"] += 1

    keyword_scores = {
        "happy": ["嬉しい", "楽しい", "よかった", "ありがとう", "好き", "笑", "happy", "glad", "thanks"],
        "soft": ["そば", "一緒", "大丈夫", "おやすみ", "優しい", "静か", "soft", "gentle", "quiet"],
        "sad": ["ごめん", "すみません", "寂しい", "悲しい", "泣", "失敗", "守れなかった", "sad", "sorry"],
        "angry": ["嫌", "だめ", "やめて", "怒", "許さない", "馬鹿", "ふざけ", "angry", "stop"],
        "surprised": ["えっ", "まさか", "本当", "なんで", "どうして", "surprised", "really"],
        "excited": ["すごい", "最高", "もちろん", "やった", "急いで", "excited", "amazing"],
    }
    for emotion, keywords in keyword_scores.items():
        for keyword in keywords:
            if keyword in normalized or keyword in text:
                scores[emotion] += 2

    if len(text) <= 18:
        scores["soft"] += 1
    if len(text) >= 80:
        scores["neutral"] += 1

    ranked = sorted(scores.items(), key=lambda item: item[1], reverse=True)
    for emotion, score in ranked:
        if emotion in available and score > 0:
            return emotion
    return "neutral"


def create_app(refs_path: Path, gpt_sovits_api: str) -> FastAPI:
    refs = load_refs(refs_path)
    available = set(refs.keys())
    app = FastAPI(title="Emotion TTS Adapter", version="1.0.0")

    @app.get("/health")
    def health():
        return {
            "ok": True,
            "gpt_sovits_api": gpt_sovits_api,
            "emotions": sorted(refs.keys()),
        }

    @app.post("/classify")
    def classify(req: TTSRequest):
        emotion = req.emotion if req.emotion in available else classify_emotion(req.text, available)
        return {"emotion": emotion, "source": "request" if req.emotion in available else "local_heuristic"}

    @app.get("/emotions")
    def emotions():
        return refs

    @app.post("/tts")
    def tts(req: TTSRequest):
        emotion = req.emotion if req.emotion in available else classify_emotion(req.text, available)
        ref = refs.get(emotion) or refs["neutral"]
        body: dict[str, Any] = {
            "text": req.text,
            "text_lang": req.text_lang,
            "ref_audio_path": ref["ref_audio_path"],
            "prompt_text": ref["prompt_text"],
            "prompt_lang": ref.get("prompt_lang", req.text_lang),
            "text_split_method": req.text_split_method,
            "batch_size": req.batch_size,
            "media_type": req.media_type,
            "streaming_mode": req.streaming_mode,
        }
        if req.extra:
            body.update(req.extra)

        try:
            upstream = requests.post(
                f"{gpt_sovits_api.rstrip('/')}/tts",
                json=body,
                timeout=180,
            )
        except requests.RequestException as exc:
            raise HTTPException(status_code=502, detail=f"GPT-SoVITS request failed: {exc}") from exc

        if upstream.status_code >= 400:
            raise HTTPException(status_code=upstream.status_code, detail=upstream.text)

        media_type = upstream.headers.get("content-type") or f"audio/{req.media_type}"
        return Response(content=upstream.content, media_type=media_type, headers={"X-Emotion": emotion})

    return app


def main() -> None:
    parser = argparse.ArgumentParser(description="Hermes-compatible emotion-to-reference adapter for GPT-SoVITS.")
    parser.add_argument("--refs", default=os.environ.get("EMOTION_REFS", "refs/emotion_refs.json"))
    parser.add_argument("--gpt-sovits-api", default=os.environ.get("GPT_SOVITS_API", "http://127.0.0.1:9883"))
    parser.add_argument("--host", default=os.environ.get("ADAPTER_HOST", "127.0.0.1"))
    parser.add_argument("--port", type=int, default=int(os.environ.get("ADAPTER_PORT", "9893")))
    args = parser.parse_args()

    app = create_app(Path(args.refs), args.gpt_sovits_api)
    uvicorn.run(app, host=args.host, port=args.port)


if __name__ == "__main__":
    main()
