#!/usr/bin/env python3
"""T13 verification: import a VRM headless and report rig facts.
Run with:
  blender.exe --background --factory-startup --python vrm_inspect.py -- --file <vrm> --out <json>
Requires the `vrm` add-on (4.10.4) to be enabled in the Blender user config.
Note: --factory-startup disables user add-ons, so this script re-enables `vrm` in-process if present.
"""
import bpy, addon_utils, json, sys, os, argparse

argv = sys.argv[sys.argv.index("--") + 1:]
ap = argparse.ArgumentParser()
ap.add_argument("--file", required=True)
ap.add_argument("--out", required=True)
ap.add_argument("--save", default="")
args = ap.parse_args(argv)

# Clear scene manually (do NOT use read_factory_settings: it wipes addon prefs)
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)
# Enable vrm extension addon (Blender 5 extension module name)
try:
    mod = addon_utils.enable("bl_ext.blender_org.vrm")
    print(f"[T13] vrm addon enabled: {mod}")
except Exception as e:
    print(f"[T13] addon_enable warning: {e}")

# Import VRM (operator varies by version; try standard)
imported = False
for op_name in ("import_scene.vrm", "wm.vrm_import", "import_scene.vrm_import"):
    try:
        op = getattr(bpy.ops, op_name.split(".")[0]).__getattribute__(op_name.split(".")[1])
        op(filepath=args.file)
        imported = True
        print(f"[T13] imported via {op_name}")
        break
    except Exception as e:
        print(f"[T13] {op_name} failed: {e}")

if not imported:
    # Fallback: use wm.vrm_import from addon
    try:
        bpy.ops.wm.vrm_import(filepath=args.file)
        imported = True
        print("[T13] imported via wm.vrm_import fallback")
    except Exception as e:
        print(f"[T13] FATAL: all import operators failed: {e}")
        sys.exit(1)

# Gather facts
armatures = [o for o in bpy.context.scene.objects if o.type == 'ARMATURE']
result = {
    "status": "ok",
    "file": args.file,
    "armature_count": len(armatures),
    "armatures": [],
    "total_bones": 0,
    "expression_names": [],
    "has_aa_ih_ou_ee_oh": {},
    "has_blink": False,
    "spring_bone_count": 0,
    "shape_key_objects": [],
}

for arm in armatures:
    bones = list(arm.data.bones) if arm.data else []
    result["armatures"].append({
        "name": arm.name,
        "bone_count": len(bones),
        "bones": sorted([b.name for b in bones])[:80],
    })
    result["total_bones"] += len(bones)

# Shape keys (VRM expressions become shape keys on mesh objects)
expr_names = set()
for obj in bpy.context.scene.objects:
    if obj.type == 'MESH' and obj.data and obj.data.shape_keys:
        sb = obj.data.shape_keys
        result["shape_key_objects"].append({"object": obj.name, "shape_keys": sorted([k.name for k in sb.key_blocks])})
        for kb in sb.key_blocks:
            expr_names.add(kb.name)

result["expression_names"] = sorted(expr_names)
# VRChat/VRM0 naming: Fcl_MTH_A/I/U/E/O map to VRM1 aa/ih/ou/ee/oh
vowel_map = {
    "aa": ("aa", "fcl_mth_a"),
    "ih": ("ih", "fcl_mth_i"),
    "ou": ("ou", "fcl_mth_u"),
    "ee": ("ee", "fcl_mth_e"),
    "oh": ("oh", "fcl_mth_o"),
}
for vowel, needles in vowel_map.items():
    result["has_aa_ih_ou_ee_oh"][vowel] = any(n in e.lower() for e in expr_names for n in needles)
result["has_blink"] = any("blink" in n.lower() or n.lower() in ("fcl_eye_close",) or "eye_close" in n.lower() for n in expr_names)

# SpringBone: VRM hair/spring bones + addon metadata, not just constraints
sb_count = 0
spring_bones = []
for arm in armatures:
    if arm.data:
        for b in arm.data.bones:
            bl = b.name.lower()
            if "hair" in bl or "spring" in bl or "transferable" in bl:
                spring_bones.append(b.name)
for obj in bpy.context.scene.objects:
    for c in getattr(obj, "constraints", []):
        if "spring" in c.type.lower() or "spring" in c.name.lower():
            sb_count += 1
result["spring_bone_count"] = sb_count
result["spring_bones_sample"] = spring_bones[:20]

print(json.dumps(result, indent=2))
os.makedirs(os.path.dirname(os.path.abspath(args.out)), exist_ok=True)
with open(args.out, "w", encoding="utf-8") as f:
    json.dump(result, f, indent=2, ensure_ascii=False)
print(f"[T13] wrote {args.out}")

if args.save:
    bpy.ops.wm.save_as_mainfile(filepath=args.save)
    print(f"[T13] saved {args.save}")
