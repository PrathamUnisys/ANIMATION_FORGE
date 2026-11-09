"""M2 v1: export M1 VRM blend to FBX (armature + mesh + shape keys).
Run: blender.exe --background --python vrm_export_fbx.py -- --blend <M1.blend> --out <out.fbx>
"""
import bpy, addon_utils, sys, os
addon_utils.enable("bl_ext.blender_org.vrm")
argv = sys.argv[sys.argv.index("--") + 1:]
def get(a, d=""):
    i = argv.index(a)
    return argv[i + 1] if i + 1 < len(argv) else d
blend, out = get("--blend"), get("--out")
bpy.ops.wm.open_mainfile(filepath=blend)
os.makedirs(os.path.dirname(os.path.abspath(out)), exist_ok=True)
# select mesh + armature only
for o in bpy.context.scene.objects:
    o.select_set(o.type in ("MESH", "ARMATURE"))
bpy.context.view_layer.objects.active = next((o for o in bpy.context.scene.objects if o.type == "MESH"), None)
bpy.ops.export_scene.fbx(
    filepath=out, use_selection=True, use_active_collection=False,
    global_scale=1.0, apply_unit_scale=True, apply_scale_options="FBX_SCALE_ALL",
    object_types={"ARMATURE", "MESH"}, use_mesh_modifiers=True,
    add_leaf_bones=False, armature_nodetype="NULL", bake_space_transform=True,
    embed_textures=True, batch_mode="OFF", use_batch_own_dir=False,
    path_mode="COPY",
)
print(f"[M2] exported {out}")
