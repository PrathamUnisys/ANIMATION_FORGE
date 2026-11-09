#!/usr/bin/env python3
"""Shot and take manifest for the Animation Forge V2 pipeline.

The V1 pipeline produced a single pass with no record of what was tried, what was
rejected, or which take was kept. This module is the missing bookkeeping: every shot
has a route, every attempt is a numbered take with a verdict, and exactly one take can
be selected.

Standard library only — it must run inside the repo venv with no extra installs.

Usage
-----
    python scripts/pipeline/shot_manifest.py new \
        --project PROJECT_001 --shot S001 --title "Warrior line" \
        --route rig --character RedHairGirl --duration 5

    python scripts/pipeline/shot_manifest.py list
    python scripts/pipeline/shot_manifest.py take-add --shot S001 --path renders/S001_t1.mov
    python scripts/pipeline/shot_manifest.py take-verdict --shot S001 --take 1 --verdict keep
    python scripts/pipeline/shot_manifest.py select --shot S001 --take 1
    python scripts/pipeline/shot_manifest.py advance --shot S001 --to review
    python scripts/pipeline/shot_manifest.py status
    python scripts/pipeline/shot_manifest.py validate

Manifest location: PIPELINE/shots/manifest.json (created on first use).
"""

from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

SCHEMA_VERSION = "1.0.0"
FPS = 24

ROUTES = ("projection", "rig", "prop", "atmosphere")
SHOT_STATUSES = ("planned", "in_progress", "review", "approved", "rejected")
TAKE_VERDICTS = ("pending", "keep", "reject")

REPO_ROOT = Path(__file__).resolve().parents[2]
MANIFEST_PATH = REPO_ROOT / "PIPELINE" / "shots" / "manifest.json"


# --------------------------------------------------------------------------- io
def _now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def load() -> dict:
    if not MANIFEST_PATH.exists():
        return {"schema_version": SCHEMA_VERSION, "updated": _now(), "projects": {}}
    with MANIFEST_PATH.open("r", encoding="utf-8") as fh:
        return json.load(fh)


def save(manifest: dict) -> None:
    MANIFEST_PATH.parent.mkdir(parents=True, exist_ok=True)
    manifest["updated"] = _now()
    tmp = MANIFEST_PATH.with_suffix(".json.tmp")
    with tmp.open("w", encoding="utf-8") as fh:
        json.dump(manifest, fh, indent=2, ensure_ascii=False)
        fh.write("\n")
    tmp.replace(MANIFEST_PATH)


# ----------------------------------------------------------------------- lookups
def find_shot(manifest: dict, shot_id: str) -> tuple[dict, dict]:
    """Return (project, shot). Raises SystemExit with a helpful message if missing."""
    matches = [
        (pid, shot)
        for pid, project in manifest["projects"].items()
        for shot in project["shots"]
        if shot["id"] == shot_id
    ]
    if not matches:
        sys.exit(f"error: shot '{shot_id}' not found. Use 'list' to see known shots.")
    if len(matches) > 1:
        owners = ", ".join(pid for pid, _ in matches)
        sys.exit(f"error: shot id '{shot_id}' is ambiguous across projects: {owners}")
    pid, shot = matches[0]
    return manifest["projects"][pid], shot


def require_project(manifest: dict, project_id: str) -> dict:
    project = manifest["projects"].get(project_id)
    if project is None:
        sys.exit(
            f"error: project '{project_id}' not found. "
            f"Known: {', '.join(manifest['projects']) or '(none)'}"
        )
    return project


# ---------------------------------------------------------------------- commands
def cmd_new(args: argparse.Namespace) -> int:
    if args.route not in ROUTES:
        sys.exit(f"error: --route must be one of {ROUTES}")
    manifest = load()
    project = manifest["projects"].setdefault(
        args.project, {"title": args.project, "created": _now(), "shots": []}
    )
    if any(s["id"] == args.shot for s in project["shots"]):
        sys.exit(f"error: shot '{args.shot}' already exists in {args.project}")

    duration = float(args.duration)
    frames = round(duration * FPS)
    shot = {
        "id": args.shot,
        "title": args.title,
        "route": args.route,
        "character": args.character,
        "duration_s": duration,
        "fps": FPS,
        "frames": frames,
        "status": "planned",
        "audio": None,
        "takes": [],
        "selected_take": None,
        "created": _now(),
        "updated": _now(),
    }
    project["shots"].append(shot)
    save(manifest)
    print(f"created {args.project}/{args.shot}  route={args.route}  "
          f"{duration}s = {frames} frames @ {FPS}fps")
    return 0


