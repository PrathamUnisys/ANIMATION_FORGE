"""T21 Shot 2 (projection): camera push through alley plate (upscaled 2192x1440).
Run: blender.exe --background --python shot2_projection.py -- --plate PIPELINE/BAKEOFF/alley_seedvr2_upscaled.png --outdir PIPELINE/BAKEOFF/T21_shot2
Camera pushes forward (Z dolly) 120 frames; UV_PROJECT on plane; render PNG sequence.
"""
import bpy, os, argparse
argv = __import__('sys').argv[__import__('sys').argv.index("--") + 1:]
ap = argparse.ArgumentParser()
ap.add_argument("--plate", required=True)
ap.add_argument("--outdir", required=True)
ap.add_argument("--frames", type=int, default=120)
args = ap.parse_args(argv)

bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)
for m in list(bpy.data.meshes):
    bpy.data.meshes.remove(m)
for m in list(bpy.data.materials):
    bpy.data.materials.remove(m)
for img in list(bpy.data.images):
    bpy.data.images.remove(img)

bpy.ops.mesh.primitive_plane_add(size=6, location=(0, 0, 1.2))
plane = bpy.context.active_object
plane.name = "PlateMesh"
# Vertical backdrop (rotate plane to stand up, facing -Y camera)
plane.rotation_euler = (1.5708, 0, 0)

mat = bpy.data.materials.new("PlateMat")
mat.use_nodes = True
bsdf = next(n for n in mat.node_tree.nodes if n.type == 'BSDF_PRINCIPLED')
tex = mat.node_tree.nodes.new('ShaderNodeTexImage')
img = bpy.data.images.load(args.plate)
tex.image = img
mat.node_tree.links.new(tex.outputs['Color'], bsdf.inputs['Base Color'])
plane.data.materials.append(mat)

# Projector camera
cam_data = bpy.data.cameras.new("Projector")
projector = bpy.data.objects.new("Projector", cam_data)
projector.location = (0, -5, 1.5)
projector.rotation_euler = (1.65, 0, 0)
bpy.context.scene.collection.objects.link(projector)

mod = plane.modifiers.new("UV_PROJECT", 'UV_PROJECT')
mod.projectors[0].object = projector

bpy.context.view_layer.objects.active = plane
plane.select_set(True)
bpy.context.view_layer.update()
bpy.ops.object.modifier_apply(modifier=mod.name)
print("[T21] UV_PROJECT applied")

# Render camera: push forward (dolly in +Y then +Z small)
rc_data = bpy.data.cameras.new("PushCam")
render_cam = bpy.data.objects.new("PushCam", rc_data)
bpy.context.scene.collection.objects.link(render_cam)
bpy.context.scene.camera = render_cam

scene = bpy.context.scene
scene.render.engine = 'BLENDER_EEVEE'
scene.render.resolution_x = 640
scene.render.resolution_y = 480
scene.render.image_settings.file_format = 'PNG'
scene.frame_start = 1
scene.frame_end = args.frames

# Push: f1 at (0,-4,1.2), f120 at (0,-1.5,1.2) looking +Y (into plate)
render_cam.location = (0, -4.0, 1.4)
render_cam.rotation_euler = (1.62, 0, 0)
render_cam.keyframe_insert(data_path="location", frame=1)
render_cam.keyframe_insert(data_path="rotation_euler", frame=1)
render_cam.location = (0, -1.5, 1.4)
render_cam.rotation_euler = (1.62, 0, 0)
render_cam.keyframe_insert(data_path="location", frame=args.frames)
render_cam.keyframe_insert(data_path="rotation_euler", frame=args.frames)

os.makedirs(args.outdir, exist_ok=True)
out = os.path.join(os.path.abspath(args.outdir), "shot2_")
scene.render.filepath = out
bpy.ops.render.render(animation=True)
print("[T21] DONE")
