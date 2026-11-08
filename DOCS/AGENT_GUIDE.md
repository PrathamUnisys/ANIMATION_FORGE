# Specialized AI Production Agents Guide

Animation Forge coordinates 16 specialized department agents plus the `PRODUCTION_DIRECTOR`:
- **Story & Script**: `STORY_ARCHITECT`, `SCREENWRITER`, `SCRIPT_CRITIC`, `SCRIPT_BREAKDOWN`
- **World & Design**: `WORLD_ARCHITECT`, `CHARACTER_ARCHITECT`, `CHARACTER_DESIGNER`, `ENVIRONMENT_DESIGNER`
- **R&D**: `RESEARCH_ANALYST`
- **Audio & Previs**: `AUDIO_DIRECTOR`, `STORYBOARD_DIRECTOR`, `CAMERA_DIRECTOR`, `PREVIS_DIRECTOR`
- **Animation, Post & QC**: `ANIMATION_ENGINEER`, `VIDEO_EDITOR`, `QUALITY_CONTROLLER`

Every agent operates inside a strict filesystem sandbox (`AgentExecutor.resolve_safe_project_path`) and emits outputs validated against `SCHEMAS/AGENT.schema.json`.
