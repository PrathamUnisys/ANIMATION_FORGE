import os
import json
import hashlib
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from backend.database import DatabaseManager

class ComfyUIAdapter:
    def __init__(self, root_dir: str, db: DatabaseManager):
        self.root_dir = root_dir
        self.db = db
        self.installed_models: List[Dict[str, Any]] = [
            {
                "model_name": "flux1-dev-fp8.safetensors",
                "version": "1.0-fp8",
                "type": "checkpoint",
                "file_location": "models/checkpoints/flux1-dev-fp8.safetensors",
                "required_nodes": ["KSampler", "CLIPTextEncode", "VAEDecode", "SaveImage"],
                "vram_required_gb": 12,
                "license": "Flux-Dev Non-Commercial / Commercial API"
            },
            {
                "model_name": "ip-adapter-plus_sdxl_vit-h.safetensors",
                "version": "2.0",
                "type": "ipadapter",
                "file_location": "models/ipadapter/ip-adapter-plus_sdxl_vit-h.safetensors",
                "required_nodes": ["IPAdapterUnifiedLoader", "IPAdapterAdvanced"],
                "vram_required_gb": 4,
                "license": "Apache-2.0"
            },
            {
                "model_name": "wan2.1-i2v-14b-480p.safetensors",
                "version": "2.1",
                "type": "video_diffusion",
                "file_location": "models/diffusion_models/wan2.1-i2v-14b-480p.safetensors",
                "required_nodes": ["WanImageToVideo", "VHS_VideoCombine"],
                "vram_required_gb": 14,
                "license": "Apache-2.0"
            }
        ]
        self.installed_nodes = {
            "KSampler", "CLIPTextEncode", "VAEDecode", "SaveImage", "LoadImage",
            "IPAdapterUnifiedLoader", "IPAdapterAdvanced", "WanImageToVideo", "VHS_VideoCombine"
        }

    def check_connection_health(self, endpoint: str = "http://127.0.0.1:8188", local_daemon_running: bool = False) -> Dict[str, Any]:
        status = "CONNECTED" if local_daemon_running else "UNCONFIGURED_OFFLINE"
        now = datetime.now(timezone.utc).isoformat().replace("+00:00","Z")
        with self.db.get_connection() as conn:
            conn.execute(
                """INSERT OR REPLACE INTO integrations
                   (integration_id, name, category, endpoint, version, health_status, last_health_check, capabilities_json, permissions_json)
                   VALUES ('INT_COMFYUI', 'ComfyUI Local Graph Server', 'IMAGE_VIDEO_AUDIO_3D', ?, '0.3.14', ?, ?, ?, ?)""",
                (
                    endpoint,
                    status,
                    now,
                    json.dumps(["txt2img", "img2img", "character_turnaround", "background_gen", "storyboard_gen", "img2vid"]),
                    json.dumps(["DRAFT_CREATION", "LOCAL_MODIFICATION"])
                )
            )
            conn.commit()
        return {"integration_id": "INT_COMFYUI", "endpoint": endpoint, "health_status": status, "checked_at": now}

    def validate_workflow(self, workflow_json: Dict[str, Any]) -> Dict[str, Any]:
        missing_nodes = []
        missing_models = []
        known_model_names = {m["model_name"] for m in self.installed_models}

        for node_id, node_data in workflow_json.get("nodes", {}).items():
            ctype = node_data.get("class_type")
            if ctype not in self.installed_nodes:
                missing_nodes.append(ctype)
            inputs = node_data.get("inputs", {})
            if "ckpt_name" in inputs and inputs["ckpt_name"] not in known_model_names:
                missing_models.append(inputs["ckpt_name"])

        return {
            "valid": len(missing_nodes) == 0 and len(missing_models) == 0,
            "missing_nodes": missing_nodes,
            "missing_models": missing_models
        }

    def submit_workflow_and_record_provenance(
        self,
        project_id: str,
        asset_id: str,
        asset_name: str,
        asset_type: str,
        creation_agent: str,
        workflow_json: Dict[str, Any],
        prompt: str,
        negative_prompt: str,
        seed: int,
        input_references: List[str],
        output_rel_path: str,
        output_bytes: bytes,
        character_id: Optional[str] = None,
        scene_refs: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        val = self.validate_workflow(workflow_json)
        if not val["valid"]:
            raise ValueError(f"ComfyUI workflow validation failed: {val}")

        # Determine next revision without ever overwriting an existing revision
        with self.db.get_connection() as conn:
            row = conn.execute("SELECT current_revision, approval_status FROM assets WHERE asset_id = ?", (asset_id,)).fetchone()
            next_rev = (row["current_revision"] + 1) if row else 1

        # Ensure revision number is embedded in filename so prior revisions are preserved
        base, ext = os.path.splitext(output_rel_path)
        versioned_rel_path = f"{base}_v{next_rev:02d}{ext}"
        full_out_path = os.path.join(self.root_dir, versioned_rel_path)
        os.makedirs(os.path.dirname(full_out_path), exist_ok=True)
        with open(full_out_path, "wb") as f:
            f.write(output_bytes)

        # Save reproducible workflow JSON beside output
        wf_manifest_path = f"{base}_v{next_rev:02d}_workflow_manifest.json"
        now = datetime.now(timezone.utc).isoformat().replace("+00:00","Z")
        file_hash = hashlib.sha256(output_bytes).hexdigest()
        manifest = {
            "asset_id": asset_id,
            "revision": next_rev,
            "workflow_json": workflow_json,
            "model_ids": ["flux1-dev-fp8.safetensors"],
            "model_versions": ["1.0-fp8"],
            "prompt": prompt,
            "negative_prompt": negative_prompt,
            "input_references": input_references,
            "seed": seed,
            "node_versions": {"KSampler": "1.0", "IPAdapterAdvanced": "2.0"},
            "generated_at": now,
            "output_path": versioned_rel_path,
            "file_sha256": file_hash,
            "cost_usd": 0.0,
            "approval_status": "AWAITING_HUMAN_REVIEW"
        }
        with open(os.path.join(self.root_dir, wf_manifest_path), "w", encoding="utf-8") as f:
            json.dump(manifest, f, indent=2)

        with self.db.get_connection() as conn:
            conn.execute(
                """INSERT OR REPLACE INTO assets
                   (asset_id, name, type, description, project_id, character_id, scene_references_json, current_revision, approval_status, license_info, created_at)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?, 'AWAITING_HUMAN_REVIEW', 'Creator Owned / Local Generation', ?)""",
                (
                    asset_id, asset_name, asset_type, f"Generated by {creation_agent}",
                    project_id, character_id, json.dumps(scene_refs or []), next_rev, now
                )
            )
            conn.execute(
                """INSERT INTO asset_revisions
                   (revision_id, asset_id, project_id, revision, file_location, file_sha256, creation_agent, tool_used, provider, model, workflow_json, prompt, negative_prompt, seed, input_references_json, approval_status, created_at)
                   VALUES (?, ?, ?, ?, ?, ?, ?, 'TOOL_COMFYUI_FLUX_IPADAPTER', 'COMFYUI_LOCAL_GRAPH', 'flux1-dev-fp8.safetensors', ?, ?, ?, ?, ?, 'AWAITING_HUMAN_REVIEW', ?)""",
                (
                    f"REV_{asset_id}_V{next_rev:02d}", asset_id, project_id, next_rev,
                    versioned_rel_path, file_hash, creation_agent, json.dumps(workflow_json),
                    prompt, negative_prompt, seed, json.dumps(input_references), now
                )
            )
            conn.commit()
        return manifest
