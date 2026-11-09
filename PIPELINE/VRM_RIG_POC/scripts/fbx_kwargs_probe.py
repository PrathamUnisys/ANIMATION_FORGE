import bpy
kw = bpy.ops.export_scene.fbx.get_rna_type().properties.keys()
print("[M2] fbx kwargs:", sorted(kw))
