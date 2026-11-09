"""Final composite: lit (T23), improved arms-down idle (larger angle), mouth/turn/gesture.
Run: blender.exe --background --python final_composite.py -- --blend T23_lit.blend --visemes test_line_visemes.json --plate alley_seedvr2_upscaled.png --outdir PIPELINE/BAKEOFF/T25_final
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
scene = bpy.context.scene

# Backdrop
bpy.ops.mesh.primitive_plane_add(size=8, location=(0, 3.0, 1.2))
plate = bpy.context.active_object
plate.name = "PlateMesh"
plate.rotation_euler = (1.5708, 0, 0)
mat = bpy.data.materials.new("PlateMat")
mat.use_nodes = True
bsdf = next(n for n in mat.node_tree.nodes if n.type == 'BSDF_PRINCIPLED')
tex = mat.node_tree.nodes.new('ShaderNodeTexImage')
tex.image = bpy.data.images.load(os.path.abspath(args.plate))
mat.node_tree.links.new(tex.outputs['Color'], bsdf.inputs['Base Color'])
plate.data.materials.append(mat)
proj_data = bpy.data.cameras.new("ProjCam")
proj = bpy.data.objects.new("ProjCam", proj_data)
proj.location = (0, -2, 1.5)
proj.rotation_euler = (1.65, 0, 0)
scene.collection.objects.link(proj)
mod = plate.modifiers.new("UV_PROJECT", 'UV_PROJECT')
mod.projectors[0].object = proj
bpy.context.view_layer.update()
bpy.ops.object.select_all(action='DESELECT')
plate.select_set(True)
bpy.context.view_layer.objects.active = plate
bpy.ops.object.modifier_apply(modifier=mod.name)
print("[T25] backdrop projected")

# Mouth
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

# Arms: improved idle (L hangs) hold, R idle then gesture
arm_r = arm_l = None
for b in arm.pose.bones:
    if "R_UpperArm" in b.name:
        arm_r = b
    if "L_UpperArm" in b.name:
        arm_l = b
arm_r.rotation_mode = 'XYZ'
arm_r.rotation_euler = (0.55, -0.15, -0.15)
arm_r.keyframe_insert(data_path="rotation_euler", frame=2)
arm_r.rotation_euler = (1.4, -0.4, 0.6)
arm_r.keyframe_insert(data_path="rotation_euler", frame=110)
arm_r.keyframe_insert(data_path="rotation_euler", frame=120)
arm_l.rotation_mode = 'XYZ'
arm_l.rotation_euler = (0.55, 0.15, 0.15)
arm_l.keyframe_insert(data_path="rotation_euler", frame=2)
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
out = os.path.join(os.path.abspath(args.outdir), "comp_")
scene.render.filepath = out
bpy.ops.render.render(animation=True)
print("[T25] DONE")
