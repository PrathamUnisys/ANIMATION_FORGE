import unreal
opt = unreal.FbxImportUI()
smi = opt.get_editor_property("skeletal_mesh_import_data")
print("[M2] smi type:", type(smi).__name__)
print("[M2] smi attrs:", [a for a in dir(smi) if not a.startswith("_")][:300])
print("[M2] task attrs:", [a for a in dir(unreal.AssetImportTask) if not a.startswith("_")][:200])
sub = unreal.get_editor_subsystem(unreal.EditorAssetSubsystem)
print("[M2] all sub methods:", [a for a in dir(sub) if not a.startswith("_")][:200])