def cmd_list(args: argparse.Namespace) -> int:
    manifest = load()
    if not manifest["projects"]:
        print("manifest is empty — create a shot with 'new'")
        return 0

    for pid, project in manifest["projects"].items():
        if args.project and pid != args.project:
            continue
        print(f"\n{pid}  ({len(project['shots'])} shots)")
        if not project["shots"]:
            print("  (no shots)")
            continue
        print(f"  {'SHOT':<8} {'ROUTE':<11} {'STATUS':<12} {'TAKES':<6} {'SEL':<4} TITLE")
        for shot in project["shots"]:
            if args.status and shot["status"] != args.status:
                continue
            sel = shot["selected_take"] if shot["selected_take"] is not None else "-"
            print(
                f"  {shot['id']:<8} {shot['route']:<11} {shot['status']:<12} "
                f"{len(shot['takes']):<6} {sel:<4} {shot['title']}"
            )
    return 0


def cmd_show(args: argparse.Namespace) -> int:
    _, shot = find_shot(load(), args.shot)
    print(json.dumps(shot, indent=2, ensure_ascii=False))
    return 0


def cmd_take_add(args: argparse.Namespace) -> int:
    if args.verdict not in TAKE_VERDICTS:
        sys.exit(f"error: --verdict must be one of {TAKE_VERDICTS}")
    manifest = load()
    _, shot = find_shot(manifest, args.shot)

    take = {
        "index": len(shot["takes"]) + 1,
        "path": args.path,
        "verdict": args.verdict,
        "wall_clock_min": args.minutes,
        "peak_ram_mb": args.ram_mb,
        "peak_vram_mb": args.vram_mb,
        "notes": args.notes or "",
        "added": _now(),
    }
    shot["takes"].append(take)
    if shot["status"] == "planned":
        shot["status"] = "in_progress"
    shot["updated"] = _now()
    save(manifest)
    print(f"{args.shot}: added take {take['index']} ({args.verdict}) -> {args.path}")
    return 0


def cmd_take_verdict(args: argparse.Namespace) -> int:
    if args.verdict not in TAKE_VERDICTS:
        sys.exit(f"error: --verdict must be one of {TAKE_VERDICTS}")
    manifest = load()
    _, shot = find_shot(manifest, args.shot)
    take = next((t for t in shot["takes"] if t["index"] == args.take), None)
    if take is None:
        sys.exit(f"error: {args.shot} has no take {args.take}")
    take["verdict"] = args.verdict
    shot["updated"] = _now()
    save(manifest)
    print(f"{args.shot}: take {args.take} -> {args.verdict}")
    return 0


def cmd_select(args: argparse.Namespace) -> int:
    manifest = load()
    _, shot = find_shot(manifest, args.shot)
    take = next((t for t in shot["takes"] if t["index"] == args.take), None)
    if take is None:
        sys.exit(f"error: {args.shot} has no take {args.take}")
    if take["verdict"] == "reject":
        sys.exit(f"error: take {args.take} is marked reject; cannot select it")
    shot["selected_take"] = args.take
    shot["status"] = "review"
    shot["updated"] = _now()
    save(manifest)
    print(f"{args.shot}: selected take {args.take}")
    return 0


def cmd_advance(args: argparse.Namespace) -> int:
    if args.to not in SHOT_STATUSES:
        sys.exit(f"error: --to must be one of {SHOT_STATUSES}")
    manifest = load()
    _, shot = find_shot(manifest, args.shot)

    # Guard rails: the pipeline's whole point is that nothing is approved without a take.
    if args.to == "approved" and shot["selected_take"] is None:
        sys.exit(f"error: {args.shot} cannot be approved without a selected take")
    if args.to == "review" and not shot["takes"]:
        sys.exit(f"error: {args.shot} cannot enter review with no takes")

    previous = shot["status"]
    shot["status"] = args.to
    shot["updated"] = _now()
    save(manifest)
    print(f"{args.shot}: {previous} -> {args.to}")
    return 0


