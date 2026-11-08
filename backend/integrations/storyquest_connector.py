import os
import json
from datetime import datetime
from typing import Any, Dict, List
from backend.database import DatabaseManager


class StoryQuestConnector:
    """
    PART 23: Versioned integration interface between Animation Forge and StoryQuest Studio.
    Maintains strict separation of responsibilities: Animation Forge reports task/deliverable/approval/milestone
    events and never duplicates XP, streaks, or gamification logic.
    Supports standalone operation and JSON event export/import when StoryQuest is offline.
    """
    def __init__(self, root_dir: str, db: DatabaseManager):
        self.root_dir = root_dir
        self.db = db
        self.event_outbox: List[Dict[str, Any]] = []

    def emit_deliverable_event(
        self,
        event_type: str,
        project_id: str,
        episode_id: str,
        task_id: str,
        asset_id: str,
        approved: bool = False
    ) -> Dict[str, Any]:
        if event_type == "deliverable.ready_for_review":
            payload = {
                "event": "deliverable.ready_for_review",
                "project_id": project_id,
                "episode_id": episode_id,
                "task_id": task_id,
                "asset_id": asset_id,
                "status": "awaiting_approval"
            }
        elif event_type == "deliverable.approved":
            payload = {
                "event": "deliverable.approved",
                "project_id": project_id,
                "episode_id": episode_id,
                "task_id": task_id,
                "asset_id": asset_id,
                "approved": bool(approved)
            }
        else:
            raise ValueError(f"Unsupported StoryQuest event type: {event_type}")

        self.event_outbox.append(payload)
        outbox_path = os.path.join(self.root_dir, "PROJECTS", project_id, "LOGS", "storyquest_event_outbox.json")
        os.makedirs(os.path.dirname(outbox_path), exist_ok=True)
        with open(outbox_path, "w", encoding="utf-8") as f:
            json.dump(self.event_outbox, f, indent=2)
        return payload
