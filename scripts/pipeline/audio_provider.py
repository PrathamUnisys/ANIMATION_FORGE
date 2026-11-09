#!/usr/bin/env python3
"""Audio provider interface: local-kokoro (proven) vs elevenlabs (stub/dry-run).
Contract: {duration, words[], phonemes[], visemes[]} + WAV + metadata, immutable cache.
Usage:
  python audio_provider.py --backend kokoro --text "Hello" --out PIPELINE/audio/test_line.wav
  python audio_provider.py --backend elevenlabs --text "Hello" --dry-run
"""
import argparse, json, sys, subprocess
from pathlib import Path

def ffprobe_duration(wav: Path):
    out = subprocess.run(
        ["ffprobe", "-v", "quiet", "-show_entries", "format=duration", "-of", "json", str(wav)],
        capture_output=True, text=True)
    try:
        d = json.loads(out.stdout)["format"]["duration"]
        return float(d)
    except Exception:
        return None

def kokoro(text: str, out: Path, voice: str = "af_heart"):
    venv_py = Path(r"D:\Work\ANIMATION_FORGE\.venv-kokoro-test\Scripts\python.exe")
    if not venv_py.exists():
        sys.exit(f"error: kokoro venv not found at {venv_py}")
    out.parent.mkdir(parents=True, exist_ok=True)
    code = f'''
from kokoro import KPipeline
import soundfile as sf
pipe = KPipeline(lang_code="a")
gen = pipe("{text.replace(chr(34), chr(39))}", voice="{voice}")
for _, _, audio in gen:
    sf.write(r"{out}", audio, 24000)
print("wrote", r"{out}")
'''
    r = subprocess.run([str(venv_py), "-c", code], capture_output=True, text=True, timeout=300)
    print(r.stdout[-2000:])
    if r.returncode not in (0,):
        print(r.stderr[-2000:], file=sys.stderr)
        sys.exit(f"error: kokoro failed exit {r.returncode}")
    dur = ffprobe_duration(out)
    contract = {"duration": dur, "words": text.split(), "phonemes": [], "visemes": [], "sample_rate": 24000, "backend": "local-kokoro", "voice": voice}
    meta_path = out.with_suffix(".json")
    meta_path.write_text(json.dumps(contract, indent=2))
    print(f"wrote {out} duration={dur} contract={meta_path}")
    return contract

def elevenlabs_dry_run(text: str):
    req = {"text": text, "model_id": "eleven_multilingual_v2", "output_format": "wav_48000", "voice_settings": {"stability": 0.5, "similarity_boost": 0.75}, "seed": 42, "optimize_streaming_latency": 0}
    print(json.dumps({"backend": "elevenlabs", "dry_run": True, "endpoint": "POST https://api.elevenlabs.io/v1/text-to-speech/{'{voice_id}'}", "request": req}, indent=2))
    print("No key required, no network call made. Pro tier required for WAV.")
    return req

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--backend", required=True, choices=["kokoro", "elevenlabs"])
    ap.add_argument("--text", required=True)
    ap.add_argument("--out", default="PIPELINE/audio/test_line.wav")
    ap.add_argument("--voice", default="af_heart")
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()
    if args.backend == "elevenlabs":
        if not args.dry_run:
            sys.exit("error: elevenlabs backend without --dry-run requires ELEVENLABS_API_KEY (not configured). Use --dry-run.")
        elevenlabs_dry_run(args.text)
    else:
        if args.dry_run:
            print("kokoro dry-run: would generate", args.text)
            return
        kokoro(args.text, Path(args.out), args.voice)

if __name__ == "__main__":
    main()
