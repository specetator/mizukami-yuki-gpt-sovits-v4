import argparse
import csv
import math
import shutil
from pathlib import Path

import librosa
import numpy as np
import soundfile as sf


EMOTIONS = ["neutral", "happy", "soft", "sad", "angry", "surprised", "excited"]


def parse_list(path: Path):
    rows = []
    with path.open("r", encoding="utf-8-sig") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            parts = line.split("|", 3)
            if len(parts) != 4:
                continue
            wav_path, speaker, lang, text = parts
            rows.append(
                {
                    "wav_path": Path(wav_path),
                    "file": Path(wav_path).name,
                    "speaker": speaker,
                    "lang": lang,
                    "text": text.strip(),
                }
            )
    return rows


def audio_features(wav_path: Path):
    y, sr = sf.read(str(wav_path), always_2d=False)
    if y.ndim > 1:
        y = np.mean(y, axis=1)
    y = y.astype(np.float32)
    duration = len(y) / sr if sr else 0.0
    if len(y) == 0:
        return {}

    rms_frames = librosa.feature.rms(y=y, frame_length=1024, hop_length=256)[0]
    rms = float(np.sqrt(np.mean(np.square(y))) + 1e-9)
    rms_db = float(20 * math.log10(rms))
    peak = float(np.max(np.abs(y)) + 1e-9)
    crest = float(20 * math.log10(peak / rms))
    zcr = float(np.mean(librosa.feature.zero_crossing_rate(y, frame_length=1024, hop_length=256)[0]))
    centroid = float(np.mean(librosa.feature.spectral_centroid(y=y, sr=sr, n_fft=1024, hop_length=256)[0]))
    rms_dynamic = float(np.percentile(rms_frames, 90) - np.percentile(rms_frames, 10))

    try:
        f0 = librosa.yin(
            y,
            fmin=librosa.note_to_hz("C2"),
            fmax=librosa.note_to_hz("C7"),
            sr=sr,
            frame_length=1024,
            hop_length=256,
        )
    except Exception:
        f0 = np.array([])

    voiced = f0[np.isfinite(f0)] if len(f0) else np.array([])
    if len(voiced):
        lo, hi = np.percentile(voiced, [5, 95])
        voiced = voiced[(voiced >= lo) & (voiced <= hi)]
    if len(voiced):
        pitch_mean = float(np.mean(voiced))
        pitch_std = float(np.std(voiced))
        pitch_range = float(np.percentile(voiced, 90) - np.percentile(voiced, 10))
    else:
        pitch_mean = pitch_std = pitch_range = 0.0

    return {
        "duration": duration,
        "rms_db": rms_db,
        "crest_db": crest,
        "zcr": zcr,
        "centroid": centroid,
        "rms_dynamic": rms_dynamic,
        "pitch_mean": pitch_mean,
        "pitch_std": pitch_std,
        "pitch_range": pitch_range,
    }


def zscore(values):
    arr = np.array(values, dtype=np.float32)
    mean = float(np.mean(arr))
    std = float(np.std(arr) + 1e-6)
    return [(float(v) - mean) / std for v in values]


def text_flags(text: str):
    return {
        "exclaim": text.count("!") + text.count("！"),
        "question": text.count("?") + text.count("？"),
        "ellipsis": text.count("...") + text.count("…"),
        "long_vowel": text.count("ー"),
    }


