#!/usr/bin/env python3
"""T09: score one media file and append a scorecard row.
Usage:
  python score.py --media PIPELINE/BAKEOFF/T15_frames/T15_f0007.png --shot S1 --track T1A [--wall-min 8 --notes "EEVEE proof"]
Metrics via ffprobe (duration, fps, resolution). Appends to PIPELINE/BAKEOFF/scorecard.json rows.
Does NOT overwrite rows; appends with measured_at timestamp.
"""
import argparse, json, pathlib, subprocess

def ffprobe(path: str) -> dict:
    out = subprocess.run(
        ["ffprobe", "-v", "quiet", "-show_entries", "format=duration", "-show_entries", "stream=width,height,r_frame_rate,codec_name", "-of", "json", str(path)],
        capture_output=True, text=True)
    try:
        d = json.loads(out.stdout)
        fmt = d.get("format", {})
        st = (d.get("streams") or [{}])[0]
        return {"duration": float(fmt.get("duration", 0) or 0), "width": st.get("width"), "height": st.get("height"), "fps": st.get("r_frame_rate"), "codec": st.get("codec_name")}
    except Exception as e:
        return {"error": str(e), "raw": out.stdout[:500]}

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--media", required=True)
    ap.add_argument("--shot", required=True, help="S1 or S2")
    ap.add_argument("--track", required=True, help="T1A T1B T2 T3 TE")
    ap.add_argument("--wall-min", type=float, default=None)
    ap.add_argument("--ram-mb", type=int, default=None)
    ap.add_argument("--vram-mb", type=int, default=None)
    ap.add_argument("--scores", default="{}", help="JSON object criterion->1..5, e.g. '{\"consistency\":4,\"motion\":3}'")
    ap.add_argument("--notes", default="")
    args = ap.parse_args()

    metrics = ffprobe(args.media)
    print(json.dumps({"media": args.media, "metrics": metrics}, indent=2))

    scorecard_path = pathlib.Path("PIPELINE/BAKEOFF/scorecard.json")
    d = json.loads(scorecard_path.read_text())
    scores = json.loads(args.scores)
    total = None
    if scores:
        weights = {c["id"]: c["weight"] for c in d["criteria"]}
        total = round(sum(scores.get(k, 0) / 5 * w for k, w in weights.items() if k in scores), 1)

    row = {
        "shot": args.shot,
        "track": args.track,
        "scores": scores,
        "total": total,
        "kept_takes": None,
        "total_takes": None,
        "wall_clock_min": args.wall_min,
        "peak_ram_mb": args.ram_mb,
        "peak_vram_mb": args.vram_mb,
        "metrics": metrics,
        "artifacts": [args.media],
        "notes": args.notes,
        "measured_at": "2026-11-09",
    }
    d["rows"].append(row)
    scorecard_path.write_text(json.dumps(d, indent=2))
    print(f"appended scorecard row #{len(d['rows'])} total={total}")

if __name__ == "__main__":
    main()
