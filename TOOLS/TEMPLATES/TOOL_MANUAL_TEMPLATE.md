---
prompt_id: TOOL_MANUAL_TEMPLATE
version: 1.0.0
modified_date: 2026-11-09
description: Reusable operational manual template for an installable or hosted production tool
dependencies: ["TOOLS_INDEX"]
change_history:
  - version: 1.0.0
    date: 2026-11-09
    summary: Standardize tool setup, connection, use and troubleshooting documentation
---
# Tool Manual Template

When creating a real manual, replace the front-matter `prompt_id` with the stable `TOOL_<TOOL_ID>` ID. Add the same tool ID and matching manual path to `TOOLS/CATALOG.json`.

## Identity and verification

- Tool ID / name: [Stable ID and display name]
- Category / supported tasks: [Categories and task tags]
- Official website / documentation: [Official URLs]
- Supported OS and version: [Verified]
- Current local status: [NOT_VERIFIED / NOT_INSTALLED / INSTALLED / CONNECTED / CONFIGURATION_REQUIRED / BLOCKED]
- Last verified: [Timestamp, machine and verification evidence]

## Installation and location

- Installation method: [Official procedure]
- Default location by OS: [Known defaults, explicitly labelled]
- Executable discovery: [How to locate and verify]
- Version command or UI location: [Exact check]
- Prerequisites and hardware: [Requirements]
- Uninstall/update notes: [Non-destructive procedure]

## Connection and configuration

- Connection type: [Local process / REST / WebSocket / hosted API / plugin]
- Default endpoint or protocol: [Documented default, not assumed live]
- Configuration location: [Local config reference; no secret values]
- Authentication method: [Credential reference only]
- Startup/shutdown: [Exact procedure]
- Health check: [Actual test and expected result]

## How to use

- Supported tasks and limitations: [Verified capabilities]
- Inputs and formats: [Formats]
- Outputs and formats: [Formats]
- Minimal test workflow: [Small reproducible example]
- Production workflow: [Steps and expected artifacts]
- Provenance to capture: [Tool/version/settings/workflow/hash]

## Debugging and recovery

| Symptom | Likely cause | Diagnostic | Fix / recovery |
|---|---|---|---|
| [Symptom] | [Cause] | [Command/log] | [Steps] |

Include log locations, port conflicts, GPU/runtime issues, model/node mismatch, common startup errors and known version-specific problems.

## Limits and operational notes

- What this tool does not do: [Explicit boundaries]
- Data/privacy/licence constraints: [References]
- Known incompatibilities: [Details]
- Escalation / useful diagnostics: [Details]

## Verification history

| Date | Machine / OS | Version | Test performed | Result / evidence |
|---|---|---|---|---|
| [Date] | [Machine] | [Version] | [Test] | [Result] |
