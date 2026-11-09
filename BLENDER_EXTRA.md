# Blender Extensions + Legacy Add-ons + Repo Supplement (2026-11-09)
Companion to P0_GAP_MATRIX + RESEARCH_P1_P3. Sources: disk `Test-Path` + https://extensions.blender.org/ (fetched).

## Installed extensions (Blender 5.2)

### user_default (19 entries with .blender_ext)
| Add-on | Purpose | Used in |
|---|---|---|
| auto_rig_pro | Auto-rig humanoid/body | Characterization |
| EasyEnv | Environment lighting (matches EasyEnv.zip) | World gen |
| faceit | Facial capture / shape keys | Facial |
| gui_slider | UI slider widget | Utilities |
| hair_brush_3d | Hair grooming brushes | Hair |
| keentools | KeenTools tracking nodes | Camera tracking |
| kekit | KitOps + HardOps | Modeling |
| mesh_data_transfer | Mesh data transfer | Retopo |
| meta_human_dna | MetaHuman DNA bridge | Char → MetaHuman |
| truedepth | TrueDepth capture (Apple) | Capture |

### blender_org
| Add-on | Purpose |
|---|---|
| amarillos_vrm_toolkit | VRM helper |
| frame_by_plane | Frame by plane (storyboard/reference) |
| model_decompressor | Model decompression |
| pseudo_rendering_farm | Pseudo render farm |
| sapling_tree_gen | Procedural trees |
| t3d_gn_presets | Geometry Nodes presets |
| ucupaint | Ucupaint (UV) |
| vrm | VRM io |

### lab_blender_org
| Add-on | Purpose |
|---|---|
| mcp | Blender MCP server addon (pairs with opencode.json npx @ahujasid/blender-mcp) |

### Legacy add-ons (`scripts/addons`)
| Folder | Purpose |
|---|---|
| ajc27_freemocap_blender_addon | FreeMoCap plugin |
| cc_blender_tools-2_3_2 / -2_3_4 | CC Blender Tools (Reallusion) — duplicate versions |
| EasyEnv | Legacy duplicate of extension EasyEnv |
| fspy_blender | fSpy camera importer (see https://fspy.io/ + https://github.com/stuffmatic/fSpy-Blender — fetched) |
| Hair_Tool_v4.4.0___Library | Hair tool 4.4 vfxMed |
| polyhavenassets-1.2.1 | Poly Haven assets browser |
| proscenium_blender | Proscenium volumetric stage |
| Rokoko Libraries + rokoko-studio-live-blender-master | Rokoko Studio Live (mocap) |
| ue5_pipeline | UE5 pipeline (matches ue5_pipeline.zip in Downloads) |

## Free/open-source candidates from https://extensions.blender.org/add-ons/ (fetched listing)
All Blender 5.x compatible Extensions, free, no cost, low risk (no VRAM).

| Candidate | Category (tags) | Evidence from fetch | Fits gap |
|---|---|---|---|
| Bool Tool (`/add-ons/bool-tool/`) | Modeling/Object | “Quick Boolean operators and tools for hard surface modeling”, 65 reviews, **1M** downloads | Modeling speed |
| Texel Density Checker (`/add-ons/texel-density-checker/`) | 3D View/Object/UV | “Toolset for working with Texel Density”, 51 reviews, 111K | Texturing |
| Mio3 UV (`/add-ons/mio3-uv/`) | UV | “UV Edit Assistant Tools”, 133 reviews, 316K | UV (pairs with ucupaint) |
| Modifier List (`/add-ons/modifier-list-fork/`) | Modeling/User Interface | “Enhanced Modifier UI”, 101 reviews, 95K | Modeling UI speed |
| Node Arrange (`/add-ons/node-arrange/`) | Node | “Arrange node trees with one click”, 100 reviews, 256K | Node speed |
| Node Pie (`/add-ons/node-pie/`) | User Interface/Node | “Add nodes faster with a pie menu”, 60 reviews, 98K | Node speed |
| Screencast Keys (`/add-ons/screencast-keys/`) | System/User Interface | “Display keys pressed”, 36 reviews, 201K | Tutorials/docs |

All are Free/Own license (Blender Extensions). Exact versions to confirm on install (Extensions page details).

## Other software / GitHub repos worth adding (tied to installed stack)
- **Blender MCP** — `lab_blender_org/mcp` (installed) + opencode npx bridge. https://github.com/ — pairs with ANIMATION_FORGE.
- **Rokoko Studio Live** — https://www.rokoko.com/ — legacy folders already staged; use for live mocap to Blender.
- **FreeMoCap Blender addon** — https://github.com/freemocap/freemocap — addon legacy present.
- **CC Blender Tools** — `cc_blender_tools-2_3_4` — https://www.reallusion.com/ — already staged.
- **Poly Haven** — https://polyhaven.org/ — addon `polyhavenassets-1.2.1` assets browser, pairs with Quixel Bridge library.
- **UE5 Pipeline** — `ue5_pipeline` folder + `ue5_pipeline.zip` — UE-Blender bridge, watch version (UE 5.8).
- **ComfyUI → Blender bridge** — custom_nodes `ComfyUI-Trellis2` outputs `.glb` → `D:\Downloads\ComfyUI_temp_*.png` / `.glb` already in Downloads; use MeshToFile3D + CLIPVisionLoader nodes in `PixelArtistry_*` workflows.

## Recommended Blender free stack (priority order for trials)
1. Bool Tool, 2. Mio3 UV, 3. Texel Density Checker, 4. Node Arrange, 5. Modifier List — all zero cost, CPU only, install via Extensions tab (2-click), no python venv needed. Trial each one-by-one on `robot.blend` or `MedivalCityGeneratorEdit.blend` sample.
2. Defer heavier fan add-ons (Retopo Flow discontinued path → use KitOps/mesh_data_transfer already installed).

Evidence: installed names via shell `Get-ChildItem extensions/.../blender_manifest.toml` (19 files). Candidate free features via webfetch `extensions.blender.org/` landing (downloads/reviews). No versions claimed beyond fetch.
