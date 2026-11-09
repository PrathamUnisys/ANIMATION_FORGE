"""T18 parallax proof: project the alley plate onto a plane via UV_PROJECT, bake, animate camera, render 2 frames.
Success = the two frames differ (true parallax), not a single sliding layer.
Run: blender.exe --background --python parallax_test.py -- --plate PIPELINE/BAKEOFF/plate_alley.jpg --outdir PIPELINE/BAKEOFF/T18_frames
"""
import bpy, os, argparse
argv = __import__('sys').argv[__import__('sys').argv.index("--") + 1:]
ap = argparse.ArgumentParser()
ap.add_argument("--plate", required=True)
ap.add_argument("--outdir", required=True)
args = ap.parse_args(argv)

# Fresh scene
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)
for m in list(bpy.data.meshes):
    bpy.data.meshes.remove(m)
for m in list(bpy.data.materials):
    bpy.data.materials.remove(m)
for img in list(bpy.data.images):
    bpy.data.images.remove(img)

# 1. Plane mesh (simple geometry that stands in for the MoGe mesh)
bpy.ops.mesh.primitive_plane_add(size=4, location=(0, 0, 0))
plane = bpy.context.active_object
plane.name = "PlateMesh"

# 2. Material with plate texture
mat = bpy.data.materials.new("PlateMat")
mat.use_nodes = True
bsdf = next(n for n in mat.node_tree.nodes if n.type == 'BSDF_PRINCIPLED')
tex = mat.node_tree.nodes.new('ShaderNodeTexImage')
img = bpy.data.images.load(args.plate)
tex.image = img
mat.node_tree.links.new(tex.outputs['Color'], bsdf.inputs['Base Color'])
plane.data.materials.append(mat)

# 3. Projector camera + UV_PROJECT modifier (Blender 5.2 built-in)
cam_data = bpy.data.cameras.new("Projector")
projector = bpy.data.objects.new("Projector", cam_data)
projector.location = (0, -3, 2)
projector.rotation_euler = (1.2, 0, 0)
bpy.context.scene.collection.objects.link(projector)

mod = plane.modifiers.new("UV_PROJECT", 'UV_PROJECT')
try:
    mod.projectors[0].object = projector
    print("[T18] projector set via UVProjector.object")
except Exception as e:
    print(f"[T18] projector set failed: {e}")

# Ensure UV layer exists
if not plane.data.uv_layers:
    plane.data.uv_layers.new(name="UVMap")

# 4. Bake (image texture bake so projection becomes a real UV)
bpy.context.view_layer.objects.active = plane
plane.select_set(True)
bpy.context.view_layer.update()
bpy.ops.object.modifier_apply(modifier=mod.name)
print("[T18] UV_PROJECT applied (no manual unwrap — projection defines UVs)")

# 5. Render camera that moves (parallax): two positions
render_cam_data = bpy.data.cameras.new("RenderCam")
render_cam = bpy.data.objects.new("RenderCam", render_cam_data)
bpy.context.scene.collection.objects.link(render_cam)
bpy.context.scene.camera = render_cam

scene = bpy.context.scene
scene.render.engine = 'BLENDER_EEVEE'
scene.render.resolution_x = 640
scene.render.resolution_y = 480
scene.render.image_settings.file_format = 'PNG'

os.makedirs(args.outdir, exist_ok=True)
frames = [(0, -4, 1.2, (1.25, 0, 0)), (-1.2, -3.5, 1.2, (1.25, 0, 0.25))]
for i, (x, y, z, rot) in enumerate(frames):
    render_cam.location = (x, y, z)
    render_cam.rotation_euler = rot
    scene.frame_set(i + 1)
    render_cam.keyframe_insert(data_path="location", frame=i + 1)
    render_cam.keyframe_insert(data_path="rotation_euler", frame=i + 1)
    out = os.path.join(os.path.abspath(args.outdir), f"T18_parallax_f{i+1}.png")
    scene.render.filepath = out
    bpy.ops.render.render(write_still=True)
    print(f"[T18] rendered {out}")

# Keyframe intermediate for potential video later
print("[T18] DONE")
