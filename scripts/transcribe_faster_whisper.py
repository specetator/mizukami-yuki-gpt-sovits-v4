import argparse
from pathlib import Path

import torch
from faster_whisper import WhisperModel
from tqdm import tqdm


def main() -> None:
    parser = argparse.ArgumentParser(description="Transcribe wav files into GPT-SoVITS list format.")
    parser.add_argument("--input-dir", required=True)
    parser.add_argument("--output-list", required=True)
    parser.add_argument("--model-dir", required=True)
    parser.add_argument("--language", default="ja")
    parser.add_argument("--speaker", default="yuki")
    parser.add_argument("--precision", default="float16")
    args = parser.parse_args()

    input_dir = Path(args.input_dir)
    output_list = Path(args.output_list)
    files = sorted(input_dir.glob("*.wav"))
    if not files:
        raise SystemExit(f"No .wav files found in {input_dir}")

    device = "cuda" if torch.cuda.is_available() else "cpu"
    precision = args.precision
    if device == "cpu" and precision == "float16":
        precision = "int8"

    model = WhisperModel(args.model_dir, device=device, compute_type=precision)
    lines = []
    for wav in tqdm(files, desc="Transcribing"):
        segments, info = model.transcribe(
            str(wav),
            beam_size=5,
            vad_filter=True,
            vad_parameters={"min_silence_duration_ms": 700},
            language=args.language,
        )
        text = "".join(segment.text for segment in segments).strip()
        if not text:
            continue
        lang = (info.language or args.language).upper()
        lines.append(f"{wav.resolve()}|{args.speaker}|{lang}|{text}")

    output_list.parent.mkdir(parents=True, exist_ok=True)
    output_list.write_text("\n".join(lines), encoding="utf-8")
    print(f"Wrote {len(lines)} transcriptions to {output_list}")
    print("Important: manually correct transcript text before training or building prompt refs.")


if __name__ == "__main__":
    main()
