"""M2: import FBX (SkeletalMesh + Morphs) into Library project via UE Python.
Run: UnrealEditor-Cmd Library.uproject -run=PythonScript -script=ue_import_fbx.py
"""
import unreal

SRC = r"D:\Work\ANIMATION_FORGE\PIPELINE\VRM_RIG_POC\outputs\M2_redhairgirl.fbx"
DEST = "/Game/VRM_RIG_POC"

sub = unreal.get_editor_subsystem(unreal.EditorAssetSubsystem)
sub.make_directory(DEST)

task = unreal.AssetImportTask()
task.filename = SRC
task.destination_path = DEST
task.destination_name = "RedHairGirl"
task.automated = True
task.replace_existing = True
task.save = True

opt = unreal.FbxImportUI()
opt.set_editor_property("import_mesh", True)
opt.set_editor_property("import_as_skeletal", True)
opt.set_editor_property("import_animations", False)
opt.set_editor_property("import_materials", True)
opt.set_editor_property("import_textures", True)
opt.set_editor_property("create_physics_asset", False)
task.options = opt

tools = unreal.AssetToolsHelpers.get_asset_tools()
tools.import_asset_tasks([task])

assets = sub.list_assets(DEST, True, False)
print("[M2] assets:", assets)
for a in assets:
    obj = sub.load_asset(a)
    print("[M2] asset:", a, (type(obj).__name__ if obj else None))
    # morph list on skeletal mesh
    if obj and isinstance(obj, unreal.SkeletalMesh):
        # morph targets live on LOD settings; introspect mesh data
        try:
            mesh = obj.get_editor_property("lod_settings")
            print("[M2] mesh type:", type(mesh).__name__ if mesh else None)
        except Exception as e:
            print("[M2] lod check:", e)
