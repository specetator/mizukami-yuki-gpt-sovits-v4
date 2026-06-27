import argparse
import json
from pathlib import Path

import requests


def main() -> None:
    parser = argparse.ArgumentParser(description="Call GPT-SoVITS /tts using an emotion reference JSON file.")
    parser.add_argument("--api", default="http://127.0.0.1:9883")
    parser.add_argument("--emotion-json", required=True)
    parser.add_argument("--emotion", default="neutral")
    parser.add_argument("--text", required=True)
    parser.add_argument("--text-lang", default="ja")
    parser.add_argument("--out", default="output.wav")
    parser.add_argument("--split-method", default="cut5")
    args = parser.parse_args()

    refs_path = Path(args.emotion_json)
    refs = json.loads(refs_path.read_text(encoding="utf-8"))
    if args.emotion not in refs:
        raise SystemExit(f"Emotion {args.emotion!r} not found. Available: {', '.join(refs)}")
    ref = refs[args.emotion]
    ref_audio_path = Path(ref["ref_audio_path"])
    if not ref_audio_path.is_absolute():
        ref_audio_path = (refs_path.resolve().parent / ref_audio_path).resolve()

    body = {
        "text": args.text,
        "text_lang": args.text_lang,
        "ref_audio_path": str(ref_audio_path),
        "prompt_text": ref["prompt_text"],
        "prompt_lang": ref.get("prompt_lang", args.text_lang),
        "text_split_method": args.split_method,
        "batch_size": 1,
        "media_type": "wav",
        "streaming_mode": False,
    }

    response = requests.post(f"{args.api.rstrip('/')}/tts", json=body, timeout=180)
    response.raise_for_status()
    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_bytes(response.content)
    print(f"Saved {out}")


if __name__ == "__main__":
    main()
