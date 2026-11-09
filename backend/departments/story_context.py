"""CR_006 M1: Versioned Series Bible + Episode Brief + Context assembly.

Design: one DB row per revision, status lifecycle:
  PROPOSED (AI) -> DRAFT (human editable) -> IN_REVIEW -> APPROVED (canon)
  APPROVED revisions are immutable; REJECTED/SUPERSEDED are terminal.
AI-generated content can never become APPROVED without an explicit human
transition via the approval path (see StoryContextService.approve_bible).

No dual source of truth: characters/environments remain in their tables;
Bible content references them by ID.
"""
import hashlib
import json
import os
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from backend.database import DatabaseManager


def canonical_hash(obj: Any) -> str:
    raw = json.dumps(obj, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(raw).hexdigest()


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


BIBLE_STATUSES = {"PROPOSED", "DRAFT", "IN_REVIEW", "APPROVED", "REJECTED", "SUPERSEDED"}
BIBLE_TRANSITIONS = {
    "PROPOSED": {"DRAFT", "REJECTED"},
    "DRAFT": {"IN_REVIEW", "PROPOSED"},
    "IN_REVIEW": {"APPROVED", "REJECTED", "DRAFT"},
    "APPROVED": {"SUPERSEDED"},
    "REJECTED": set(),
    "SUPERSEDED": set(),
}


class BibleTransitionError(Exception):
    pass


class StoryContextService:
    def __init__(self, root_dir: str, db: DatabaseManager):
        self.root_dir = root_dir
        self.db = db

    # ---- Series Bible ----

    def create_bible(self, series_id: str, content: Dict[str, Any], project_id: Optional[str] = None,
                     status: str = "DRAFT", created_by: str = "HUMAN_OWNER",
                     rights_status: str = "NOT_REQUIRED") -> Dict[str, Any]:
        if status not in BIBLE_STATUSES:
            raise ValueError(f"Invalid bible status {status}")
        if status == "APPROVED":
            raise BibleTransitionError("New Bibles cannot be created directly as APPROVED. Use PROPOSED/DRAFT then human approve.")
        content_hash = canonical_hash(content)
        now = now_iso()
        with self.db.get_connection() as conn:
            row = conn.execute("SELECT MAX(revision) AS m FROM story_bibles WHERE series_id = ?", (series_id,)).fetchone()
            next_rev = (row["m"] or 0) + 1
            rev_id = f"BIBLE_{series_id}_R{next_rev:03d}"
            conn.execute(
                """INSERT INTO story_bibles
                   (bible_revision_id, series_id, project_id, revision, previous_revision, status,
                    content_json, content_hash_sha256, provenance_json, rights_review_status, created_by, created_at)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                (
                    rev_id, series_id, project_id, next_rev, next_rev - 1 if next_rev > 1 else None,
                    status, json.dumps(content, indent=2), content_hash,
                    json.dumps({"created_by": created_by, "status": status}),
                    rights_status, created_by, now,
                ),
            )
            conn.execute(
                """INSERT INTO story_bible_heads (series_id, project_id, head_revision, head_status, updated_at)
                   VALUES (?, ?, ?, ?, ?)
                   ON CONFLICT(series_id) DO UPDATE SET head_revision=excluded.head_revision,
                       head_status=excluded.head_status, updated_at=excluded.updated_at""",
                (series_id, project_id, next_rev, status, now),
            )
            # Mirror into series.bible_json (legacy readable surface) without deleting history
            conn.execute(
                "UPDATE series SET bible_json = ? WHERE series_id = ?",
                (json.dumps(content), series_id),
            )
            conn.commit()
        return {"bible_revision_id": rev_id, "series_id": series_id, "revision": next_rev, "status": status, "content_hash_sha256": content_hash}

    def revise_bible(self, series_id: str, content: Dict[str, Any], created_by: str,
                     status: str = "DRAFT") -> Dict[str, Any]:
        if status == "APPROVED":
            raise BibleTransitionError("Revisions cannot be created as APPROVED. Submit IN_REVIEW then human-approve.")
        with self.db.get_connection() as conn:
            head = conn.execute("SELECT head_revision, head_status FROM story_bible_heads WHERE series_id = ?", (series_id,)).fetchone()
            if not head:
                raise KeyError(f"No Bible head for series {series_id}")
            if head["head_status"] == "APPROVED":
                # Never overwrite approved head: new revision supersedes via status flow
                pass
        return self.create_bible(series_id=series_id, content=content, status=status, created_by=created_by)

    def get_bible(self, series_id: str, revision: Optional[int] = None) -> Dict[str, Any]:
        with self.db.get_connection() as conn:
            if revision is None:
                row = conn.execute(
                    "SELECT sb.* FROM story_bibles sb JOIN story_bible_heads h ON sb.series_id=h.series_id AND sb.revision=h.head_revision WHERE sb.series_id = ?",
                    (series_id,),
                ).fetchone()
            else:
                row = conn.execute("SELECT * FROM story_bibles WHERE series_id = ? AND revision = ?", (series_id, revision)).fetchone()
            if not row:
                raise KeyError(f"Bible not found for series {series_id} revision {revision}")
            d = dict(row)
            d["content"] = json.loads(d.pop("content_json"))
            d["provenance"] = json.loads(d.pop("provenance_json"))
            return d

    def list_bible_revisions(self, series_id: str) -> List[Dict[str, Any]]:
        with self.db.get_connection() as conn:
            rows = conn.execute("SELECT * FROM story_bibles WHERE series_id = ? ORDER BY revision DESC", (series_id,)).fetchall()
            out = []
            for r in rows:
                d = dict(r)
                d["content"] = json.loads(d.pop("content_json", "{}"))
                d.pop("provenance_json", None)
                out.append(d)
            return out

    def transition_bible(self, bible_revision_id: str, new_status: str, actor: str, human_confirmed: bool = False) -> Dict[str, Any]:
        if new_status not in BIBLE_STATUSES:
            raise ValueError(f"Invalid status {new_status}")
        with self.db.get_connection() as conn:
            row = conn.execute("SELECT * FROM story_bibles WHERE bible_revision_id = ?", (bible_revision_id,)).fetchone()
            if not row:
                raise KeyError(f"Bible revision {bible_revision_id} not found")
            cur = row["status"]
            if cur == "APPROVED" and new_status != "SUPERSEDED":
                raise BibleTransitionError("APPROVED Bible is immutable; only SUPERSEDED via new revision is allowed.")
            if new_status not in BIBLE_TRANSITIONS[cur]:
                raise BibleTransitionError(f"Illegal Bible transition {cur} -> {new_status}")
            if new_status == "APPROVED" and not human_confirmed:
                raise BibleTransitionError("APPROVED requires human_confirmed=True via the Windows reviewer path. AI cannot approve canon.")
            conn.execute("UPDATE story_bibles SET status = ? WHERE bible_revision_id = ?", (new_status, bible_revision_id))
            # If this is the head revision, update head status
            head = conn.execute("SELECT head_revision FROM story_bible_heads WHERE series_id = ?", (row["series_id"],)).fetchone()
            if head and head["head_revision"] == row["revision"]:
                conn.execute("UPDATE story_bible_heads SET head_status = ?, updated_at = ? WHERE series_id = ?", (new_status, now_iso(), row["series_id"]))
            conn.commit()
            return {"bible_revision_id": bible_revision_id, "from": cur, "to": new_status, "actor": actor}

    def get_approved_canon(self, series_id: str) -> Optional[Dict[str, Any]]:
        with self.db.get_connection() as conn:
            row = conn.execute(
                "SELECT * FROM story_bibles WHERE series_id = ? AND status = 'APPROVED' ORDER BY revision DESC LIMIT 1", (series_id,)
            ).fetchone()
            if not row:
                return None
            d = dict(row)
            d["content"] = json.loads(d.pop("content_json"))
            return d

    # ---- Episode Brief ----

    def create_brief(self, project_id: str, content: Dict[str, Any], episode_id: Optional[str] = None,
                     series_id: Optional[str] = None, status: str = "DRAFT", created_by: str = "HUMAN_OWNER") -> Dict[str, Any]:
        if status == "APPROVED":
            raise BibleTransitionError("Briefs cannot be created as APPROVED.")
        if content.get("primary_genre_id"):
            self._validate_genre_selection(content)
        content_hash = canonical_hash(content)
        now = now_iso()
        ep_id = episode_id or content.get("episode_id") or f"EP_{project_id}"
        with self.db.get_connection() as conn:
            row = conn.execute(
                "SELECT MAX(revision) AS m FROM episode_briefs WHERE project_id = ? AND episode_id = ?", (project_id, ep_id)
            ).fetchone()
            next_rev = (row["m"] or 0) + 1
            brief_id = f"BRIEF_{project_id}_{ep_id}_R{next_rev:03d}"
            conn.execute(
                """INSERT INTO episode_briefs
                   (brief_revision_id, project_id, episode_id, series_id, revision, previous_revision, status,
                    content_json, content_hash_sha256, created_by, created_at)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                (
                    brief_id, project_id, ep_id, series_id, next_rev, next_rev - 1 if next_rev > 1 else None,
                    status, json.dumps(content, indent=2), content_hash, created_by, now,
                ),
            )
            conn.commit()
        return {"brief_revision_id": brief_id, "project_id": project_id, "episode_id": ep_id, "revision": next_rev, "content_hash_sha256": content_hash}

    def get_brief(self, project_id: str, episode_id: str, revision: Optional[int] = None) -> Dict[str, Any]:
        with self.db.get_connection() as conn:
            if revision is None:
                row = conn.execute(
                    "SELECT * FROM episode_briefs WHERE project_id = ? AND episode_id = ? ORDER BY revision DESC LIMIT 1",
                    (project_id, episode_id),
                ).fetchone()
            else:
                row = conn.execute(
                    "SELECT * FROM episode_briefs WHERE project_id = ? AND episode_id = ? AND revision = ?", (project_id, episode_id, revision)
                ).fetchone()
            if not row:
                raise KeyError(f"Brief not found for {project_id}/{episode_id}")
            d = dict(row)
            d["content"] = json.loads(d.pop("content_json"))
            return d

    def _validate_genre_selection(self, brief: Dict[str, Any]):
        reg_path = os.path.join(self.root_dir, "GENRES", "REGISTRY.json")
        with open(reg_path, encoding="utf-8") as f:
            reg = json.load(f)
        valid = {p["genre_id"] for p in reg.get("profiles", []) if p.get("status") == "ACTIVE"}
        primary = brief.get("primary_genre_id")
        if primary not in valid:
            raise ValueError(f"Unknown/inactive primary_genre_id {primary!r}. Valid: {sorted(valid)}")
        secondaries = brief.get("secondary_genre_ids") or []
        if len(secondaries) != len(set(secondaries)):
            raise ValueError("Duplicate secondary_genre_ids")
        for s in secondaries:
            if s not in valid:
                raise ValueError(f"Unknown/inactive secondary genre {s!r}")
        channel = brief.get("channel_style_id")
        if channel is not None:
            ch_path = os.path.join(self.root_dir, "STYLES", "CHANNELS.json")
            with open(ch_path, encoding="utf-8") as f:
                ch = json.load(f)
            valid_ch = {c.get("style_id") or c.get("channel_id") for c in ch.get("channels", [])}
            if valid_ch and channel not in valid_ch:
                raise ValueError(f"Unknown channel_style_id {channel!r}")
            # If channels list is empty, any value is rejected as unknown
            if not valid_ch:
                raise ValueError(f"Unknown channel_style_id {channel!r} (channel registry empty)")

    # ---- Context assembly (DOCS/SCREENPLAY_CONTEXT_ASSEMBLY.md) ----

    CONTEXT_ASSEMBLY_VERSION = "1.1.0"

    def assemble_context(self, project_id: str, episode_id: str, series_id: Optional[str] = None,
                         primary_genre_id: Optional[str] = None, secondary_genre_ids: Optional[List[str]] = None,
                         channel_style_id: Optional[str] = None) -> Dict[str, Any]:
        with self.db.get_connection() as conn:
            proj = conn.execute("SELECT * FROM projects WHERE project_id = ?", (project_id,)).fetchone()
            if not proj:
                raise KeyError(f"Project {project_id} not found")
            proj = dict(proj)
            brief_row = conn.execute(
                "SELECT * FROM episode_briefs WHERE project_id = ? AND episode_id = ? ORDER BY revision DESC LIMIT 1",
                (project_id, episode_id),
            ).fetchone()
            if brief_row is None:
                raise KeyError(f"No Episode Brief for {project_id}/{episode_id}; create one before assembling context.")
            brief_row = dict(brief_row)
            brief_status = brief_row.get("status")
            brief_content = json.loads(brief_row.pop("content_json"))
            brief_row["content"] = brief_content
        # Genre/channel selection comes from the brief unless explicitly overridden.
        # No silent Fantasy fallback; no fabricated channel profile.
        primary_genre_id = primary_genre_id or brief_content.get("primary_genre_id")
        if not primary_genre_id:
            raise ValueError("No primary_genre_id in brief or request; genre cannot be inferred.")
        if secondary_genre_ids is None:
            secondary_genre_ids = brief_content.get("secondary_genre_ids") or []
        if channel_style_id is None:
            channel_style_id = brief_content.get("channel_style_id")  # may be None (channel-neutral)
        # Validate genre/channel
        self._validate_genre_selection({
            "primary_genre_id": primary_genre_id,
            "secondary_genre_ids": secondary_genre_ids,
            "channel_style_id": channel_style_id,
        })
        # Load profiles with hashes (never fabricate a channel profile)
        def genre_profile(genre_id: str) -> Dict[str, Any]:
            reg_path = os.path.join(self.root_dir, "GENRES", "REGISTRY.json")
            with open(reg_path, encoding="utf-8") as f:
                reg = json.load(f)
            prof = next((p for p in reg["profiles"] if p["genre_id"] == genre_id), None)
            if not prof:
                raise ValueError(f"Profile {genre_id} not in registry")
            ppath = os.path.join(self.root_dir, prof["instruction_path"])
            raw = open(ppath, "rb").read() if os.path.exists(ppath) else b""
            return {
                "profile_id": genre_id, "version": prof["version"],
                "content_hash_sha256": hashlib.sha256(raw).hexdigest(),
                "source_path": prof["instruction_path"],
                "instruction_text": raw.decode("utf-8", errors="ignore")[:4000],
            }

        def channel_profile(style_id: str) -> Dict[str, Any]:
            ch_path = os.path.join(self.root_dir, "STYLES", "CHANNELS.json")
            with open(ch_path, encoding="utf-8") as f:
                ch = json.load(f)
            entry = next((c for c in ch.get("channels", []) if (c.get("style_id") or c.get("channel_style_id") or c.get("channel_id")) == style_id), None)
            if entry is None:
                raise ValueError(f"Channel style {style_id!r} is not registered (registry has {len(ch.get('channels',[]))} entries); report NOT_REGISTERED instead of fabricating.")
            guide = entry.get("guide_path", "")
            raw = open(os.path.join(self.root_dir, guide), "rb").read() if guide and os.path.exists(os.path.join(self.root_dir, guide)) else b""
            return {
                "profile_id": style_id, "version": entry.get("version", "1.0.0"),
                "content_hash_sha256": hashlib.sha256(raw).hexdigest(),
                "source_path": guide or "STYLES/CHANNELS.json",
                "instruction_text": raw.decode("utf-8", errors="ignore")[:4000],
            }

        primary = genre_profile(primary_genre_id)
        secondaries = [genre_profile(s) for s in secondary_genre_ids]
        channel = channel_profile(channel_style_id) if channel_style_id else None
        canon_row = self.get_approved_canon(series_id) if series_id else None
        sw_path = os.path.join(self.root_dir, "AGENTS", "SCREENWRITER", "INSTRUCTION.md")
        sw_raw = open(sw_path, "rb").read() if os.path.exists(sw_path) else b""
        sw_ref = {"profile_id": "AGENT_SCREENWRITER", "version": "1.0.0",
                  "content_hash_sha256": hashlib.sha256(sw_raw).hexdigest(), "source_path": "AGENTS/SCREENWRITER/INSTRUCTION.md",
                  "instruction_text": sw_raw.decode("utf-8", errors="ignore")[:4000]}
        # Immutable, hashable context package (timestamps excluded from hash)
        project_ctx = {
            "project_id": project_id, "title": proj.get("title"), "synopsis": proj.get("synopsis"),
            "creative_brief": proj.get("creative_brief"), "target_audience": proj.get("target_audience"),
            "intended_runtime_sec": proj.get("intended_runtime_sec"), "language": proj.get("language"),
            "visual_direction": proj.get("visual_direction"), "restrictions_json": proj.get("restrictions_json"),
        }
        episode_ctx = {
            "episode_id": episode_id, "brief_revision_id": brief_row["brief_revision_id"],
            "brief_revision": brief_row["revision"], "brief_status": brief_status,
            "brief_content": brief_content,
        }
        series_ctx = {
            "series_id": series_id,
            "bible_revision_id": canon_row["bible_revision_id"] if canon_row else None,
            "bible_revision": canon_row["revision"] if canon_row else None,
            "canon_content": canon_row["content"] if canon_row else None,
            "canon_content_hash_sha256": canon_row["content_hash_sha256"] if canon_row else None,
        }
        profile_ctx = {
            "primary_genre": {"profile_id": primary["profile_id"], "version": primary["version"], "content_hash_sha256": primary["content_hash_sha256"], "source_path": primary["source_path"]},
            "secondary_genres": [{"profile_id": s["profile_id"], "version": s["version"], "content_hash_sha256": s["content_hash_sha256"], "source_path": s["source_path"]} for s in secondaries],
            "channel_style": ({"profile_id": channel["profile_id"], "version": channel["version"], "content_hash_sha256": channel["content_hash_sha256"], "source_path": channel["source_path"]} if channel else None),
            "screenwriter_instruction": {"profile_id": sw_ref["profile_id"], "version": sw_ref["version"], "content_hash_sha256": sw_ref["content_hash_sha256"], "source_path": sw_ref["source_path"]},
        }
        prompt_context_text = "\n\n".join([
            f"PROJECT:\n{json.dumps(project_ctx)[:2500]}",
            f"SERIES_CANON_APPROVED:\n{json.dumps(series_ctx['canon_content'] or {})[:3500]}",
            f"EPISODE_BRIEF:\n{json.dumps(episode_ctx['brief_content'])[:4000]}",
            f"PRIMARY_GENRE:\n{primary['instruction_text'][:2000]}",
            f"SECONDARY_GENRES:\n" + "\n\n".join(s["instruction_text"][:1000] for s in secondaries),
            f"CHANNEL_STYLE:\n{(channel['instruction_text'][:1000] if channel else 'NONE (channel-neutral)')}",
            f"SCREENWRITER:\n{sw_ref['instruction_text'][:2000]}",
        ])
        manifest = {
            "project_id": project_id,
            "context_version": self.CONTEXT_ASSEMBLY_VERSION,
            "primary_genre": profile_ctx["primary_genre"],
            "secondary_genres": profile_ctx["secondary_genres"],
            "channel_style": profile_ctx["channel_style"],
            "screenwriter_instruction": profile_ctx["screenwriter_instruction"],
            "project_sources": [{"source_type": "PROJECT_BRIEF", "source_id": project_id, "revision_or_hash": project_ctx["synopsis"][:64]}] + (
                [{"source_type": "STORY_BIBLE", "source_id": f"{series_id}/r{canon_row['revision']}", "revision_or_hash": canon_row["content_hash_sha256"]}] if canon_row else []
            ),
            "assembled_at": now_iso(),
        }
        package_for_hash = {
            "project": project_ctx,
            "episode": episode_ctx,
            "series": series_ctx,
            "profiles": profile_ctx,
            "context_version": self.CONTEXT_ASSEMBLY_VERSION,
        }
        manifest["context_hash_sha256"] = canonical_hash(package_for_hash)
        return {
            "manifest": manifest,
            "package": package_for_hash,
            "prompt_context_text": prompt_context_text,
            "project": proj,
            "brief": brief_content,
            "brief_hash": brief_row["content_hash_sha256"],
            "brief_revision_id": brief_row["brief_revision_id"],
            "canon": series_ctx["canon_content"],
            "canon_hash": series_ctx["canon_content_hash_sha256"],
            "canon_revision_id": series_ctx["bible_revision_id"],
            "profiles": {"primary": primary, "secondaries": secondaries, "channel": channel, "screenwriter": sw_ref},
        }
