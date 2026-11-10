# Known Limitations

## Verified before implementation

- No ComfyUI listener or process was detected; requests to `127.0.0.1:8188/system_stats` and `/object_info` timed out. Live generation, model discovery, output retrieval, and visual quality are therefore unverified.
- Current app `ComfyUIAdapter` is a simulation/provenance writer, not a local ComfyUI client. Current Blender/Unreal adapter is not an automated production exporter.
- The only current database screenplay marked `APPROVED` is `SCR_PROJECT_001_V01`, a short fantasy-comedy scene in one throne-room location. Its use exercises characters, props, action, and staging but does not test historical or multi-location environments.
- All ten YouTube experiment scripts and EP10 revision 2 remain draft/proposed; they cannot be used as approved pilot inputs.
- `Ollama` was documented as offline in the current repo snapshot. Initial script analysis therefore cannot depend on live LLM enrichment.
- Repository-prescribed tests currently have a pre-existing red: 30 passed, 1 failed on two CR_007 instruction-validator findings. The validator reports 131 files, 9 rules, and the same 2 findings.

## Scope boundaries

- AI images cannot establish exact 3D geometry, calibrated camera values, or world coordinates. Generated blocking art is illustrative; normalized diagrams are the explicit staging plan.
- Prompt text, seeds, LoRA, IP-Adapter, ControlNet, or a selected reference image do not guarantee identity or visual continuity. Human inspection remains required.
- Workflow compatibility depends on the exact ComfyUI build, checkpoint, node set, model files, and input/output bindings. The module will discover/validate what it can but will not install missing models or custom nodes.
- Licenses vary by checkpoint, LoRA, adapter, and generated content. The module records configured model identifiers but does not clear their use rights.
- Standalone review decisions are local creative decisions. They are not authenticated GovernanceEngine approvals and do not approve the screenplay.
- Blender/Unreal handoff is structured shot intent and references, not a built scene, imported asset, Sequencer, `.blend`, or validated engine coordinate set.

## Validation still required

- Start a local ComfyUI instance and verify health, workflow validation, prompt submission, progress/error handling, image upload and retrieval against the exact configured workflow.
- Generate all art candidates from the common scene; compare whether directions are legible and distinct to a human.
- Generate at least one storyboard and one blocking image from the same approved shot and inspect their references and metadata.
- Test image serving and approval/rejection/regeneration in the local review UI.
- Validate handoff JSON against the existing scene/shot contracts and manually inspect it in the intended DCC.
