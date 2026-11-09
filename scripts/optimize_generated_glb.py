"""Optimize generated GLB in Blender (decimate to target tris, export FBX).
Usage:
  blender --background --python optimize_generated_glb.py -- <input.glb> <output.fbx> <target_tris>
Example:
  blender --background --python optimize_generated_glb.py -- input.glb output.fbx 50000
"""
import sys
import bpy
import os

def mesh_stats(obj):
    me = obj.data
    me.calc_loop_triangles()
    return len(me.polygons), len(me.loop_triangles) * 3

def main():
    import os
    argv = sys.argv
    sep_idx = [i for i, a in enumerate(argv) if a == "--"]
    if sep_idx:
        sep = max(sep_idx)
        args = argv[sep+1:]
    else:
        args = []
    print("PARSED_ARGS", args)
    if len(args) >= 2:
        inp, out = args[0], args[1]
    else:
        inp = os.environ.get("INPUT_GLB", "")
        out = os.environ.get("OUTPUT_FBX", "")
        print("ENV_FALLBACK", inp, out)
    if not inp or not out:
        print("Need input.glb and output.fbx (via -- or env)")
        return 1
    target = int(args[2]) if len(args) > 2 else 50000

    bpy.ops.wm.read_factory_settings(use_empty=True)
    if inp.lower().endswith(".glb"):
        bpy.ops.import_scene.gltf(filepath=inp)
    else:
        bpy.ops.import_scene.fbx(filepath=inp)

    total_before = 0
    objs = [o for o in bpy.context.scene.objects if o.type == 'MESH']
    if not objs:
        print("ERROR: no mesh found in", inp)
        return 1
    # Apply scale + merge verts per mesh
    for o in objs:
        bpy.ops.object.select_all(action='DESELECT')
        o.select_set(True)
        bpy.context.view_layer.objects.active = o
        bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
        total_before += mesh_stats(o)[0]

    total_after = 0
    if total_before > 0:
        ratio_total = min(1.0, target / total_before)
        for o in objs:
            # estimate per-object tris
            tris_before, _ = mesh_stats(o)
            if tris_before == 0:
                continue
            # skip shape-key meshes (facial rigs) - decimate modifier cannot apply; log instead
            if o.data.shape_keys is not None:
                print(f"SKIP shape-key mesh {o.name} ({tris_before} tris) - facial rig preserved")
                total_after += tris_before
                continue
            dec = o.modifiers.new(name="Decimate", type='DECIMATE')
            dec.ratio = max(0.05, ratio_total)
            bpy.ops.object.select_all(action='DESELECT')
            o.select_set(True)
            bpy.context.view_layer.objects.active = o
            bpy.ops.object.modifier_apply(modifier="Decimate")
            # clean
            bpy.ops.object.mode_set(mode='EDIT')
            bpy.ops.mesh.select_all(action='SELECT')
            bpy.ops.mesh.remove_doubles(threshold=0.0001)
            bpy.ops.mesh.normals_make_consistent(inside=False)
            bpy.ops.object.mode_set(mode='OBJECT')
            total_after += mesh_stats(o)[0]

    print(f"TRIS_BEFORE {total_before} TRIS_AFTER {total_after} TARGET {target}")
    os.makedirs(os.path.dirname(os.path.abspath(out)), exist_ok=True)
    bpy.ops.export_scene.fbx(filepath=os.path.abspath(out), use_mesh_modifiers=True, add_leaf_bones=False)
    print("EXPORTED", out, f"{os.path.getsize(out)} bytes")
    return 0

if __name__ == "__main__":
    main()
