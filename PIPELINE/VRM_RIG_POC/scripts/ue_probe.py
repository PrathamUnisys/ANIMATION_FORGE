import unreal
print("[M2] FbxImportUI attrs:", [a for a in dir(unreal.FbxImportUI) if not a.startswith("_")][:200])
print("[M2] editor asset methods:", [a for a in dir(unreal.get_editor_subsystem(unreal.EditorAssetSubsystem)) if "import" in a.lower() or "make" in a.lower()])
