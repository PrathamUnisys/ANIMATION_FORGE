import unreal
sub = unreal.get_editor_subsystem(unreal.EditorAssetSubsystem)
mesh = sub.load_asset("/Game/VRM_RIG_POC/RedHairGirl.RedHairGirl")
names = mesh.get_all_morph_target_names()
print("[M2] all morph names:", len(names), names[:10])
