"""M2b: import Face-only FBX."""
import unreal
SRC = r"D:\Work\ANIMATION_FORGE\PIPELINE\VRM_RIG_POC\outputs\M2b_face.fbx"
DEST = "/Game/VRM_RIG_POC"
sub = unreal.get_editor_subsystem(unreal.EditorAssetSubsystem)
task = unreal.AssetImportTask()
task.filename = SRC; task.destination_path = DEST
task.destination_name = "RedHairGirlFace"
task.automated = True; task.replace_existing = True; task.save = True
opt = unreal.FbxImportUI()
opt.set_editor_property("import_mesh", True)
opt.set_editor_property("import_as_skeletal", True)
opt.set_editor_property("import_animations", False)
task.options = opt
unreal.AssetToolsHelpers.get_asset_tools().import_asset_tasks([task])
mesh = sub.load_asset("/Game/VRM_RIG_POC/RedHairGirlFace.RedHairGirlFace")
if mesh:
    names = mesh.get_all_morph_target_names()
    print("[M2b] face mesh morphs:", len(names), names[:10])
    skel = mesh.get_editor_property("skeleton")
    print("[M2b] bones:", len(skel.get_editor_property("bone_tree")) if skel else 0)
else:
    print("[M2b] load failed, assets:", sub.list_assets(DEST, True, False))
