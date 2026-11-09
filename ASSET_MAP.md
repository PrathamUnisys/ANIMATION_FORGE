# Creative Software + Projects + Asset Map — C:\ and D:\ (Expanded)
Updated 2026-11-09 — Tools-first full sweep per `D:\Work\ANIMATION_FORGE\TOOLS\CATALOG.json` + `README.md`
Method: read-only disk checks + vendor page fetches (web search down 402 → webfetch fallback). Nothing started live.

## Drives
- `C:\` — 489 GB used / 19 GB free (critically low)
- `D:\` — 885 GB used / 115 GB free

## Internal Tools catalog (Animation Forge)
- `TOOLS/` = `BLENDER/`, `COMFYUI/`, `UNREAL_ENGINE/`, `TEMPLATES/`, `CATALOG.json`, `README.md`
- `CATALOG.json` v1.0.0 — 3 desktop tools + 5 providers, 11 task groups. All `SIMULATION_ONLY` / `NOT_VERIFIED` in original.
  Providers: `LOCAL_DETERMINISTIC_STUDIO`, `OPENAI_COMPATIBLE_CLOUD`, `ELEVENLABS_TTS`, `LOCAL_KOKORO_TTS`, `COMFYUI_LOCAL_GRAPH`
- `LIBRARY/ASSET_INDEX.json` = empty `{"assets":[]}`
- `LIBRARY/STORAGE_ROOTS.example.json` = 4 roots (PROJECTS_ROOT, SHARED_LIBRARY_ROOT, CHANNEL_BRAND_ROOT, RENDER_OUTPUT_ROOT) all UNCONFIGURED
- Manual standard: `TEMPLATES/TOOL_MANUAL_TEMPLATE.md` — never guess path/version; use `UNKNOWN / NOT_INSTALLED / NOT_VERIFIED` until checked. Hosted providers stay in `PROVIDERS/`.

## Software Deep Dive (what it does + where + version)

### DCC / 3D
| Tool | What it does (vendor source) | Path | Version | Category |
|---|---|---|---|---|
| Blender | 3D creation: modeling, rigging, materials, animation, lighting, rendering, compositing — https://www.blender.org/ | `D:\Program Files\BlenderFoudation\blender.exe` + datafolders 5.0, 5.2; roaming 2.93–5.2 | 5.2 | DCC_3D |
| Unreal Engine | Real-time 3D engine: scene assembly, lighting, cameras, Sequencer, animation, VP, rendering — https://www.unrealengine.com/ | `C:\Program Files\Epic Games\UE_5.6`, `D:\Work\Epic\UE_5.7`, `UE_5.8` | 5.6 CL-44394996 / 5.7 CL-51494982 / 5.8 CL-58902052 | REALTIME_3D |
| ZBrush 2025 | Digital sculpting (Maxon) — https://www.maxon.net/en/zbrush | `C:\Program Files\Maxon ZBrush 2025\` (contains `ZData` only at top in listing — exe needs deeper check) | UNKNOWN (Maxon ZBrush 2025 folder) | SCULPT |
| DAZ 3D Studio | Character posing/animation (DAZ3DIM1) — https://www.daz3d.com/ | `C:\Program Files\DAZ 3D\DAZ3DIM1\` | UNKNOWN | DCC_3D |
| Marvelous Designer | Cloth simulation / garment patterns (Enterprise Offline) — https://www.marvelousdesigner.com/ | `D:\Program Files\Marvelous Designer Enterprise Network Offline\MarvelousDesigner_Enterprise_Offline.exe` | 2025.2.143 | CLOTH |
| Moho 14 / 14.4 | 2D animation (Lost Marble) — https://moho.lostmarble.com/ | `C:\Program Files\Moho 14\Moho.exe` | 14.4 | ANIMATION_2D |
| Krita | 2D painting/illustration — https://krita.org/ | `C:\Program Files\Krita (x64)\bin\krita.exe` | 5.2.14 | 2D_PAINT |
| PureRef | Mood/reference board (image planes) — https://www.pureref.com/ | `C:\Program Files\PureRef\PureRef.exe` | 2.1.3 | REFERENCE |
| Gaea 2.0 | Procedural terrain/heightmaps (QuadSpinner) — https://quadspinner.com/ | `D:\Work\Gaea 2.0\Gaea.exe` + project `D:\Work\Gaea\Project,Output,Document` | 2.x (Gaea 2.0 folder) | WORLD_GEN |
| PlantFactory | Procedural vegetation (e-on) — folder `D:\Program Files\PlantFactory\` contains only `datafolder,Uninstall` in listing — needs deeper check. https://www.e-onsoftware.com/plantfactory/ | `D:\Program Files\PlantFactory\` | UNKNOWN | VEGETATION |
| Faceform Wrap 2025.11.14 | Topology transfer for digital doubles — conform scans to one mesh for facial rigging — https://faceform.com/ (fetched 2026-11-09) | `C:\Program Files\Faceform\Wrap 2025.11.14\` + `D:\Work\Content Creation\faceform`, `D:\Downloads\Faceform Wrap 2025.11.14 vfxMed` | 2025.11.14 (from folder name) | FACE_PIPELINE |
| Adobe suite | Creative Cloud (Photoshop etc) — https://www.adobe.com/ | `C:\Program Files\Adobe\` (x64+x86) | UNKNOWN | 2D/VIDEO |
| The Foundry | Nuke VFX licensing tools (FlexLM/RLM) — https://www.foundry.com/ | `C:\Program Files\The Foundry\FLEXlm,LicensingTools7.1,RLM` + `C:\Users\sb291\FoundryLicensing` | 7.1 (LicensingTools) | VFX_LICENSE |

### Character / mocap / rigging
| Tool | What it does | Path | Version | Category |
|---|---|---|---|---|
| Character Creator 5 | Character generation (Reallusion) — https://www.reallusion.com/ | `C:\Program Files\Reallusion\Character Creator 5\Bin64\CharacterCreator.exe` | 5.12.1927.1 | CHAR_GEN |
| AccuRIG | Auto-rig humanoid characters (Reallusion, free) — https://www.reallusion.com/auto-rig/ | `C:\Program Files\AccuRIG\AccuRIG.exe` | UNKNOWN (no version string checked) | AUTO_RIG |
| Cascadeur | Physics-based character animation / posing / mocap cleanup — https://www.cascadeur.com/ | `C:\Program Files\Cascadeur\cascadeur.exe` + `CascadeurOriginal\` | 2026.1.2.0.15343 | CHAR_ANIM |
| FreeMoCap | Free open-source **markerless mocap** (2+ webcams, outputs CSV/FBX/.blend) — https://freemocap.org/ (fetched) | `C:\Users\sb291\freemocap_data\` (logs+recording_sessions) | UNKNOWN | MOCAP |
| SkellyTracker / Skelly | FreeMoCap companion tracker (Skelly = FreeMoCap mascot) — https://github.com/freemocap/freemocap | `C:\Users\sb291\skelly-cam-recordings`, `skellytracker_data`, `skelly_synchronize_data`, `skelly_viewer_data` | UNKNOWN | MOCAP_UTIL |
| TrueDepth Blender addon | Depth utility addon (python311+313) | `C:\Users\sb291\TrueDepth-blender-addon\settings.json` | UNKNOWN | BLENDER_ADDON |
| VRM_Converter (Unity) | VRM → Unity conversion project | `C:\Users\sb291\VRM_Converter\Assets,Library,Packages,ProjectSettings` | UNKNOWN | VRM |
| Reallusion iCity | Real-estate / city preset packs for CC/iClone | `D:\Content Creation\iCity Cyberpunk 1.7.1 - Individual License\`, `D:\Library\Blender\iCity[-Cyberpunk Theme]` | 1.7.1 | CITY_PRESETS |
| Quixel Bridge | 3D asset browser (Megascans) — https://quixely.com or https://bridge.quixely.com? — canonical: https://www.quixely.com/ | `C:\Program Files\Bridge\` (exists, empty at top), `D:\Work\Quxeil Bridge\New folder` (empty) | UNKNOWN — **Bridge mystery, needs live check** | ASSET_BROWSER |

### Video / audio / media
| Tool | What it does | Path | Version | Category |
|---|---|---|---|---|
| DaVinci Resolve | Video editing/color/Fusion — https://www.blackmagicdesign.com/products/davinciresolve | `C:\Program Files\Blackmagic Design\DaVinci Resolve\Resolve.exe` + `C:\Users\sb291\DaVinci Resolve Media` | 21.0.0.48 | VIDEO_EDIT |
| Audacity | Audio editor — https://www.audacityteam.org/ | `C:\Program Files\Audacity\Audacity.exe` | 3.7.7 | AUDIO |
| OBS Studio | Screen/stream capture — https://obsproject.com/ | `C:\Program Files\obs-studio\` | 31.1.2 (uninstall.exe) | CAPTURE |

### AI / generation
| Tool | What it does | Path | Version |
|---|---|---|---|
| ComfyUI portable | Node-based local image/video generation server — https://github.com/Comfy-Org/ComfyUI | `D:\Downloads\ComfyUI_windows_portable_nvidia\ComfyUI_windows_portable\ComfyUI\` + `python_embeded\`, `run_nvidia_gpu.bat` | UNKNOWN (offline) |
| Ollama | Local LLM runner — https://ollama.com/ | `D:\Ollama\blobs,manifests` + `%LOCALAPPDATA%\Ollama` | 0.40.14 (per AGENTS.md) |

### Pipeline / dev / util (non-creative but installed)
| Tool | What it does | Path | Version |
|---|---|---|---|
| Blender MCP (opencode) | Local MCP bridge for Blender — `C:\Users\sb291\opencode.json` → `npx @ahujasid/blender-mcp`, enabled | config only; AGENTS says uvx + 9876 — **conflict** | — |
| Rigby2D | 2D skeletal animation (Spine-like) — https://www.rigby2d.com?/github — portable `.exe` + repo under `D:\Work\Tools\rigby2d\src-tauri` | `D:\Work\Rigby2D_x64_portable.exe`, `D:\Work\Tools\rigby2d\` | UNKNOWN |
| Air Live Drive | Mounts cloud storage (Google/OneDrive/Dropbox/S3 +40) as local drive, no sync — https://www.airlivedrive.com/ (fetched: “Best Cloud Drive Mapper”) | `C:\Program Files\AirLiveDrive\AirLiveDrive.exe` | UNKNOWN |
| Dokan | Virtual filesystem driver (Air Live Drive depends on it) — https://dokan-dev.github.io/ | `C:\Program Files\Dokan\` + `AirLiveDrive\dokan2.dll` | UNKNOWN |
| Ghidra | Software Reverse Engineering framework (NSA, open source) — https://ghidra-sre.org/ (fetch redirected to github.com/NationalSecurityAgency/ghidra) | `D:\Ghidra\` (contains `Cascadeur.rep`, `Cascadeur.gpr` — **not** Ghidra install, folder reused) | UNKNOWN |
| Git / Git LFS | Version control — https://git-scm.com/ | `C:\Program Files\Git\cmd\git.exe` | 2.54.0.windows.1 |
| ffmpeg | CLI media conversion — https://ffmpeg.org/ | `C:\Program Files\ffmpeg\` | UNKNOWN |
| miniconda3 | Python env manager — https://docs.conda.io/ | `C:\Users\sb291\miniconda3\` | UNKNOWN |
| nodejs | JS runtime — https://nodejs.org/ | `C:\Program Files\nodejs\` | UNKNOWN |
| Unity + Unity Hub | Game engine — https://unity.com/ | `C:\Program Files\Unity`, `Unity Hub` (no exe version found in `Hub\Editor\*\Editor\Unity.exe`) | UNKNOWN |
| Softdeluxe FDM | Free Download Manager — https://www.freedownloadmanager.org/ | `C:\Program Files\Softdeluxe\Free Download Manager\` | UNKNOWN |
| Dependencies (lucasg) | DLL dependency viewer — https://github.com/lucasg/Dependencies | `D:\Downloads\Dependencies_x64_Release\Dependencies.exe` | UNKNOWN |
| aco_alt_installers.zip | AccuRIG/CC alt installers bundle (staged) | `D:\Downloads\aco_alt_installers\aco_alt_installers.zip` | — |

## Projects (user content)
- **Unreal:** `D:\Projects\` ×6 — Detactive_Env, MyVfxProject, SamuraiProject, StylizedProceduralEn, Stylized_env, Stylized_FullVid
- **Rigby2D:** `D:\Work\Rigby2D-Projects\` — flat-man.rigby, rigbytron.rigby, frames*, fight-audio.wav
- **Blender:** `D:\Library\Blender\Medieval*Generator*.blend`, `D:\Downloads\robot.blend`, Desktop `medieval_alley_*.png` (150+)
- **Cascadeur:** `D:\Library\Cascadeur\Maximo_model.casc`, `D:\Library\Animations\CascadeurManny,Maximo`
- **CC5 libs:** `D:\Work\Reallusion Custom\` (Accessory, Actor, Hair, Props, Set…) + `D:\Library\CC to Blender\Base.fbx`
- **ComfyUI workflows:** `D:\Comfyui Workflow\PixelArtistry_*.json` ×5, `D:\Work\Workflows\*.json` ×3
- **CC5→Blender plugins:** `D:\Downloads\Plugins\Blender_Pipeline_Plugin_for_CC5_Hub.exe`, `cc_blender_tools-2_3_2.zip`

## Asset Libraries
- `D:\Library\` — 3d Characters, Animations, Blender, Cascadeur, CC to Blender, Characters, City Meshes, Clothes, Landscape Material, Metahuman export, Road, Rocks for Unreal, Tree, Unreal Landscape Materials
- `D:\Content Creation\` — faceform, fSpy-1.0.3-win, iCity Cyberpunk 1.7.1, Inspirations, Material, Mocap
- `D:\Exports\` — Blender, Hairs, Metahuman, OBS Exports, PlantFactory, Unreal Animation, Unreal Metahuman fbx
- `D:\Courses\` — AI Metahuman Tutorial, Unreal Engine Course, Boundless Unreal for Filmmakers, Bloop Animations, CharacterClass
- `D:\Downloads\` — staging with dupes (`ComfyUI_windows_portable_nvi*`, VRM4U_5_7/5_8, Cascadeur v2026.1.2, Faceform Wrap vfxMed, Hair_Tool vfxMed, Dreamscape Nature Tower, TreeIt-20-8-2025…)
- `D:\Work\` — ANIMATION_FORGE, Content Creation, Epic (UE 5.7/5.8), Gaea, Gaea 2.0, Mods, Quxeil Bridge, Reallision, Reallusion Custom, Rigby2D-Projects, Tools, Workflows
- `D:\Games\` — AC Black Flag Resynced, Black Myth Wukong, ELDEN RING, Horizon Zero Dawn Remastered, ModEngine-2.1.0.0-win64, Mods, Stellar Blade

## MCP / Config (offline, check later)
- Blender MCP `C:\Users\sb291\opencode.json` npx vs AGENTS uvx/9876 — resolve on first live run
- Unreal MCP `127.0.0.1:8000/mcp`, Rigby2D (workspace `D:\Work\Rigby2D-Projects`), ComfyUI `run_nvidia_gpu.bat` — all not started
- Ollama `ornith:9b` primary / `qwen3.5:4b` fallback, models `D:\Ollama`

## TODO
- [ ] Bridge exe mystery + Megascans path; iClone present?; ZBrush/PlantFactory/Dok an exes deeper
- [ ] C: 19 GB free — archive Desktop medieval frames + Downloads dupes to D:
- [ ] Canonical ComfyUI location (portable in Downloads vs Work)
- [ ] Expanded TOOLS catalog: 12 new manuals added (see git diff)

## Re-verify
Backups made before edit (`ASSET_MAP.md.bak-20261109`, `CATALOG.json.bak-20261109`). File re-read after write + row counts vs sweep.
