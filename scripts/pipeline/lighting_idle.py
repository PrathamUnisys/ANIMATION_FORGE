"""Lighting + idle pass applied to T22 composite scene.
Run: blender.exe --background --python lighting_idle.py -- --blend OUT.blend
Edits an existing blend: adds HDRI-less 3-point lighting (key/fill/rim + world), arms-down idle.
"""
import bpy, addon_utils, json, sys, argparse, math
addon_utils.enable("bl_ext.blender_org.vrm")

argv = sys.argv[sys.argv.index("--") + 1:]
ap = argparse.ArgumentParser()
ap.add_argument("--blend", required=True)       # input blend (T13)
ap.add_argument("--visemes", required=True)
ap.add_argument("--plate", required=True)
ap.add_argument("--outblend", required=True)    # output blend
ap.add_argument("--frames", type=int, default=120)
args = ap.parse_args(argv)

bpy.ops.wm.open_mainfile(filepath=args.blend)
vis = json.loads(open(args.visemes, encoding="utf-8").read())
scene = bpy.context.scene

# --- World: warm ambient instead of black ---
world = scene.world or bpy.data.worlds.new("World")
scene.world = world
world.use_nodes = True
bg = next((n for n in world.node_tree.nodes if n.type == 'BACKGROUND'), None)
if bg:
    bg.inputs["Color"].default_value = (0.28, 0.22, 0.18, 1.0)
    bg.inputs["Strength"].default_value = 1.2

# --- 3-point lighting: warm key, cool fill, rim ---
def add_light(name, loc, rot, energy, color, stype='SUN'):
    data = bpy.data.lights.new(name, stype)
    data.energy = energy
    data.color = color
    obj = bpy.data.objects.new(name, data)
    obj.location = loc
    obj.rotation_euler = rot
    scene.collection.objects.link(obj)
    return obj

# Remove existing sun if any
for o in [x for x in scene.objects if x.type == 'LIGHT']:
    scene.collection.objects.remove(o)

add_light("KeyWarm", (2.5, -2.5, 3.5), (0.9, 0.3, 0.4), 4.0, (1.0, 0.82, 0.62))
add_light("FillCool", (-2.5, -2.0, 2.0), (1.1, -0.4, -0.5), 1.5, (0.65, 0.75, 1.0))
add_light("Rim", (0.5, 3.0, 2.5), (1.4, 0.2, 1.2), 2.5, (1.0, 0.9, 0.7))

print("[L] lighting applied (idle keyframes handled by composite_shot)")
bpy.ops.wm.save_as_mainfile(filepath=args.outblend)
print(f"[L] saved {args.outblend}")
