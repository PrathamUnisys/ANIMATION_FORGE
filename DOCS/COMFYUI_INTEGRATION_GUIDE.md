# ComfyUI First-Class Integration Guide

`ComfyUIAdapter` (`backend/integrations/comfyui_adapter.py`) connects to local or secure remote ComfyUI instances (`http://127.0.0.1:8188`).
- **Pre-Flight Validation**: Verifies every `class_type` node and checkpoint/IP-Adapter model file against the actual installed inventory before submitting to `/prompt`.
- **Reproducibility Manifest**: Saves `<asset>_vXX_workflow_manifest.json` containing the full node graph, model versions, prompt, negative prompt, seed, SHA-256 hash, and input references alongside every generated asset.
- **Honest Offline Status**: When no ComfyUI daemon is reachable on port 8188, Integration Manager reports `UNCONFIGURED_OFFLINE` rather than faking a live connection.
