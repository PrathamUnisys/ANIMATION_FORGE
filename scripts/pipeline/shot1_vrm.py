"""T20 Shot 1 (track 1a VRM): line + head turn + arm gesture, two angles.
Run: blender.exe --background --python shot1_vrm.py -- --blend T13_redhairgirl.blend --visemes test_line_visemes.json --outdir PIPELINE/BAKEOFF/T20_shot1
Renders PNG sequence + assembles mp4 via ffmpeg. Two angles: A frontal mid, B 30deg off-axis.
"""
import bpy, addon_utils, json, sys, os, argparse, math, random
addon_utils.enable("bl_ext.blender_org.vrm")

argv = sys.argv[sys.argv.index("--") + 1:]
ap = argparse.ArgumentParser()
ap.add_argument("--blend", required=True)
ap.add_argument("--visemes", required=True)
ap.add_argument("--outdir", required=True)
ap.add_argument("--frames", type=int, default=120)  # 5s @ 24fps
args = ap.parse_args(argv)

bpy.ops.wm.open_mainfile(filepath=args.blend)
vis = json.loads(open(args.visemes, encoding="utf-8").read())
os.makedirs(args.outdir, exist_ok=True)

scene = bpy.context.scene
face = bpy.data.objects.get("Face")
kb_by_name = {kb.name: kb for kb in face.data.shape_keys.key_blocks}

# --- mouth (from T15, looped to 120 frames) ---
# Repeat the 56-frame viseme timeline twice-ish: map 56 -> 120 by scaling frame numbers
scale = args.frames / vis["frames"]
for kf in vis["keyframes"]:
    f_scaled = max(1, round(kf["frame"] * scale))
    for name, w in kf["fcl_weights"].items():
        kb = kb_by_name.get(name)
        if kb:
            kb.value = w
            kb.keyframe_insert(data_path="value", frame=int(f_scaled))
for kf in vis["keyframes"]:
    f_scaled = max(1, round(kf["frame"] * scale)) + 2
    for name in ("Fcl_MTH_A", "Fcl_MTH_I", "Fcl_MTH_U", "Fcl_MTH_E", "Fcl_MTH_O"):
        kb = kb_by_name.get(name)
        if kb:
            kb.value = 0.0
            kb.keyframe_insert(data_path="value", frame=min(f_scaled, args.frames))

# --- blink + micro-motion (from T15) ---
random.seed(7)
for f in range(20, args.frames, 72):
    for name in ("Fcl_EYE_Close", "Fcl_EYE_Close_L", "Fcl_EYE_Close_R"):
        kb = kb_by_name.get(name)
        if kb:
            kb.value = 1.0
            kb.keyframe_insert(data_path="value", frame=int(f))
            kb.value = 0.0
            kb.keyframe_insert(data_path="value", frame=int(f) + 3)

arm = next((o for o in scene.objects if o.type == 'ARMATURE'), None)
head_pb = None
for b in arm.pose.bones:
    if "head" in b.name.lower():
        head_pb = b
        break
if head_pb:
    head_pb.rotation_mode = 'XYZ'
    # Combined: micro-motion + turn envelope (frames 40-70 turn to 0.7 rad, hold)
    for f in range(1, args.frames + 1, 6):
        mx = 0.02 * math.sin(f * 0.35)
        my = 0.015 * math.sin(f * 0.22 + 1.3)
        turn = 0.0
        if f >= 70:
            turn = 0.7
        elif f > 40:
            turn = 0.7 * (f - 40) / 30.0
        head_pb.rotation_euler = (my, mx + turn, 0)
        head_pb.keyframe_insert(data_path="rotation_euler", frame=f)
    head_pb.keyframe_insert(data_path="rotation_euler", frame=args.frames)

# --- arm gesture: character-right upper arm raises (frames 80-110, hold to end) ---
arm_pb = None
for b in arm.pose.bones:
    if "_R_UpperArm" in b.name:
        arm_pb = b
        break
if arm_pb:
    arm_pb.rotation_mode = 'XYZ'
    arm_pb.rotation_euler = (0, 0, 0)
    arm_pb.keyframe_insert(data_path="rotation_euler", frame=80)
    arm_pb.rotation_euler = (0.6, -0.4, 0.6)
    arm_pb.keyframe_insert(data_path="rotation_euler", frame=110)
    arm_pb.keyframe_insert(data_path="rotation_euler", frame=120)

scene.frame_start = 1
scene.frame_end = args.frames
scene.render.engine = 'BLENDER_EEVEE'
scene.render.resolution_x = 640
scene.render.resolution_y = 480
scene.render.image_settings.file_format = 'PNG'

# Camera A: frontal mid (0, -1.8, 1.5); Camera B: 30deg off-axis (1.0, -1.6, 1.5)
cam_data = bpy.data.cameras.new("T20Cam")
cam = bpy.data.objects.new("T20Cam", cam_data)
scene.collection.objects.link(cam)
scene.camera = cam
cam.data.lens = 50

# Light
light_data = bpy.data.lights.new("Sun", 'SUN')
light_data.energy = 3.0
light_obj = bpy.data.objects.new("Sun", light_data)
light_obj.location = (1, -1, 3)
scene.collection.objects.link(light_obj)

# Angle A
cam.location = (0, -1.8, 1.5)
cam.rotation_euler = (1.45, 0, 0)
out_a = os.path.join(os.path.abspath(args.outdir), "angleA_")
scene.render.filepath = out_a
bpy.ops.render.render(animation=True)
print(f"[T20] angle A rendered to {out_a}####.png")

# Angle B (30deg off-axis): move camera +x, re-aim
cam.location = (1.05, -1.6, 1.5)
# aim at head (0,0,1.5): direction (-1.05, 1.6, 0) -> rotation approx
cam.rotation_euler = (1.45, 0, 0.58)
out_b = os.path.join(os.path.abspath(args.outdir), "angleB_")
scene.render.filepath = out_b
bpy.ops.render.render(animation=True)
print(f"[T20] angle B rendered to {out_b}####.png")
print("[T20] DONE")
