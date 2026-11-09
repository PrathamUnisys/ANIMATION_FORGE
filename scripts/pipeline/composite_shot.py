"""Composite: VRM character on upscaled alley plate (same shot, one scene).
Run: blender.exe --background --python composite_shot.py -- --blend T13_redhairgirl.blend --visemes test_line_visemes.json --plate alley_seedvr2_upscaled.png --outdir PIPELINE/BAKEOFF/T22_composite
Renders 120 frames: backdrop plate (UV_PROJECT) + character with mouth/blink/turn/gesture.
"""
import bpy, addon_utils, json, sys, os, argparse, math, random
addon_utils.enable("bl_ext.blender_org.vrm")

argv = sys.argv[sys.argv.index("--") + 1:]
ap = argparse.ArgumentParser()
ap.add_argument("--blend", required=True)
ap.add_argument("--visemes", required=True)
ap.add_argument("--plate", required=True)
ap.add_argument("--outdir", required=True)
ap.add_argument("--frames", type=int, default=120)
args = ap.parse_args(argv)

bpy.ops.wm.open_mainfile(filepath=args.blend)
vis = json.loads(open(args.visemes, encoding="utf-8").read())
os.makedirs(args.outdir, exist_ok=True)

# --- Backdrop plate (vertical, behind character) ---
bpy.ops.mesh.primitive_plane_add(size=8, location=(0, 3.0, 1.2))
plate = bpy.context.active_object
plate.name = "PlateMesh"
plate.rotation_euler = (1.5708, 0, 0)
mat = bpy.data.materials.new("PlateMat")
mat.use_nodes = True
bsdf = next(n for n in mat.node_tree.nodes if n.type == 'BSDF_PRINCIPLED')
tex = mat.node_tree.nodes.new('ShaderNodeTexImage')
img = bpy.data.images.load(os.path.abspath(args.plate))
tex.image = img
mat.node_tree.links.new(tex.outputs['Color'], bsdf.inputs['Base Color'])
plate.data.materials.append(mat)

proj_data = bpy.data.cameras.new("ProjCam")
proj = bpy.data.objects.new("ProjCam", proj_data)
proj.location = (0, -2, 1.5)
proj.rotation_euler = (1.65, 0, 0)
bpy.context.scene.collection.objects.link(proj)
mod = plate.modifiers.new("UV_PROJECT", 'UV_PROJECT')
mod.projectors[0].object = proj
bpy.context.view_layer.update()
bpy.ops.object.select_all(action='DESELECT')
plate.select_set(True)
bpy.context.view_layer.objects.active = plate
bpy.ops.object.modifier_apply(modifier=mod.name)
print("[T22] backdrop projected")

# --- Character animation (reuse shot1 logic, scaled to 120f) ---
scene = bpy.context.scene
face = bpy.data.objects.get("Face")
kb_by_name = {kb.name: kb for kb in face.data.shape_keys.key_blocks}
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
head_pb.rotation_mode = 'XYZ'
for f in range(1, args.frames + 1, 6):
    mx = 0.02 * math.sin(f * 0.35)
    my = 0.015 * math.sin(f * 0.22 + 1.3)
    turn = 0.7 if f >= 70 else (0.7 * (f - 40) / 30.0 if f > 40 else 0.0)
    head_pb.rotation_euler = (my, mx + turn, 0)
    head_pb.keyframe_insert(data_path="rotation_euler", frame=f)
arm_pb = None
for b in arm.pose.bones:
    if "R_UpperArm" in b.name:
        arm_pb = b
        break
arm_pb.rotation_mode = 'XYZ'
# Idle down at f1 (single key), gesture at f110, hold to end
arm_pb.rotation_euler = (0.15, -0.25, -0.35)
arm_pb.keyframe_insert(data_path="rotation_euler", frame=1)
arm_pb.rotation_euler = (0.6, -0.4, 0.6)
arm_pb.keyframe_insert(data_path="rotation_euler", frame=110)
arm_pb.keyframe_insert(data_path="rotation_euler", frame=120)
# Left arm idle hold (single pair)
arm_l = None
for b in arm.pose.bones:
    if "L_UpperArm" in b.name:
        arm_l = b
        break
arm_l.rotation_mode = 'XYZ'
arm_l.rotation_euler = (0.15, 0.25, 0.35)
arm_l.keyframe_insert(data_path="rotation_euler", frame=1)
arm_l.keyframe_insert(data_path="rotation_euler", frame=120)

scene.frame_start = 1
scene.frame_end = args.frames
scene.render.engine = 'BLENDER_EEVEE'
scene.render.resolution_x = 640
scene.render.resolution_y = 480
scene.render.image_settings.file_format = 'PNG'

cam_data = bpy.data.cameras.new("CompCam")
cam = bpy.data.objects.new("CompCam", cam_data)
scene.collection.objects.link(cam)
scene.camera = cam
cam.data.lens = 50
cam.location = (0, -1.6, 1.45)
cam.rotation_euler = (1.5, 0, 0)

light_data = bpy.data.lights.new("Sun", 'SUN')
light_data.energy = 2.0
light_obj = bpy.data.objects.new("Sun", light_data)
light_obj.location = (1, -1, 3)
scene.collection.objects.link(light_obj)

out = os.path.join(os.path.abspath(args.outdir), "comp_")
scene.render.filepath = out

# Render per-frame with explicit view_layer update so pose evaluation matches
# what `view_layer.update()` reports (fixes Blender 5 slot/eval divergence seen in T23).
for f in range(1, args.frames + 1):
    scene.frame_set(f)
    bpy.context.view_layer.update()
    if f == 48:
        print(f"[T22] f48 pre-render R arm: {tuple(round(v,3) for v in arm_pb.rotation_euler)} frame={scene.frame_current}")
    scene.render.filepath = os.path.join(os.path.abspath(args.outdir), f"comp_{f:04d}.png")
    bpy.ops.render.render(write_still=True)
print("[T22] DONE per-frame")
