import argparse
import csv
import json
import subprocess
from pathlib import Path


EMOTIONS = ["neutral", "happy", "soft", "sad", "angry", "surprised", "excited"]


def run_ffmpeg(ffmpeg: str, src: Path, dst: Path) -> None:
    dst.parent.mkdir(parents=True, exist_ok=True)
    cmd = [
        ffmpeg,
        "-hide_banner",
        "-y",
        "-i",
        str(src),
        "-ac",
        "1",
        "-ar",
        "32000",
        "-c:a",
        "pcm_s16le",
        str(dst),
    ]
    subprocess.run(cmd, check=True)


def read_prompt_csv(path: Path):
    with path.open("r", encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)
        rows = list(reader)
    prompts = {}
    for row in rows:
        emotion = row.get("emotion", "").strip()
        if not emotion:
            continue
        prompts[emotion] = {
            "ref_audio_path": row.get("ref_audio_path", "").strip(),
            "prompt_lang": row.get("prompt_lang", "ja").strip() or "ja",
            "prompt_text": row.get("prompt_text", "").strip(),
        }
    return prompts


def main() -> None:
    parser = argparse.ArgumentParser(description="Convert selected emotion clips and generate emotion_refs.json/csv.")
    parser.add_argument("--prompt-csv", required=True, help="CSV with emotion,ref_audio_path,prompt_lang,prompt_text")
    parser.add_argument("--out-dir", required=True)
    parser.add_argument("--ffmpeg", default="ffmpeg")
    parser.add_argument("--skip-convert", action="store_true")
    args = parser.parse_args()

    prompt_csv = Path(args.prompt_csv)
    out_dir = Path(args.out_dir)
    selected_dir = out_dir / "selected"
    prompts = read_prompt_csv(prompt_csv)

    missing = [emotion for emotion in EMOTIONS if emotion not in prompts]
    if missing:
        raise SystemExit(f"Missing emotions in CSV: {', '.join(missing)}")

    refs = {}
    csv_rows = []
    for emotion in EMOTIONS:
        item = prompts[emotion]
        src = Path(item["ref_audio_path"])
        if not src.exists():
            raise SystemExit(f"Reference audio does not exist for {emotion}: {src}")
        if not item["prompt_text"]:
            raise SystemExit(f"prompt_text is empty for {emotion}; manually correct ASR first.")

        dst = selected_dir / f"{emotion}.wav"
        if args.skip_convert:
            dst = src
        else:
            run_ffmpeg(args.ffmpeg, src, dst)

        refs[emotion] = {
            "ref_audio_path": str(dst.resolve()),
            "prompt_lang": item["prompt_lang"],
            "prompt_text": item["prompt_text"],
        }
        csv_rows.append(
            {
                "emotion": emotion,
                "ref_audio_path": refs[emotion]["ref_audio_path"],
                "prompt_lang": refs[emotion]["prompt_lang"],
                "prompt_text": refs[emotion]["prompt_text"],
            }
        )

    out_dir.mkdir(parents=True, exist_ok=True)
    json_path = out_dir / "emotion_refs.json"
    csv_path = out_dir / "emotion_refs.csv"
    json_path.write_text(json.dumps(refs, ensure_ascii=False, indent=2), encoding="utf-8")
    with csv_path.open("w", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=["emotion", "ref_audio_path", "prompt_lang", "prompt_text"])
        writer.writeheader()
        writer.writerows(csv_rows)

    print(f"Wrote {json_path}")
    print(f"Wrote {csv_path}")


if __name__ == "__main__":
    main()
