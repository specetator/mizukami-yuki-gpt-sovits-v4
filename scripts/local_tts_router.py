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
    emotion: str = "neutral"
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


def create_app(refs_path: Path, gpt_sovits_api: str) -> FastAPI:
    refs = load_refs(refs_path)
    app = FastAPI(title="Local TTS Router", version="1.0.0")

    @app.get("/health")
    def health():
        return {
            "ok": True,
            "gpt_sovits_api": gpt_sovits_api,
            "emotions": sorted(refs.keys()),
        }

    @app.get("/emotions")
    def emotions():
        return refs

    @app.post("/tts")
    def tts(req: TTSRequest):
        emotion = req.emotion if req.emotion in refs else "neutral"
        ref = refs[emotion]
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
    parser = argparse.ArgumentParser(
        description="Local emotion-reference router for GPT-SoVITS. The caller supplies emotion; this service maps it to local reference audio."
    )
    parser.add_argument("--refs", default=os.environ.get("EMOTION_REFS", "refs/emotion_refs.json"))
    parser.add_argument("--gpt-sovits-api", default=os.environ.get("GPT_SOVITS_API", "http://127.0.0.1:9884"))
    parser.add_argument("--host", default=os.environ.get("ROUTER_HOST", "127.0.0.1"))
    parser.add_argument("--port", type=int, default=int(os.environ.get("ROUTER_PORT", "9883")))
    args = parser.parse_args()

    app = create_app(Path(args.refs), args.gpt_sovits_api)
    uvicorn.run(app, host=args.host, port=args.port)


if __name__ == "__main__":
    main()