def classify(rows):
    for row in rows:
        row.update(audio_features(row["wav_path"]))
        row.update(text_flags(row["text"]))
        row["chars_per_sec"] = len(row["text"]) / max(row["duration"], 0.1)

    for key in ["rms_db", "pitch_std", "pitch_range", "chars_per_sec", "rms_dynamic", "zcr", "centroid"]:
        zs = zscore([r.get(key, 0.0) for r in rows])
        for row, z in zip(rows, zs):
            row[f"{key}_z"] = z

    for row in rows:
        energy = row["rms_db_z"]
        pitch = max(row["pitch_std_z"], row["pitch_range_z"])
        rate = row["chars_per_sec_z"]
        dyn = row["rms_dynamic_z"]
        sharp = max(row["zcr_z"], row["centroid_z"])

        scores = {emotion: 0.0 for emotion in EMOTIONS}
        scores["neutral"] += 1.2 - 0.35 * abs(energy) - 0.35 * abs(pitch) - 0.25 * abs(rate)
        scores["soft"] += 0.8 - 0.45 * energy - 0.25 * sharp + 0.35 * row["ellipsis"]
        scores["sad"] += 0.35 - 0.35 * energy - 0.15 * rate + 0.25 * row["ellipsis"]
        scores["happy"] += 0.20 + 0.25 * energy + 0.45 * pitch + 0.25 * rate
        scores["angry"] += 0.10 + 0.50 * energy + 0.25 * sharp + 0.35 * rate + 0.35 * row["exclaim"]
        scores["surprised"] += 0.15 + 0.20 * energy + 0.60 * pitch + 0.75 * row["question"] + 0.20 * row["long_vowel"]
        scores["excited"] += 0.10 + 0.45 * energy + 0.45 * pitch + 0.40 * rate + 0.55 * row["exclaim"]

        if row["duration"] < 2.0 or row["duration"] > 15.0:
            for emotion in scores:
                scores[emotion] -= 0.25
        if dyn > 0.8:
            scores["excited"] += 0.15
            scores["angry"] += 0.10

        ranked = sorted(scores.items(), key=lambda item: item[1], reverse=True)
        best, best_score = ranked[0]
        second_score = ranked[1][1]
        confidence = 1 / (1 + math.exp(-(best_score - second_score)))
        confidence = max(0.50, min(0.95, 0.5 + (confidence - 0.5) * 1.5))

        row["suggested_emotion"] = best
        row["confidence"] = confidence
        row["second_choice"] = ranked[1][0]
        row["third_choice"] = ranked[2][0]
        row["notes"] = make_notes(row)

    return rows


def make_notes(row):
    notes = []
    if row["exclaim"]:
        notes.append("exclamation")
    if row["question"]:
        notes.append("question")
    if row["ellipsis"]:
        notes.append("ellipsis")
    if row["rms_db_z"] > 0.8:
        notes.append("louder than average")
    if row["rms_db_z"] < -0.8:
        notes.append("softer than average")
    if max(row["pitch_std_z"], row["pitch_range_z"]) > 0.8:
        notes.append("large pitch movement")
    if row["chars_per_sec_z"] > 0.8:
        notes.append("fast text rate")
    return "; ".join(notes) if notes else "balanced acoustic profile"


def write_outputs(rows, out_dir: Path):
    out_dir.mkdir(parents=True, exist_ok=True)
    for emotion in EMOTIONS:
        emotion_dir = out_dir / emotion
        emotion_dir.mkdir(exist_ok=True)
        for old_file in emotion_dir.glob("*.wav"):
            old_file.unlink()

    csv_path = out_dir / "emotion_candidates.csv"
    fieldnames = [
        "file",
        "suggested_emotion",
        "confidence",
        "second_choice",
        "third_choice",
        "text",
        "duration",
        "rms_db",
        "pitch_mean",
        "pitch_std",
        "pitch_range",
        "chars_per_sec",
        "notes",
        "wav_path",
    ]
    with csv_path.open("w", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            out = {key: row.get(key, "") for key in fieldnames}
            for key in ["confidence", "duration", "rms_db", "pitch_mean", "pitch_std", "pitch_range", "chars_per_sec"]:
                out[key] = f"{float(out[key]):.3f}"
            out["wav_path"] = str(row["wav_path"])
            writer.writerow(out)

            score = int(round(row["confidence"] * 100))
            dst = out_dir / row["suggested_emotion"] / f"{score}_{row['file']}"
            shutil.copy2(row["wav_path"], dst)

    summary_path = out_dir / "summary.txt"
    counts = {emotion: 0 for emotion in EMOTIONS}
    for row in rows:
        counts[row["suggested_emotion"]] += 1
    with summary_path.open("w", encoding="utf-8") as f:
        for emotion in EMOTIONS:
            f.write(f"{emotion}: {counts[emotion]}\n")

    return csv_path


def main():
    parser = argparse.ArgumentParser(description="Create emotion reference candidates from a GPT-SoVITS list.")
    parser.add_argument("--list", required=True, dest="list_path")
    parser.add_argument("--out-dir", required=True)
    args = parser.parse_args()

    rows = parse_list(Path(args.list_path))
    if not rows:
        raise SystemExit("No valid rows found in list file.")
    rows = classify(rows)
    csv_path = write_outputs(rows, Path(args.out_dir))
    print(csv_path)
    print("Use these as candidates only. Listen manually and choose one final clip per emotion.")


if __name__ == "__main__":
    main()
