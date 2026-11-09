"""T15 Blender: drive VRM mouth from viseme keyframes, render proof frames.
Run: blender.exe --background --python mouth_drive.py -- --blend T13_redhairgirl.blend --visemes test_line_visemes.json --outdir PIPELINE/BAKEOFF/T15_frames
"""
import bpy, addon_utils, json, sys, os, argparse
addon_utils.enable("bl_ext.blender_org.vrm")

argv = sys.argv[sys.argv.index("--") + 1:]
ap = argparse.ArgumentParser()
ap.add_argument("--blend", required=True)
ap.add_argument("--visemes", required=True)
ap.add_argument("--outdir", required=True)
args = ap.parse_args(argv)

bpy.ops.wm.open_mainfile(filepath=args.blend)
vis = json.loads(open(args.visemes, encoding="utf-8").read())
os.makedirs(args.outdir, exist_ok=True)

# Find Face object with shape keys
face = bpy.data.objects.get("Face")
if face is None or not face.data.shape_keys:
    raise SystemExit("Face object with shape keys not found")
kb_by_name = {kb.name: kb for kb in face.data.shape_keys.key_blocks}

# Apply mouth keyframes
for kf in vis["keyframes"]:
    for fcl_name, w in kf["fcl_weights"].items():
        kb = kb_by_name.get(fcl_name)
        if kb is None:
            continue
        kb.value = w
        kb.keyframe_insert(data_path="value", frame=int(kf["frame"]))
    # neutral beat at next cue to avoid holding
for kf in vis["keyframes"]:
    for fcl_name in ("Fcl_MTH_A", "Fcl_MTH_I", "Fcl_MTH_U", "Fcl_MTH_E", "Fcl_MTH_O"):
        kb = kb_by_name.get(fcl_name)
        if kb:
            kb.value = 0.0
            kb.keyframe_insert(data_path="value", frame=int(kf["frame"]) + 2)

# --- Procedural blink (Fcl_EYE_Close): short dip every ~3s, double-blink occasionally ---
import random
random.seed(7)
blink_frames = list(range(20, vis["frames"], 72)) + [random.randint(30, vis["frames"] - 5)]
for f in blink_frames:
    for name in ("Fcl_EYE_Close", "Fcl_EYE_Close_L", "Fcl_EYE_Close_R"):
        kb = kb_by_name.get(name)
        if kb:
            kb.value = 1.0
            kb.keyframe_insert(data_path="value", frame=int(f))
            kb.value = 0.0
            kb.keyframe_insert(data_path="value", frame=int(f) + 3)

# --- Subtle head micro-motion on the head bone (prevents uncanny stillness) ---
scene = bpy.context.scene
arm = next((o for o in scene.objects if o.type == 'ARMATURE'), None)
if arm:
    head_bone = None
    for b in arm.data.bones:
        if "head" in b.name.lower():
            head_bone = b
            break
    if head_bone:
        import math
        for f in range(1, vis["frames"] + 1, 6):
            sx = 0.02 * math.sin(f * 0.35)
            sy = 0.015 * math.sin(f * 0.22 + 1.3)
            pb = arm.pose.bones.get(head_bone.name)
            if pb:
                pb.rotation_mode = 'XYZ'
                pb.rotation_euler = (sy, sx, 0)
                pb.keyframe_insert(data_path="rotation_euler", frame=f)

# Set scene for render
try:
    scene.render.engine = 'BLENDER_EEVEE'
except Exception as e:
    print(f"engine fallback: {e}")
scene.render.resolution_x = 640
scene.render.resolution_y = 640
scene.render.image_settings.file_format = 'PNG'
scene.frame_start = 1
scene.frame_end = vis["frames"]
scene.render.film_transparent = False

# Camera: close-up on head for facial proof
cam_data = None
for o in scene.objects:
    if o.type == 'CAMERA':
        cam_data = o
        break
if cam_data is None:
    cam_data = bpy.data.objects.new("Cam", bpy.data.cameras.new("Cam"))
    scene.collection.objects.link(cam_data)
    scene.camera = cam_data
# VRM origin is at feet; head ~1.55m. Frame head tightly.
cam_data.location = (0, -0.55, 1.55)
cam_data.rotation_euler = (1.5708, 0, 0)  # look +Y (toward character face)
cam_data.data.lens = 50

# Light
light_data = bpy.data.lights.new("Sun", 'SUN')
light_data.energy = 3.0
light_obj = bpy.data.objects.new("Sun", light_data)
light_obj.location = (1, -1, 3)
scene.collection.objects.link(light_obj)

# Render a few proof frames where mouth is open
proof_frames = [kf["frame"] for kf in vis["keyframes"] if kf["fcl_weights"]][:4]
print(f"[T15] proof frames: {proof_frames}")
for f in proof_frames:
    scene.frame_set(f)
    out = os.path.join(os.path.abspath(args.outdir), f"T15_f{f:04d}.png")
    scene.render.filepath = out
    bpy.ops.render.render(write_still=True)
    print(f"[T15] rendered {out}")

print(f"[T15] DONE frames={vis['frames']} keyframes={len(vis['keyframes'])}")
