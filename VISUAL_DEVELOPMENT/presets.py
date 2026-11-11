"""Generation presets: the pipelines a user can choose from.

A preset is a named set of models and sampling settings that are known to
work together on this machine. It exists so that the choice of pipeline is a
decision the user makes, not a set of numbers buried in a workflow file.

The presets here were measured on this machine: an RTX 4060 with 8 GB of video
memory and 12 GB of RAM, running ComfyUI 0.34.2 locally.
"""

from __future__ import annotations

from typing import Any

# The pipeline templates, by id.
TEMPLATE_SD15 = "txt2img_v1"
TEMPLATE_SD15_CANNY = "txt2img_canny_v1"
TEMPLATE_SDXL = "sdxl_lightning_4step_v1"
TEMPLATE_SDXL_CANNY = "sdxl_lightning_4step_canny_v1"

PRESETS: list[dict[str, Any]] = [
    {
        "preset_id": "sd15_dreamshaper",
        "label": "SD 1.5 - DreamShaper 8",
        "note": "The original pipeline. Small, quick, and the one every pilot image was made with.",
        "template": TEMPLATE_SD15,
        "canny_template": TEMPLATE_SD15_CANNY,
        "model": "dreamshaper_8.safetensors",
        "lora": "arcane_offset.safetensors",
        "lora_strength": 0.65,
        "vae": "",
        "width": 768,
        "height": 768,
        "steps": 25,
        "cfg": 8.0,
        "sampler": "euler",
        "scheduler": "simple",
        "control_net": "control_v11p_sd15_canny.pth",
        "measured": "about 8 s per 768x768 image",
        "vram_note": "under 2 GB of video memory",
    },
    {
        "preset_id": "sdxl_lightning_4step",
        "label": "SDXL - Lightning 4 step",
        "note": "Far better looking, at 1024x1024, in four steps. Recommended for boards.",
        "template": TEMPLATE_SDXL,
        "canny_template": TEMPLATE_SDXL_CANNY,
        "model": "sd_xl_base_1.0.safetensors",
        "lora": "sdxl_lightning_4step_lora.safetensors",
        "lora_strength": 1.0,
        "vae": "sdxl_vae_fp16_fix.safetensors",
        "width": 1024,
        "height": 1024,
        "steps": 4,
        "cfg": 1.0,
        "sampler": "euler",
        "scheduler": "sgm_uniform",
        "control_net": "diffusers_xl_canny_mid_fp16.safetensors",
        "measured": "about 16 s per 1024x1024 image, including the model load",
        "vram_note": "about 2.4 GB of extra video memory on an 8 GB card",
    },
]

PRESETS_BY_ID: dict[str, dict[str, Any]] = {preset["preset_id"]: preset for preset in PRESETS}


def get_preset(preset_id: str) -> dict[str, Any] | None:
    return PRESETS_BY_ID.get(preset_id)


def preset_settings(preset_id: str) -> dict[str, Any]:
    """The generation settings a preset implies."""
    preset = PRESETS_BY_ID.get(preset_id)
    if preset is None:
        return {}
    settings = {
        "model": preset["model"],
        "lora": preset["lora"],
        "lora_strength": preset["lora_strength"],
        "width": preset["width"],
        "height": preset["height"],
        "steps": preset["steps"],
        "cfg": preset["cfg"],
        "sampler": preset["sampler"],
        "scheduler": preset["scheduler"],
        "control_net": preset["control_net"],
        "preset": preset_id,
    }
    if preset.get("vae"):
        settings["vae"] = preset["vae"]
    return settings


def template_for(preset_id: str, control_image: str | None = None) -> str:
    """The workflow template a preset uses, with or without conditioning."""
    preset = PRESETS_BY_ID.get(preset_id)
    if preset is None:
        return TEMPLATE_SD15_CANNY if control_image else TEMPLATE_SD15
    if control_image:
        return preset["canny_template"]
    return preset["template"]


def preset_summary() -> list[dict[str, Any]]:
    """The presets, in the shape the application shows them."""
    return [
        {
            "preset_id": preset["preset_id"],
            "label": preset["label"],
            "note": preset["note"],
            "model": preset["model"],
            "width": preset["width"],
            "height": preset["height"],
            "steps": preset["steps"],
            "cfg": preset["cfg"],
            "sampler": preset["sampler"],
            "scheduler": preset["scheduler"],
            "measured": preset["measured"],
            "vram_note": preset["vram_note"],
        }
        for preset in PRESETS
    ]
