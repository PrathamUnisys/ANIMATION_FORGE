# Phase 0 Technical Research & Ecosystem Verification

## Verified Official Integrations & Specifications (November 2026)
1. **Tauri 2.0 Sidecar**: Verified external binary packaging via `bundle.externalBin` in `tauri.conf.json` ([Tauri Sidecar Docs](https://v2.tauri.app/develop/sidecar/)).
2. **Model Context Protocol (MCP)**: Verified official Python SDK (`mcp`) supporting `STDIO` and `Streamable HTTP` transports ([MCP Python SDK](https://py.sdk.modelcontextprotocol.io/) and [MCP Transports Specification](https://modelcontextprotocol.io/specification/2025-11-25/basic/transports)).
3. **ComfyUI Server API**: Verified HTTP `/prompt`, `/history`, `/system_stats` and WebSocket `/ws` endpoints ([ComfyUI Server Routes](https://docs.comfy.org/development/comfyui-server/comms_routes)).
4. **Blender Headless Scripting**: Verified `bpy` 5.2 LTS wheel & unattended CLI flag execution `blender --background --python <script> --` ([PyPI bpy](https://pypi.org/project/bpy/)).
5. **Unreal Engine 5 Python & Sequencer**: Verified `unreal.LevelSequence`, `unreal.SequencerTools`, and Remote Control API ([Unreal Python Sequencer Docs](https://dev.epicgames.com/documentation/unreal-engine/python-scripting-in-sequencer-in-unreal-engine)).
6. **ElevenLabs TTS v3/v4**: Verified `stability`, `similarity_boost`, `style`, `speed`, and `pronunciation_dictionary_locators` ([ElevenLabs TTS Docs](https://elevenlabs.io/docs/overview/capabilities/text-to-speech)).
