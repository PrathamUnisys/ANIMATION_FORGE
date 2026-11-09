"""M2b: export Face only to isolate morph survival."""
import bpy, addon_utils, sys, os
addon_utils.enable("bl_ext.blender_org.vrm")
argv = sys.argv[sys.argv.index("--") + 1:]
def get(a, d=""):
    i = argv.index(a); return argv[i+1] if i+1 < len(argv) else d
blend, out = get("--blend"), get("--out")
bpy.ops.wm.open_mainfile(filepath=blend)
face = bpy.data.objects.get("Face")
arm = next((o for o in bpy.context.scene.objects if o.type == "ARMATURE"), None)
for o in bpy.context.scene.objects:
    o.select_set(False)
if face: face.select_set(True)
if arm: arm.select_set(True)
bpy.context.view_layer.objects.active = face
os.makedirs(os.path.dirname(os.path.abspath(out)), exist_ok=True)
bpy.ops.export_scene.fbx(filepath=out, use_selection=True, global_scale=1.0,
    apply_unit_scale=True, apply_scale_options="FBX_SCALE_ALL",
    object_types={"ARMATURE", "MESH"}, use_mesh_modifiers=True,
    add_leaf_bones=False, armature_nodetype="NULL", bake_space_transform=True,
    embed_textures=True, batch_mode="OFF", path_mode="COPY")
print(f"[M2b] exported Face-only {out}")
