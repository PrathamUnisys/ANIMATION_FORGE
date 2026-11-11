"""Prompt overrides: the user's own text on top of the generated prompt.

The generated prompt is built from the Style Bible and the shot record, and it
is a good prompt. It is not always **the** prompt. A director wants to say
"hold the camera lower", a supervisor wants to drop a module that keeps
fighting the design, and anyone who has spent time in ComfyUI has a workflow
they trust more than a built-in one.

Three layers, each optional, applied in a fixed order:

    1. the generated modules, minus any the user excludes
    2. an optional full replacement of that text
    3. the user's own text, appended

The negative prompt works the same way, and the generation settings (model,
LoRA, steps, CFG, sampler, scheduler, seed, width, height) can be overridden
per target as well.

Everything is recorded. The merged result says which overrides were applied,
and the generation manifest stores the effective prompt, so the handoff can
always explain how an image was produced.
"""

from __future__ import annotations

from typing import Any

from .common import new_id, utc_now

OVERRIDES_FILE = "PROMPTS/prompt_overrides_v001.json"
WORKFLOWS_DIR = "PROMPTS/workflows"

# The kinds of thing a prompt can belong to.
TARGET_KINDS = ("SHOT", "ART_DIRECTION_CANDIDATE")

# The generation settings a user may take over. Anything else in the settings
# is derived from the Style Bible and stays there.
OVERRIDABLE_SETTINGS = (
    "model",
    "lora",
    "lora_strength",
    "vae",
    "width",
    "height",
    "steps",
    "cfg",
    "sampler",
    "scheduler",
    "seed",
    "control_net",
    "preset",
    "workflow_template",
)


def build_override(
    target_id: str,
    kind: str,
    *,
    prompt_extra: str = "",
    prompt_replace: str | None = None,
    negative_extra: str = "",
    exclude_modules: list[str] | None = None,
    settings_override: dict[str, Any] | None = None,
    workflow_id: str | None = None,
    note: str = "",
    actor: str = "operator",
) -> dict[str, Any]:
    """Create one override record."""
    if kind not in TARGET_KINDS:
        raise ValueError(f"Unknown override kind: {kind!r}")
    settings = {
        key: value
        for key, value in (settings_override or {}).items()
        if key in OVERRIDABLE_SETTINGS and value is not None
    }
    unknown = sorted(set(settings_override or {}) - set(OVERRIDABLE_SETTINGS))
    if unknown:
        raise ValueError(f"Settings that cannot be overridden: {unknown}")
    return {
        "override_id": new_id("OVR"),
        "target_id": target_id,
        "kind": kind,
        "prompt_extra": prompt_extra.strip(),
        "prompt_replace": prompt_replace.strip() if prompt_replace else None,
        "negative_extra": negative_extra.strip(),
        "exclude_modules": sorted(set(exclude_modules or [])),
        "settings_override": settings,
        "workflow_id": workflow_id,
        "updated_at": utc_now(),
        "actor": actor,
        "note": note,
    }


def load_overrides(store: Any) -> dict[str, Any]:
    """Read every override, keyed by target id."""
    path = store.path(OVERRIDES_FILE)
    if not path.is_file():
        return {}
    value = store.read(OVERRIDES_FILE)
    if not isinstance(value, dict):
        return {}
    return value.get("overrides", {}) if isinstance(value.get("overrides"), dict) else {}


def save_override(store: Any, override: dict[str, Any]) -> dict[str, Any]:
    """Store one override. Overrides are working state, so they update in place."""
    overrides = load_overrides(store)
    overrides[override["target_id"]] = override
    store.update_json(
        OVERRIDES_FILE,
        {"schema_version": "1.0.0", "updated_at": utc_now(), "overrides": overrides},
    )
    return override


def clear_override(store: Any, target_id: str) -> bool:
    """Remove an override. Returns whether there was one."""
    overrides = load_overrides(store)
    if target_id not in overrides:
        return False
    del overrides[target_id]
    store.update_json(
        OVERRIDES_FILE,
        {"schema_version": "1.0.0", "updated_at": utc_now(), "overrides": overrides},
    )
    return True


def get_override(store: Any, target_id: str) -> dict[str, Any] | None:
    return load_overrides(store).get(target_id)


def _join(parts: list[str]) -> str:
    return ", ".join(part.strip().rstrip(",") for part in parts if part and part.strip())


def effective_prompt(
    built: dict[str, Any],
    override: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Merge the generated prompt with the user's override.

    ``built`` is the output of :func:`VISUAL_DEVELOPMENT.prompt_builder.build_shot_prompt`
    or ``build_candidate_prompt``: it carries the modules and the negative list.
    """
    modules: dict[str, str] = dict(built.get("modules", {}))
    generated_prompt = built.get("prompt", "")
    generated_negative = built.get("negative_prompt", "")
    excluded: list[str] = []
    extra = ""
    replacement = None
    negative_extra = ""
    applied: list[str] = []

    if override:
        excluded = [name for name in override.get("exclude_modules", []) if name in modules]
        for name in excluded:
            modules.pop(name, None)
        replacement = override.get("prompt_replace") or None
        extra = override.get("prompt_extra", "") or ""
        negative_extra = override.get("negative_extra", "") or ""
        if excluded:
            applied.append("exclude_modules")
        if replacement:
            applied.append("prompt_replace")
        if extra:
            applied.append("prompt_extra")
        if negative_extra:
            applied.append("negative_extra")

    if replacement:
        prompt = replacement
    else:
        prompt = _join(list(modules.values()))

    if extra:
        prompt = f"{prompt}, {extra}" if prompt else extra

    negative = generated_negative
    if negative_extra:
        negative = f"{negative}, {negative_extra}" if negative else negative_extra

    return {
        "prompt": prompt,
        "negative_prompt": negative,
        "modules": modules,
        "generated_prompt": generated_prompt,
        "generated_negative_prompt": generated_negative,
        "excluded_modules": excluded,
        "applied_overrides": applied,
        "changed": prompt != generated_prompt or negative != generated_negative,
    }


def effective_settings(
    settings: dict[str, Any],
    override: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Merge the generation settings with the user's override.

    A preset is applied first, because a preset is a coherent set: the
    four-step SDXL pipeline needs its own model, steps, guidance and scheduler
    and does not work with a mixture. Anything the user set by hand is applied
    after it, so a single number can still be changed.
    """
    from .presets import preset_settings

    merged = dict(settings)
    applied: list[str] = []
    if override:
        chosen = (override.get("settings_override") or {}).get("preset")
        if chosen:
            merged.update(preset_settings(chosen))
            applied.append("preset")
        for key, value in (override.get("settings_override") or {}).items():
            if key == "preset" or value is None:
                continue
            merged[key] = value
            applied.append(key)
    return {"settings": merged, "applied_overrides": applied}


def override_summary(store: Any) -> list[dict[str, Any]]:
    """Every override in the project, for the review UI and the handoff."""
    overrides = load_overrides(store)
    return [
        {
            "target_id": target_id,
            "kind": override.get("kind", ""),
            "prompt_extra": override.get("prompt_extra", ""),
            "prompt_replace": override.get("prompt_replace"),
            "negative_extra": override.get("negative_extra", ""),
            "exclude_modules": override.get("exclude_modules", []),
            "settings_override": override.get("settings_override", {}),
            "workflow_id": override.get("workflow_id"),
            "updated_at": override.get("updated_at", ""),
            "actor": override.get("actor", ""),
            "note": override.get("note", ""),
        }
        for target_id, override in sorted(overrides.items())
    ]
