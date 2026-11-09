#!/usr/bin/env python3
"""T08: Rhubarb mouth cues -> VRM expression weights.
IMPORTANT: Rhubarb's 9 shapes (A, C, E, F, B, G, H, X) are NOT 1:1 with VRM's 5 vowels.
This script documents and implements the phoneme-based mapping, not name matching.
Usage:
  python align_to_visemes.py --rhubarb PIPELINE/audio/test_line_rhubarb.json --out PIPELINE/audio/test_line_visemes.json
"""
import argparse, json
from pathlib import Path

# Rhubarb -> VRM5 target weights. Based on phonetic groups, not letter names.
# A = open vowel (aa), C = closed/teeth (ih+ee blend), E = mid-front (ee), F = labial (ou/oh blend), B = closed (silence-ish), G/H/X = misc/closed
RHUBARB_TO_VRM5 = {
    "A": {"aa": 1.0},
    "C": {"ih": 0.7, "ee": 0.3},
    "E": {"ee": 0.8, "ih": 0.2},
    "F": {"ou": 0.6, "oh": 0.4},
    "B": {},
    "G": {"aa": 0.2},
    "H": {"ih": 0.5, "ee": 0.5},
    "X": {},
}
# Map VRM1 names to the Fcl_MTH_* shape-key names found in RedHairGirl.vrm (T13)
VRM1_TO_FCL = {"aa": "Fcl_MTH_A", "ih": "Fcl_MTH_I", "ou": "Fcl_MTH_U", "ee": "Fcl_MTH_E", "oh": "Fcl_MTH_O"}

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--rhubarb", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--fps", type=int, default=24)
    args = ap.parse_args()
    d = json.loads(Path(args.rhubarb).read_text())
    cues = d["mouthCues"]
    duration = d["metadata"]["duration"]
    frames = round(duration * args.fps)
    print(f"duration={duration}s cues={len(cues)} frames={frames} @ {args.fps}fps")
    keyframes = []
    for cue in cues:
        weights = RHUBARB_TO_VRM5.get(cue["value"], {})
        fcl = {VRM1_TO_FCL[k]: v for k, v in weights.items()}
        keyframes.append({"start": cue["start"], "end": cue["end"], "frame": round(cue["start"] * args.fps), "rhubarb": cue["value"], "vrm5": weights, "fcl_weights": fcl})
    out = {"duration_s": duration, "fps": args.fps, "frames": frames, "mapping": "rhubarb9->vrm5 (phoneme-based, not 1:1)", "keyframes": keyframes}
    Path(args.out).write_text(json.dumps(out, indent=2))
    print(f"wrote {args.out} ({len(keyframes)} keyframes, {frames} frames total)")

if __name__ == "__main__":
    main()
