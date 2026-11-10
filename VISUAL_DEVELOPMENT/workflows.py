from __future__ import annotations

from typing import Any

from .comfyui_client import ComfyUIClient

WORKFLOW_TXT2IMG = "txt2img_v1"
WORKFLOW_TXT2IMG_CANNY = "txt2img_canny_v1"

DEFAULT_NEGATIVE = (
    "extra characters, inconsistent character design, changing outfit, unreadable composition, "
    "watermark, text, logo, low resolution, blurry, poor anatomy, extra limbs, missing hands, "
    "cropped subject"
)


def txt2img_workflow(
    *,
    positive: str,
    negative: str = DEFAULT_NEGATIVE,
    model: str = "dreamshaper_8.safetensors",
    lora: str | None = None,
    lora_strength: float = 0.65,
    width: int = 768,
    height: int = 768,
    steps: int = 25,
    cfg: float = 8.0,
    sampler: str = "euler",
    scheduler: str = "simple",
    seed: int = 536354036775427,
    filename_prefix: str = "VisualDev",
) -> dict[str, Any]:
    """Build an API-format text-to-image workflow.

    Node references use the ComfyUI API convention: ["node_id", output_index].
    """
    workflow: dict[str, Any] = {
        "1": {
            "class_type": "CheckpointLoaderSimple",
            "inputs": {"ckpt_name": model},
        },
        "3": {
            "class_type": "CLIPTextEncode",
            "inputs": {"text": positive, "clip": ["1", 1]},
        },
        "4": {
            "class_type": "CLIPTextEncode",
            "inputs": {"text": negative, "clip": ["1", 1]},
        },
        "5": {
            "class_type": "EmptyLatentImage",
            "inputs": {"width": width, "height": height, "batch_size": 1},
        },
        "6": {
            "class_type": "KSampler",
            "inputs": {
                "model": ["1", 0],
                "positive": ["3", 0],
                "negative": ["4", 0],
                "latent_image": ["5", 0],
                "seed": seed,
                "steps": steps,
                "cfg": cfg,
                "sampler_name": sampler,
                "scheduler": scheduler,
                "denoise": 1.0,
            },
        },
        "7": {
            "class_type": "VAEDecode",
            "inputs": {"samples": ["6", 0], "vae": ["1", 2]},
        },
        "8": {
            "class_type": "SaveImage",
            "inputs": {"images": ["7", 0], "filename_prefix": filename_prefix},
        },
    }
    if lora:
        workflow["2"] = {
            "class_type": "LoraLoader",
            "inputs": {
                "model": ["1", 0],
                "clip": ["1", 1],
                "lora_name": lora,
                "strength_model": lora_strength,
                "strength_clip": lora_strength,
            },
        }
        workflow["3"]["inputs"]["clip"] = ["2", 1]
        workflow["4"]["inputs"]["clip"] = ["2", 1]
        workflow["6"]["inputs"]["model"] = ["2", 0]
    return workflow


def txt2img_canny_workflow(
    *,
    positive: str,
    negative: str = DEFAULT_NEGATIVE,
    model: str = "dreamshaper_8.safetensors",
    control_image: str,
    control_net: str = "control_v11p_sd15_canny.pth",
    control_strength: float = 0.8,
    low_threshold: float = 0.4,
    high_threshold: float = 0.8,
    width: int = 768,
    height: int = 768,
    steps: int = 25,
    cfg: float = 8.0,
    sampler: str = "euler",
    scheduler: str = "simple",
    seed: int = 536354036775427,
    filename_prefix: str = "VisualDev",
) -> dict[str, Any]:
    """Build an API-format workflow with a Canny ControlNet conditioning image."""
    workflow = txt2img_workflow(
        positive=positive,
        negative=negative,
        model=model,
        width=width,
        height=height,
        steps=steps,
        cfg=cfg,
        sampler=sampler,
        scheduler=scheduler,
        seed=seed,
        filename_prefix=filename_prefix,
    )
    workflow["9"] = {"class_type": "LoadImage", "inputs": {"image": control_image}}
    workflow["10"] = {
        "class_type": "Canny",
        "inputs": {
            "image": ["9", 0],
            "low_threshold": low_threshold,
            "high_threshold": high_threshold,
        },
    }
    workflow["11"] = {
        "class_type": "ControlNetLoader",
        "inputs": {"control_net_name": control_net},
    }
    workflow["12"] = {
        "class_type": "ControlNetApplyAdvanced",
        "inputs": {
            "positive": ["3", 0],
            "negative": ["4", 0],
            "control_net": ["11", 0],
            "image": ["10", 0],
            "vae": ["1", 2],
            "strength": control_strength,
            "start_percent": 0.0,
            "end_percent": 1.0,
        },
    }
    workflow["6"]["inputs"]["positive"] = ["12", 0]
    workflow["6"]["inputs"]["negative"] = ["12", 1]
    return workflow


def validate_workflow(client: ComfyUIClient, workflow: dict[str, Any]) -> dict[str, Any]:
    """Check every node class and required input against the live /object_info."""
    info = client.object_info()
    missing_nodes: list[str] = []
    missing_inputs: list[str] = []
    unknown_inputs: list[str] = []
    for node_id, node in workflow.items():
        class_type = node.get("class_type")
        definition = info.get(class_type)
        if definition is None:
            missing_nodes.append(f"{node_id}:{class_type}")
            continue
        required = definition.get("input", {}).get("required", {})
        optional = definition.get("input", {}).get("optional", {})
        provided = node.get("inputs", {})
        for input_name in required:
            if input_name not in provided:
                missing_inputs.append(f"{node_id}:{class_type}.{input_name}")
        for input_name in provided:
            if input_name not in required and input_name not in optional:
                unknown_inputs.append(f"{node_id}:{class_type}.{input_name}")
    return {
        "status": "PASS"
        if not missing_nodes and not missing_inputs and not unknown_inputs
        else "FAIL",
        "missing_nodes": missing_nodes,
        "missing_inputs": missing_inputs,
        "unknown_inputs": unknown_inputs,
    }


def workflow_settings(workflow: dict[str, Any]) -> dict[str, Any]:
    """Extract reproducibility settings from a built workflow."""
    settings: dict[str, Any] = {}
    for node in workflow.values():
        inputs = node.get("inputs", {})
        if node.get("class_type") == "CheckpointLoaderSimple":
            settings["model"] = inputs.get("ckpt_name")
        elif node.get("class_type") == "LoraLoader":
            settings["lora"] = inputs.get("lora_name")
            settings["lora_strength"] = inputs.get("strength_model")
        elif node.get("class_type") == "KSampler":
            settings["seed"] = inputs.get("seed")
            settings["steps"] = inputs.get("steps")
            settings["cfg"] = inputs.get("cfg")
            settings["sampler"] = inputs.get("sampler_name")
            settings["scheduler"] = inputs.get("scheduler")
        elif node.get("class_type") == "EmptyLatentImage":
            settings["width"] = inputs.get("width")
            settings["height"] = inputs.get("height")
        elif node.get("class_type") == "ControlNetLoader":
            settings["control_net"] = inputs.get("control_net_name")
    return settings
