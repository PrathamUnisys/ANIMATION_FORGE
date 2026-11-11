from __future__ import annotations

import time
from pathlib import Path
from typing import Any

from .blocking import build_blocking_layout, render_blocking_png, render_blocking_svg
from .comfyui_client import ComfyUIClient, ComfyUIError
from .common import sha256_bytes, utc_now
from .prompt_builder import build_shot_prompt
from .storage import ProjectStore
from .workflows import (
    apply_to_user_workflow,
    txt2img_canny_workflow,
    txt2img_sdxl_lightning_canny_workflow,
    txt2img_sdxl_lightning_workflow,
    txt2img_workflow,
    validate_workflow,
    workflow_settings,
)


class GenerationError(RuntimeError):
    pass


def _record_event(
    store: ProjectStore,
    action: str,
    target_type: str,
    target_id: str,
    actor: str = "operator",
    note: str = "",
    metadata: dict[str, Any] | None = None,
) -> dict[str, Any]:
    from .common import new_id

    event = {
        "event_id": new_id("EVT"),
        "timestamp": utc_now(),
        "actor": actor,
        "action": action,
        "target_type": target_type,
        "target_id": target_id,
        "note": note,
        "metadata": metadata or {},
    }
    store.append_event(event)
    return event


def generate_image(
    client: ComfyUIClient,
    store: ProjectStore,
    *,
    artifact_type: str,
    relative_dir: str,
    prompt: str,
    negative_prompt: str,
    settings: dict[str, Any],
    workflow_id: str,
    shot_id: str = "",
    sequence_id: str = "",
    scene_id: str = "",
    style_bible_sha256: str = "",
    source_script_sha256: str = "",
    control_image_path: Path | None = None,
    control_net_strength: float = 0.8,
    filename_prefix: str = "VisualDev",
    actor: str = "operator",
    user_workflow: dict[str, Any] | None = None,
    user_settings: dict[str, Any] | None = None,
    override_applied: list[str] | None = None,
) -> dict[str, Any]:
    """Submit one workflow to ComfyUI and store the image plus its provenance.

    When a user workflow is supplied it is used as the graph, and only the
    prompt text and the sampling inputs are filled in. Everything the user
    built is preserved and the manifest says the graph was theirs.
    """
    common = {
        "positive": prompt,
        "negative": negative_prompt,
        "model": settings.get("model", "dreamshaper_8.safetensors"),
        "width": int(settings.get("width", 768)),
        "height": int(settings.get("height", 768)),
        "steps": int(settings.get("steps", 25)),
        "cfg": float(settings.get("cfg", 8.0)),
        "sampler": settings.get("sampler", "euler"),
        "scheduler": settings.get("scheduler", "simple"),
        "seed": int(settings.get("seed", 536354036775427)),
        "filename_prefix": filename_prefix,
    }

    reference_images: list[str] = []
    control_net = None
    workflow_source = "BUILT_IN"
    from .presets import template_for

    template = settings.get("workflow_template") or template_for(
        settings.get("preset", ""), str(control_image_path) if control_image_path else None
    )
    if user_workflow is not None:
        filled = apply_to_user_workflow(
            user_workflow,
            positive=prompt,
            negative=negative_prompt,
            # Only the settings the user set by hand go into their own graph.
            settings=user_settings if user_settings is not None else settings,
        )
        workflow = filled["workflow"]
        workflow_source = "USER"
        override_applied = list(override_applied or []) + list(filled["applied"])
        if filled.get("missing"):
            override_applied = list(override_applied) + [
                f"not-applied:{name}" for name in filled["missing"]
            ]
    elif template in ("sdxl_lightning_4step_v1", "sdxl_lightning_4step_canny_v1"):
        # The SDXL four step pipeline has its own VAE and its own settings, so
        # it is built from its own template rather than the 1.5 one.
        sdxl_settings = {
            "model": common["model"],
            "lora": settings.get("lora"),
            "lora_strength": float(settings.get("lora_strength", 1.0)),
            "vae": settings.get("vae") or "sdxl_vae_fp16_fix.safetensors",
            "width": common["width"],
            "height": common["height"],
            "steps": common["steps"],
            "cfg": common["cfg"],
            "sampler": common["sampler"],
            "scheduler": common["scheduler"],
            "seed": common["seed"],
            "filename_prefix": filename_prefix,
        }
        if control_image_path is not None:
            upload = client.upload_image(control_image_path)
            reference_images.append(upload.get("name", control_image_path.name))
            workflow = txt2img_sdxl_lightning_canny_workflow(
                positive=prompt,
                negative=negative_prompt,
                control_image=upload.get("name", control_image_path.name),
                control_net=settings.get("control_net")
                or "diffusers_xl_canny_mid_fp16.safetensors",
                control_strength=control_net_strength,
                **sdxl_settings,
            )
            control_net = settings.get("control_net") or "diffusers_xl_canny_mid_fp16.safetensors"
        else:
            workflow = txt2img_sdxl_lightning_workflow(
                positive=prompt, negative=negative_prompt, **sdxl_settings
            )
    elif control_image_path is not None:
        upload = client.upload_image(control_image_path)
        reference_images.append(upload.get("name", control_image_path.name))
        workflow = txt2img_canny_workflow(
            control_image=upload.get("name", control_image_path.name),
            control_strength=control_net_strength,
            **common,
        )
        control_net = settings.get("control_net", "control_v11p_sd15_canny.pth")
    else:
        lora = settings.get("lora")
        workflow = txt2img_workflow(
            lora=lora,
            lora_strength=float(settings.get("lora_strength", 0.65)),
            **common,
        )

    check = validate_workflow(client, workflow)
    if check["status"] != "PASS":
        raise GenerationError(f"Workflow validation failed: {check}")

    started = time.time()
    try:
        result = client.generate(workflow)
    except ComfyUIError as exc:
        raise GenerationError(str(exc)) from exc
    elapsed = round(time.time() - started, 2)

    if not result["outputs"]:
        raise GenerationError("ComfyUI finished without producing an image output.")

    image_bytes = client.fetch_image(result["outputs"][0])
    resolved = workflow_settings(workflow)

    manifest: dict[str, Any] = {
        "artifact_type": artifact_type,
        "shot_id": shot_id,
        "sequence_id": sequence_id,
        "scene_id": scene_id,
        "prompt": prompt,
        "negative_prompt": negative_prompt,
        "workflow_id": workflow_id,
        "workflow_version": "1.0.0",
        "workflow_source": workflow_source,
        "prompt_overrides_applied": list(override_applied or []),
        "model": resolved.get("model"),
        "lora": resolved.get("lora"),
        "lora_strength": resolved.get("lora_strength"),
        "seed": resolved.get("seed"),
        "width": resolved.get("width"),
        "height": resolved.get("height"),
        "steps": resolved.get("steps"),
        "cfg": resolved.get("cfg"),
        "sampler": resolved.get("sampler"),
        "scheduler": resolved.get("scheduler"),
        "control_net": control_net,
        "reference_images": reference_images,
        "style_bible_sha256": style_bible_sha256,
        "source_script_sha256": source_script_sha256,
        "comfyui_prompt_id": result["prompt_id"],
        "comfyui_output": result["outputs"][0],
        "generation_seconds": elapsed,
        "status": "GENERATED",
        "review_status": "PENDING",
        "created_at": utc_now(),
    }
    manifest = {key: value for key, value in manifest.items() if value is not None}
    image_path, manifest_path = store.write_generation_artifact(
        relative_dir, image_bytes, manifest, ".png"
    )
    manifest = store.read(manifest_path)
    _record_event(
        store,
        "NOTE",
        artifact_type,
        shot_id or manifest["generation_id"],
        actor=actor,
        note="Image generated by ComfyUI",
        metadata={
            "generation_id": manifest["generation_id"],
            "image_path": image_path,
            "prompt_id": result["prompt_id"],
            "seed": manifest.get("seed"),
            "model": manifest.get("model"),
        },
    )
    return {
        "status": "PASS",
        "generation_id": manifest["generation_id"],
        "image_path": image_path,
        "manifest_path": manifest_path,
        "image_sha256": manifest["image_sha256"],
        "bytes": len(image_bytes),
        "prompt_id": result["prompt_id"],
        "seed": manifest.get("seed"),
        "model": manifest.get("model"),
        "elapsed_sec": elapsed,
        "workflow_source": workflow_source,
        "applied_overrides": list(override_applied or []),
    }


