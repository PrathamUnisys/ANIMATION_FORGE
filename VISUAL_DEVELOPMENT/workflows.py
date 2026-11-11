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


def txt2img_sdxl_lightning_workflow(
    *,
    positive: str,
    negative: str = DEFAULT_NEGATIVE,
    model: str = "sd_xl_base_1.0.safetensors",
    lora: str | None = "sdxl_lightning_4step_lora.safetensors",
    lora_strength: float = 1.0,
    vae: str = "sdxl_vae_fp16_fix.safetensors",
    width: int = 1024,
    height: int = 1024,
    steps: int = 4,
    cfg: float = 1.0,
    sampler: str = "euler",
    scheduler: str = "sgm_uniform",
    seed: int = 536354036775427,
    filename_prefix: str = "VisualDev",
) -> dict[str, Any]:
    """Build an API-format SDXL workflow that runs in four steps.

    The distilled checkpoint is far better than the 1.5 model it replaces, but
    it needs its own settings: four steps, a guidance of one and the
    sgm_uniform scheduler. The VAE is loaded separately because the stock SDXL
    VAE overflows in half precision, and the overflow shows as a black image
    rather than as an error.

    Measured on an 8 GB card: 1024x1024 in about sixteen seconds, using
    roughly 2.4 GB of extra video memory.
    """
    workflow: dict[str, Any] = {
        "1": {"class_type": "CheckpointLoaderSimple", "inputs": {"ckpt_name": model}},
        "3": {"class_type": "CLIPTextEncode", "inputs": {"text": positive, "clip": ["1", 1]}},
        "4": {"class_type": "CLIPTextEncode", "inputs": {"text": negative, "clip": ["1", 1]}},
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
        "7": {"class_type": "VAELoader", "inputs": {"vae_name": vae}},
        "8": {"class_type": "VAEDecode", "inputs": {"samples": ["6", 0], "vae": ["7", 0]}},
        "9": {
            "class_type": "SaveImage",
            "inputs": {"images": ["8", 0], "filename_prefix": filename_prefix},
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


def txt2img_sdxl_lightning_canny_workflow(
    *,
    positive: str,
    negative: str = DEFAULT_NEGATIVE,
    control_image: str,
    control_net: str = "diffusers_xl_canny_mid_fp16.safetensors",
    control_strength: float = 0.8,
    low_threshold: float = 0.4,
    high_threshold: float = 0.8,
    **kwargs: Any,
) -> dict[str, Any]:
    """The SDXL four-step workflow with Canny conditioning on a layout."""
    workflow = txt2img_sdxl_lightning_workflow(positive=positive, negative=negative, **kwargs)
    workflow["10"] = {"class_type": "LoadImage", "inputs": {"image": control_image}}
    workflow["11"] = {
        "class_type": "Canny",
        "inputs": {
            "image": ["10", 0],
            "low_threshold": low_threshold,
            "high_threshold": high_threshold,
        },
    }
    workflow["12"] = {
        "class_type": "ControlNetLoader",
        "inputs": {"control_net_name": control_net},
    }
    workflow["13"] = {
        "class_type": "ControlNetApplyAdvanced",
        "inputs": {
            "positive": ["3", 0],
            "negative": ["4", 0],
            "control_net": ["12", 0],
            "image": ["11", 0],
            "vae": ["7", 0],
            "strength": control_strength,
            "start_percent": 0.0,
            "end_percent": 1.0,
        },
    }
    workflow["6"]["inputs"]["positive"] = ["13", 0]
    workflow["6"]["inputs"]["negative"] = ["13", 1]
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
        elif node.get("class_type") == "VAELoader":
            settings["vae"] = inputs.get("vae_name")
        elif node.get("class_type") == "ControlNetLoader":
            settings["control_net"] = inputs.get("control_net_name")
    return settings


# ------------------------------------------------------- user supplied graphs

# The node that turns text into conditioning. A user workflow may hold several
# of them, so the positive and the negative one are found by following the
# links out of the sampler rather than by guessing.
TEXT_NODE_CLASSES = ("CLIPTextEncode", "CLIPTextEncodeSDXL", "CLIPTextEncodeSDXLRefiner")
SAMPLER_NODE_CLASSES = ("KSampler", "KSamplerAdvanced", "SamplerCustom", "SamplerCustomAdvanced")
LATENT_NODE_CLASSES = ("EmptyLatentImage", "EmptySD3LatentImage", "EmptyLatentImagePresets")

# Conditioning nodes that pass a text conditioning through to the sampler. A
# ControlNet sits between the text and the sampler in most real graphs, so the
# text node has to be found by walking back through them.
CONDITIONING_PASSTHROUGH = {
    "ControlNetApply": ("positive",),
    "ControlNetApplyAdvanced": ("positive", "negative"),
    "ConditioningSetArea": ("conditioning",),
    "ConditioningSetAreaPercentage": ("conditioning",),
    "ConditioningSetTimestepRange": ("conditioning",),
    "ConditioningCombine": ("conditioning_1", "conditioning_2"),
    "ConditioningConcat": ("conditioning_to", "conditioning_from"),
    "ConditioningSetAreaStrength": ("conditioning",),
    "FluxGuidance": ("conditioning",),
    "DisableNoise": ("conditioning",),
}


def _link_target(link: Any) -> str | None:
    """Return the node id a ComfyUI link points at."""
    if isinstance(link, (list, tuple)) and link and isinstance(link[0], str):
        return link[0]
    return None


def _walk_to_text_node(
    workflow: dict[str, Any],
    node_id: str | None,
    direction: str = "positive",
    seen: set[str] | None = None,
) -> str | None:
    """Follow the conditioning back to the text node that feeds it.

    The sampler usually does not point at the text node directly: a
    ControlNet, a guidance node or a conditioning operation sits in between.
    Guessing by node order would put the prompt into the wrong node, so the
    graph is walked instead, and the walk keeps the direction it came from:
    the negative conditioning of a ControlNet is not the positive one.

    A graph that does not resolve returns None rather than a guess.
    """
    if not node_id or node_id not in workflow:
        return None
    node = workflow[node_id]
    if node.get("class_type") in TEXT_NODE_CLASSES:
        return node_id
    seen = seen if seen is not None else set()
    if node_id in seen:
        return None
    seen.add(node_id)
    class_type = node.get("class_type", "")
    inputs = node.get("inputs", {})
    names = CONDITIONING_PASSTHROUGH.get(class_type)
    if names is None:
        names = [
            name
            for name, value in inputs.items()
            if _link_target(value) is not None
        ]
    else:
        # The input that matches the direction is tried first.
        names = sorted(names, key=lambda name: 0 if name == direction else 1)
    for name in names:
        target = _link_target(inputs.get(name))
        if target is None:
            continue
        found = _walk_to_text_node(workflow, target, direction, seen)
        if found is not None:
            return found
    return None


def resolve_prompt_nodes(workflow: dict[str, Any]) -> dict[str, str | None]:
    """Find the positive text node, the negative text node and the latent node.

    The graph is followed the way ComfyUI follows it: from the sampler back
    to the nodes that feed it. Guessing by node order would break on any
    workflow the user built themselves, and would put the prompt into the
    negative node of a graph with a ControlNet in it.
    """
    sampler_id: str | None = None
    for node_id, node in workflow.items():
        if node.get("class_type") in SAMPLER_NODE_CLASSES:
            sampler_id = node_id
            break

    positive_id: str | None = None
    negative_id: str | None = None
    latent_id: str | None = None

    if sampler_id is not None:
        inputs = workflow[sampler_id].get("inputs", {})
        positive_id = _walk_to_text_node(
            workflow, _link_target(inputs.get("positive")), "positive"
        )
        negative_id = _walk_to_text_node(
            workflow, _link_target(inputs.get("negative")), "negative"
        )
        latent_id = _link_target(inputs.get("latent_image"))

    text_nodes = [
        node_id
        for node_id, node in workflow.items()
        if node.get("class_type") in TEXT_NODE_CLASSES
    ]
    if positive_id is None and len(text_nodes) == 1:
        positive_id = text_nodes[0]
    if negative_id is None and len(text_nodes) == 2 and positive_id == text_nodes[0]:
        negative_id = text_nodes[1]

    if latent_id is not None and latent_id not in workflow:
        latent_id = None

    return {
        "sampler": sampler_id,
        "positive": positive_id,
        "negative": negative_id,
        "latent": latent_id,
    }


def apply_to_user_workflow(
    workflow: dict[str, Any],
    *,
    positive: str,
    negative: str,
    settings: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Return a copy of a user workflow with the prompt and settings applied.

    Everything the user built is preserved. Only the text inputs and the
    sampling and size inputs are replaced, and only where the graph actually
    has them.
    """
    import copy

    result = copy.deepcopy(workflow)
    nodes = resolve_prompt_nodes(result)
    applied: list[str] = []
    missing: list[str] = []

    positive_id = nodes["positive"]
    if positive_id and positive_id in result:
        result[positive_id].setdefault("inputs", {})["text"] = positive
        applied.append(f"text:{positive_id}")

    negative_id = nodes["negative"]
    if negative_id and negative_id in result:
        result[negative_id].setdefault("inputs", {})["text"] = negative
        applied.append(f"text:{negative_id}")

    settings = settings or {}
    sampler_id = nodes["sampler"]
    if sampler_id and sampler_id in result:
        inputs = result[sampler_id].setdefault("inputs", {})
        mapping = {
            "seed": "seed",
            "steps": "steps",
            "cfg": "cfg",
            "sampler": "sampler_name",
            "scheduler": "scheduler",
        }
        for key, input_name in mapping.items():
            if settings.get(key) is None:
                continue
            # KSamplerAdvanced calls the seed noise_seed.
            for candidate in (input_name, "noise_seed" if input_name == "seed" else ""):
                if candidate and candidate in inputs:
                    inputs[candidate] = settings[key]
                    applied.append(f"{candidate}:{sampler_id}")
                    break
            else:
                if input_name == "seed":
                    # The graph has no seed input at all. Say so rather than
                    # dropping the value silently.
                    missing.append("seed")

    latent_id = nodes["latent"]
    if latent_id and latent_id in result:
        inputs = result[latent_id].setdefault("inputs", {})
        for key, input_name in (("width", "width"), ("height", "height")):
            if settings.get(key) is not None and input_name in inputs:
                inputs[input_name] = settings[key]
                applied.append(f"{input_name}:{latent_id}")

    # A model, a LoRA and a VAE are only applied where the graph has the
    # node for them. A graph that loads its own keeps its own.
    for node in result.values():
        class_type = node.get("class_type")
        inputs = node.setdefault("inputs", {})
        if class_type == "CheckpointLoaderSimple" and settings.get("model"):
            inputs["ckpt_name"] = settings["model"]
            applied.append(f"ckpt_name:{node.get('_meta', {}).get('title', 'checkpoint')}")
        elif class_type == "LoraLoader" and settings.get("lora"):
            inputs["lora_name"] = settings["lora"]
            applied.append("lora_name")
        elif class_type == "VAELoader" and settings.get("vae"):
            inputs["vae_name"] = settings["vae"]
            applied.append("vae_name")
        elif class_type == "ControlNetLoader" and settings.get("control_net"):
            inputs["control_net_name"] = settings["control_net"]
            applied.append("control_net_name")

    return {"workflow": result, "applied": applied, "nodes": nodes, "missing": missing}


def validate_user_workflow(
    client: ComfyUIClient,
    workflow: dict[str, Any],
) -> dict[str, Any]:
    """Validate a user supplied API-format workflow against the live server.

    On top of the node and input checks the built-in validator performs, this
    reports whether the graph can actually take a prompt: a workflow with no
    text node has nothing to write the prompt into.
    """
    report = validate_workflow(client, workflow)
    nodes = resolve_prompt_nodes(workflow)
    report["prompt_nodes"] = nodes
    report["can_take_prompt"] = nodes["positive"] is not None
    if nodes["positive"] is None:
        report["status"] = "FAIL"
        report.setdefault("errors", []).append(
            "No CLIPTextEncode node is reachable from the sampler, so the workflow "
            "cannot take a prompt."
        )
    return report

