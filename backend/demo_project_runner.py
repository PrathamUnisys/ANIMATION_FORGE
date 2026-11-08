import os
import json
from datetime import datetime, timezone
from typing import Any, Dict
from backend.database import DatabaseManager
from backend.governance.rule_loader import GovernanceEngine
from backend.governance.approval_engine import ApprovalEngine
from backend.providers.manager import ProviderManager
from backend.orchestration.agent_executor import AgentExecutor
from backend.departments.story_pipeline import StoryAndScreenplayPipeline
from backend.rnd.research_engine import ProductionRndEngine
from backend.integrations.mcp_gateway import AnimationForgeMcpGateway
from backend.integrations.comfyui_adapter import ComfyUIAdapter
from backend.departments.production_studios import CreativeProductionStudios
from backend.integrations.blender_unreal_adapters import SafeBlenderAndUnrealAdapter
from backend.qc.quality_controller import QualityControlEngine
from backend.integrations.storyquest_connector import StoryQuestConnector
from backend.integrations.plugin_manager import PluginManager


def run_forgotten_kingdom_e2e_project(root_dir: str, db_path: str) -> Dict[str, Any]:
    """
    Executes the complete 12-step end-to-end acceptance demonstration project:
    'The Forgotten Kingdom' (PROJECT_001) with explicit human approval gates at every stage.
    """
    db = DatabaseManager(db_path)
    governance = GovernanceEngine(root_dir, db)
    approvals = ApprovalEngine(db)
    providers = ProviderManager(db)
    executor = AgentExecutor(root_dir, db, governance, approvals, providers)
    story_pipe = StoryAndScreenplayPipeline(root_dir, db, approvals)
    rnd_engine = ProductionRndEngine(root_dir, db, approvals)
    mcp_gateway = AnimationForgeMcpGateway(db)
    comfyui = ComfyUIAdapter(root_dir, db)
    studios = CreativeProductionStudios(root_dir, db, approvals, comfyui)
    blender_adapter = SafeBlenderAndUnrealAdapter(root_dir, db, approvals)
    qc_engine = QualityControlEngine(db)
    storyquest = StoryQuestConnector(root_dir, db)
    plugin_mgr = PluginManager(root_dir, db)

    project_id = "PROJECT_001"
    now = datetime.now(timezone.utc).isoformat().replace("+00:00","Z")

    # Step 0: Create Project & Story Bible
    with db.get_connection() as conn:
        conn.execute(
            """INSERT OR REPLACE INTO projects
               (project_id, title, synopsis, genre, target_audience, intended_runtime_sec, language, creative_brief, visual_direction, animation_technique, production_goals_json, restrictions_json, status, current_stage, active_mode, series_id, created_at, updated_at)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 'ACTIVE', 'COMPLETED_PRODUCTION_PACKAGE', 'PRODUCTION_MODE', 'SER_ELDORIA', ?, ?)""",
            (
                project_id,
                "The Forgotten Kingdom",
                "An earnest squire and his sarcastic slime familiar accidentally awaken an ancient bureaucratic Stone Golem while polishing a rusted royal crown, crowning the slime King of Eldoria.",
                "Fantasy Comedy",
                "Teen & Young Adult (13+)",
                45,
                "en-US",
                "High-contrast 2.5D illustrated fantasy citadel with expressive character acting and deadpan bureaucratic comedy.",
                "Charcoal gothic stonework, warm amber god-rays, emerald slime subsurface scattering, hand-inked rim highlights.",
                "HYBRID",
                json.dumps(["Complete 45-second pilot short", "Verify 100% character consistency across 4 shots", "Export OTIO timeline + SRT subtitles"]),
                json.dumps(["No automatic creative approvals", "Zero unapproved third-party plugins"]),
                now, now
            )
        )
        conn.execute(
            "INSERT OR REPLACE INTO series (series_id, title, bible_json, created_at) VALUES ('SER_ELDORIA', 'Chronicles of Eldoria', ?, ?)",
            (json.dumps({"world_rules": ["Royal crowns bind to whichever creature touches them after buffing", "Golems enforce tax law"]}), now)
        )
        conn.execute(
            "INSERT OR REPLACE INTO episodes (episode_id, project_id, series_id, episode_number, title, animation_technique, status, created_at) VALUES ('EP001', ?, 'SER_ELDORIA', 1, 'Crown & Foreclosure', 'HYBRID', 'COMPLETED', ?)",
            (project_id, now)
        )
        conn.commit()

    # Step 1: Story & 13-Pass Screenplay Development + Human Screenplay Approval Gate #1
    script_res = story_pipe.develop_screenplay_revision(
        project_id=project_id,
        title="The Forgotten Kingdom",
        premise="Squire Sir Pip and slime Gloop polish a cursed crown and trigger a Stone Golem bailiff.",
        genre="Fantasy Comedy",
        target_audience="Teen & Young Adult (13+)",
        intended_duration_sec=45,
        tone=None  # Let AI propose and mark creative assumption
    )
    storyquest.emit_deliverable_event("deliverable.ready_for_review", project_id, "EP001", "TASK_SCRIPT_001", script_res["script_id"])
    approvals.submit_human_decision(
        approval_id=script_res["approval_id"],
        decision="APPROVED",
        human_user_id="HUMAN_EXEC_PRODUCER",
        comments="Approved v1 screenplay. Comedic timing on King Gloop coronation is spot on.",
        rationale_for_memory="Approved 3-act 45s screenplay structure with 4 shots."
    )
    storyquest.emit_deliverable_event("deliverable.approved", project_id, "EP001", "TASK_SCRIPT_001", script_res["script_id"], approved=True)

    # Step 2: Production Requirement & Scene Breakdown
    breakdown_res = story_pipe.generate_production_breakdown(project_id, script_res["script_id"])

    # Step 3: Mandatory Online Tool Research & R&D
    rnd_res = rnd_engine.run_mandatory_project_rnd(project_id, script_res["script_id"], online_available=True)
    poc_res = rnd_engine.execute_authorized_poc(project_id, "TOOL_COMFYUI_FLUX_IPADAPTER", human_authorized=True, estimated_cost_usd=0.0, download_mb=0.0)

    # Step 4: Human Toolchain Approval Gate #2 -> Generates APPROVED_TOOLCHAIN.json
    toolchain_profile = rnd_engine.approve_and_lock_toolchain(
        project_id=project_id,
        selected_tool_ids=["TOOL_COMFYUI_FLUX_IPADAPTER", "TOOL_BLENDER_HEADLESS_5_2", "TOOL_ELEVENLABS_TTS_V3", "TOOL_KOKORO_LOCAL_TTS"],
        human_user_id="HUMAN_EXEC_PRODUCER",
        cost_limit_usd=15.0,
        rationale="Selected local ComfyUI Flux+IPAdapter for character lock, Blender 5.2 LTS for 2.5D parallax camera, and ElevenLabs/Kokoro TTS."
    )

    # Step 5: Character Design Studio (Sir Pip, Gloop, Stone Golem) + Human Approval
    char_pip = studios.register_and_generate_character(
        project_id=project_id,
        character_id="CHAR_SIR_PIP",
        name="Sir Pip of Turnipshire",
        role="Protagonist Squire",
        bible_data={"age": 21, "personality": "Earnest, optimistic, legally oblivious", "costume": "Oversized dented steel pauldrons over patched tunic"},
        visual_locks={"eyes": "hazel_wide", "hair": "tousled_chestnut", "pauldrons": "asymmetric_dented_left", "palette": ["#1E293B", "#D4AF37", "#38BDF8"]},
        voice_profile={"pitch": "bright_tenor", "cadence": "eager_heroic"},
        palette_rgb=[(20, 28, 44), (212, 175, 55), (56, 189, 248)]
    )
    approvals.submit_human_decision(char_pip["approval_id"], "APPROVED", "HUMAN_EXEC_PRODUCER", "Locked Sir Pip turnaround & dented pauldron identity.", "Locked Sir Pip visual identity.")

    char_gloop = studios.register_and_generate_character(
        project_id=project_id,
        character_id="CHAR_GLOOP",
        name="King Gloop the Gelatinous",
        role="Deuteragonist Slime Familiar",
        bible_data={"age": 300, "personality": "Deadpan, cynical, secretly regal", "accessories": "Brass monocle & Crown of Eldoria"},
        visual_locks={"body": "translucent_emerald_dome", "accessory": "brass_monocle_right", "palette": ["#064E3B", "#10B981", "#FACC15"]},
        voice_profile={"pitch": "dry_baritone_blorp", "cadence": "sarcastic_deadpan"},
        palette_rgb=[(12, 42, 36), (16, 185, 129), (250, 204, 21)]
    )
    approvals.submit_human_decision(char_gloop["approval_id"], "APPROVED", "HUMAN_EXEC_PRODUCER", "Approved Gloop emerald translucency and monocle.", "Locked Gloop visual identity.")

    char_golem = studios.register_and_generate_character(
        project_id=project_id,
        character_id="CHAR_STONE_GOLEM",
        name="Bailiff Granite-IX",
        role="Antagonist Bureaucratic Golem",
        bible_data={"age": 1200, "personality": "Monotone tax collector", "accessories": "Chiseled basalt clipboard"},
        visual_locks={"body": "mossy_basalt_blocks", "eyes": "glowing_amber_runes", "palette": ["#1F2937", "#F59E0B", "#4ADE80"]},
        voice_profile={"pitch": "sub_bass_echo", "cadence": "robotic_statute_reader"},
        palette_rgb=[(28, 32, 38), (245, 158, 11), (74, 222, 128)]
    )
    approvals.submit_human_decision(char_golem["approval_id"], "APPROVED", "HUMAN_EXEC_PRODUCER", "Approved Stone Golem proportions.", "Locked Stone Golem visual identity.")

    # Step 6: Environment Studio + Human Approval
    env_throne = studios.register_and_generate_environment(
        project_id=project_id,
        location_id="LOC_THRONE_ROOM",
        name="Forgotten Citadel Throne Room",
        environment_type="INT_RUINED_CASTLE_2_5D",
        bible_data={"architecture": "Mossy gothic arches", "lighting": "Amber morning god-rays", "layers": ["FG_Pillars", "MG_Throne_Dais", "BG_Vaulted_Ruins"]}
    )
    approvals.submit_human_decision(env_throne["approval_id"], "APPROVED", "HUMAN_EXEC_PRODUCER", "Approved 2.5D multi-plane throne room plate.", "Locked LOC_THRONE_ROOM for reuse across SCN_001 and SCN_002.")

    # Step 7: Audio Studio + Human Approval
    audio_pkg = studios.generate_audio_production_package(project_id, "SCN_001", provider_id="LOCAL_KOKORO_TTS")
    for line in audio_pkg["lines"]:
        approvals.submit_human_decision(line["approval_id"], "APPROVED", "HUMAN_EXEC_PRODUCER", f"Approved voice line {line['line_id']}")

    # Step 8: Storyboard, Camera & Previs Animatic + Mandatory Animatic Gate #3 Approval
    sb_res = studios.generate_storyboards_and_animatic(project_id)
    for shot in sb_res["shots"]:
        approvals.submit_human_decision(shot["approval_id"], "APPROVED", "HUMAN_EXEC_PRODUCER", f"Approved storyboard panel {shot['shot_id']}")
    approvals.submit_human_decision(
        sb_res["animatic_approval_id"],
        "APPROVED",
        "HUMAN_EXEC_PRODUCER",
        "Animatic pacing and 45s timing approved for full animation production.",
        "Approved Animatic Gate #3."
    )

    # Step 9 & 10: Animation Engine (Safe Blender Adapter) & Post-Production Assembly
    anim_post_res = blender_adapter.execute_animation_and_post_production(project_id, sb_res["animatic_approval_id"])

    # Step 11: 5-Stage Quality Control Engine
    qc_reports = qc_engine.run_full_5_stage_qc(project_id)

    # Step 12: Final Human Approval Gate #4
    storyquest.emit_deliverable_event("deliverable.ready_for_review", project_id, "EP001", "TASK_FINAL_001", anim_post_res["final_package_id"])
    approvals.submit_human_decision(
        anim_post_res["final_approval_id"],
        "APPROVED",
        "HUMAN_EXEC_PRODUCER",
        "Final Episode 1 package approved for release.",
        "Completed final human approval for The Forgotten Kingdom."
    )
    storyquest.emit_deliverable_event("deliverable.approved", project_id, "EP001", "TASK_FINAL_001", anim_post_res["final_package_id"], approved=True)

    # Register & evaluate sample OTIO plugin and ComfyUI health status
    with open(os.path.join(root_dir, "PLUGINS/EXAMPLES/open_timeline_exporter/manifest.json"), "r", encoding="utf-8") as f:
        plg_manifest = json.load(f)
    plugin_mgr.register_discovered_plugin(plg_manifest)
    plugin_mgr.transition_plugin_state("PLG_OTIO_TIMELINE_EXPORTER", "EVALUATED")
    plugin_mgr.transition_plugin_state("PLG_OTIO_TIMELINE_EXPORTER", "APPROVED_FOR_INSTALLATION", human_authorized=True)
    plugin_mgr.transition_plugin_state("PLG_OTIO_TIMELINE_EXPORTER", "INSTALLED", human_authorized=True)
    plugin_mgr.transition_plugin_state("PLG_OTIO_TIMELINE_EXPORTER", "ENABLED", human_authorized=True)

    comfyui.check_connection_health("http://127.0.0.1:8188", local_daemon_running=False)

    return {
        "project_id": project_id,
        "script": script_res,
        "breakdown": breakdown_res,
        "rnd": rnd_res,
        "poc": poc_res,
        "toolchain": toolchain_profile,
        "characters": [char_pip, char_gloop, char_golem],
        "environment": env_throne,
        "audio": audio_pkg,
        "storyboard_animatic": sb_res,
        "animation_post": anim_post_res,
        "qc_reports": qc_reports,
        "storyquest_events": storyquest.event_outbox
    }