def write_blocking_layout(
    store: ProjectStore,
    shot: dict[str, Any],
    scene: dict[str, Any],
    sequence: dict[str, Any],
    relative_dir: str,
) -> dict[str, Any]:
    """Write the deterministic normalized staging layout (JSON + SVG + PNG)."""
    layout = build_blocking_layout(shot, scene)
    layout["sequence_id"] = sequence["sequence_id"]
    version = store.latest_number(relative_dir, "layout")
    stem = f"{relative_dir.rstrip('/')}/layout_v{version:03d}"
    store.write_json(f"{stem}.json", layout)
    store.write_bytes(f"{stem}.svg", render_blocking_svg(layout).encode("utf-8"))
    store.write_bytes(f"{stem}.png", render_blocking_png(layout))
    return {
        "status": "PASS",
        "layout_path": f"{stem}.json",
        "svg_path": f"{stem}.svg",
        "png_path": f"{stem}.png",
        "layout": layout,
    }


def blocking_png_path(store: ProjectStore, relative_dir: str) -> str | None:
    """Find the newest blocking PNG for a shot directory."""
    folder = store.path(relative_dir)
    if not folder.exists():
        return None
    candidates = sorted(folder.glob("layout_v*.png"))
    if not candidates:
        return None
    return f"{relative_dir.rstrip('/')}/{candidates[-1].name}"