def cmd_status(args: argparse.Namespace) -> int:
    manifest = load()
    totals: dict[str, int] = {s: 0 for s in SHOT_STATUSES}
    takes = 0
    kept = 0
    for project in manifest["projects"].values():
        for shot in project["shots"]:
            totals[shot["status"]] = totals.get(shot["status"], 0) + 1
            takes += len(shot["takes"])
            kept += sum(1 for t in shot["takes"] if t["verdict"] == "keep")

    total_shots = sum(totals.values())
    print(f"projects : {len(manifest['projects'])}")
    print(f"shots    : {total_shots}")
    for status in SHOT_STATUSES:
        if totals.get(status):
            print(f"  {status:<12} {totals[status]}")
    print(f"takes    : {takes}  (kept {kept}, reject rate "
          f"{(0 if not takes else round(100 * (takes - kept) / takes))}%)")
    return 0


def cmd_validate(args: argparse.Namespace) -> int:
    manifest = load()
    problems: list[str] = []
    for pid, project in manifest["projects"].items():
        seen: set[str] = set()
        for shot in project["shots"]:
            if shot["id"] in seen:
                problems.append(f"{pid}: duplicate shot id {shot['id']}")
            seen.add(shot["id"])
            if shot["route"] not in ROUTES:
                problems.append(f"{pid}/{shot['id']}: bad route {shot['route']}")
            if shot["status"] not in SHOT_STATUSES:
                problems.append(f"{pid}/{shot['id']}: bad status {shot['status']}")
            if round(shot["duration_s"] * shot["fps"]) != shot["frames"]:
                problems.append(
                    f"{pid}/{shot['id']}: frames {shot['frames']} != "
                    f"round({shot['duration_s']} * {shot['fps']})"
                )
            if shot["selected_take"] is not None:
                if not any(t["index"] == shot["selected_take"] for t in shot["takes"]):
                    problems.append(
                        f"{pid}/{shot['id']}: selected_take {shot['selected_take']} does not exist"
                    )
            if shot["status"] == "approved" and shot["selected_take"] is None:
                problems.append(f"{pid}/{shot['id']}: approved without a selected take")

    if problems:
        print("INVALID:")
        for p in problems:
            print(f"  - {p}")
        return 1
    print(f"OK: {MANIFEST_PATH} ({len(manifest['projects'])} projects)")
    return 0


# ------------------------------------------------------------------------ parser
def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Animation Forge shot/take manifest",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    sub = parser.add_subparsers(dest="command", required=True)

    p = sub.add_parser("new", help="create a shot")
    p.add_argument("--project", required=True)
    p.add_argument("--shot", required=True, help="shot id, e.g. S001")
    p.add_argument("--title", required=True)
    p.add_argument("--route", required=True, help=f"one of {ROUTES}")
    p.add_argument("--character", default="")
    p.add_argument("--duration", default="5", help="seconds (default 5)")
    p.set_defaults(func=cmd_new)

    p = sub.add_parser("list", help="list shots")
    p.add_argument("--project", default=None)
    p.add_argument("--status", default=None)
    p.set_defaults(func=cmd_list)

    p = sub.add_parser("show", help="show one shot as JSON")
    p.add_argument("--shot", required=True)
    p.set_defaults(func=cmd_show)

    p = sub.add_parser("take-add", help="record a take")
    p.add_argument("--shot", required=True)
    p.add_argument("--path", required=True)
    p.add_argument("--verdict", default="pending")
    p.add_argument("--minutes", type=float, default=None, help="wall clock minutes")
    p.add_argument("--ram-mb", type=int, default=None)
    p.add_argument("--vram-mb", type=int, default=None)
    p.add_argument("--notes", default="")
    p.set_defaults(func=cmd_take_add)

    p = sub.add_parser("take-verdict", help="set a take verdict")
    p.add_argument("--shot", required=True)
    p.add_argument("--take", type=int, required=True)
    p.add_argument("--verdict", required=True)
    p.set_defaults(func=cmd_take_verdict)

    p = sub.add_parser("select", help="select the keeper take")
    p.add_argument("--shot", required=True)
    p.add_argument("--take", type=int, required=True)
    p.set_defaults(func=cmd_select)

    p = sub.add_parser("advance", help="move a shot to another status")
    p.add_argument("--shot", required=True)
    p.add_argument("--to", required=True, help=f"one of {SHOT_STATUSES}")
    p.set_defaults(func=cmd_advance)

    p = sub.add_parser("status", help="summary counts")
    p.set_defaults(func=cmd_status)

    p = sub.add_parser("validate", help="check manifest integrity")
    p.set_defaults(func=cmd_validate)

    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
