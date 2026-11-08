# Safe Blender Integration Guide

`SafeBlenderAndUnrealAdapter` (`backend/integrations/blender_unreal_adapters.py`) integrates with Blender 5.2 LTS (`bpy` / `blender --background --python`).
- **AST Security Gate**: Every generated Python script is parsed via Python's `ast` module before execution. Imports of `subprocess`, `socket`, `shutil`, `requests`, `urllib`, or calls to `eval`/`exec`/`system` are rejected with `UnsafeScriptError`.
- **Non-Destructive Staging**: Scripts execute strictly in `PROJECTS/<ID>/DRAFTS/` and never overwrite approved `.blend` files.
