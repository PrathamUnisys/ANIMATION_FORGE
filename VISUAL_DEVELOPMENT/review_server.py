"""Standalone loopback review UI for the Visual Development module.

This is a local creative review tool, not an Animation Forge GovernanceEngine
approval. It serves the real generated files from the project directory and
records append-only review events.
"""

from __future__ import annotations

import json
import mimetypes
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any
from urllib.parse import unquote, urlparse

from .common import contained_path, new_id, utc_now
from .storage import ProjectStore

PAGE_TEMPLATE = """<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<title>Visual Development Review - __PROJECT__</title>
<style>
:root { color-scheme: dark; }
body { margin:0; font-family: "Segoe UI", system-ui, sans-serif; background:#0f1319; color:#dfe6ef; }
header { padding:16px 24px; background:#161c25; border-bottom:1px solid #2a3442; position:sticky; top:0; z-index:5; }
h1 { margin:0 0 4px; font-size:20px; }
.sub { color:#8fa1b8; font-size:13px; }
nav { display:flex; gap:6px; margin-top:10px; flex-wrap:wrap; }
nav button { background:#1e2732; color:#cfe0f2; border:1px solid #34414f; border-radius:6px; padding:7px 14px; cursor:pointer; font-size:13px; }
nav button.active { background:#2f6f8f; border-color:#4f9bc4; color:#fff; }
main { padding:22px 24px 60px; }
section { display:none; }
section.active { display:block; }
h2 { font-size:16px; margin:22px 0 10px; color:#9fd3ef; border-bottom:1px solid #27313d; padding-bottom:6px; }
.card { background:#161c25; border:1px solid #2a3442; border-radius:8px; padding:14px; margin-bottom:14px; }
.grid { display:grid; grid-template-columns:repeat(auto-fill,minmax(280px,1fr)); gap:14px; }
figure { margin:0; background:#11161d; border:1px solid #27313d; border-radius:6px; overflow:hidden; }
figure img { width:100%; display:block; background:#000; }
figure img.broken { background:#3a2020; min-height:120px; }
figcaption { padding:9px 11px; font-size:12px; color:#a9bcd2; }
figcaption b { color:#e8f0f8; display:block; margin-bottom:3px; }
button.act { background:#2f6f8f; color:#fff; border:none; border-radius:5px; padding:6px 11px; cursor:pointer; font-size:12px; margin-top:7px; }
button.act.approve { background:#2f7d4f; }
button.act.reject { background:#8f3a3a; }
button.act.regen { background:#6b5a2f; }
.row { display:flex; gap:18px; flex-wrap:wrap; }
.row > div { flex:1 1 380px; }
pre { background:#11161d; border:1px solid #27313d; border-radius:6px; padding:12px; overflow:auto; font-size:12px; color:#c8d6e6; }
table { width:100%; border-collapse:collapse; font-size:13px; }
th,td { text-align:left; padding:7px 9px; border-bottom:1px solid #27313d; vertical-align:top; }
th { color:#8fa1b8; font-weight:600; }
.pill { display:inline-block; padding:2px 8px; border-radius:10px; font-size:11px; margin-right:6px; }
.PASS,.APPROVED { background:#1f4d33; color:#8fe0b0; }
.FAIL,.REJECTED { background:#5a2626; color:#f0a0a0; }
.PENDING,.DRAFT { background:#4a4126; color:#e8d090; }
.NOT_CHECKED,.REVIEW { background:#26303c; color:#a9bcd2; }
#toast { position:fixed; right:18px; bottom:18px; background:#1e2732; border:1px solid #3d4a59; padding:11px 16px; border-radius:7px; font-size:13px; display:none; }
.banner { display:none; margin:0; padding:11px 24px; background:#5a2626; color:#ffd8d8; border-bottom:1px solid #7a3a3a; font-size:13px; }
</style>
</head>
<body>
<header>
  <h1>Visual Development Review</h1>
  <div class="sub" id="subtitle"></div>
  <nav id="tabs"></nav>
</header>
<div id="banner" class="banner"></div>
<main>
  <section id="tab-overview"></section>
  <section id="tab-artdirection"></section>
  <section id="tab-stylebible"></section>
  <section id="tab-storyboard"></section>
  <section id="tab-blocking"></section>
  <section id="tab-jobs"></section>
</main>
<div id="toast"></div>
<script>
const STATE = __STATE__;
const TABS = [["overview","Overview"],["artdirection","Art Direction"],["stylebible","Style Bible"],["storyboard","Storyboard"],["blocking","Blocking"],["jobs","Generation Monitor"]];
let active = (location.hash || "").replace("#", "");
if (!TABS.some(t => t[0] === active)) active = "overview";

function esc(s){ return String(s ?? "").replace(/[&<>"]/g, c => ({"&":"&amp;","<":"&lt;",">":"&gt;","\\"":"&quot;"}[c])); }
function escAttr(s){ return esc(s).replace(/'/g, "&#39;"); }
function toast(msg){ const t=document.getElementById("toast"); t.textContent=msg; t.style.display="block"; setTimeout(()=>t.style.display="none",3200); }

async function act(action, target_type, target_id, extra){
  const body = Object.assign({action, target_type, target_id}, extra||{});
  const res = await fetch("/api/action", {method:"POST", headers:{"Content-Type":"application/json"}, body:JSON.stringify(body)});
  const data = await res.json();
  toast(data.status === "PASS" ? (data.message || "Done") : ("Failed: " + (data.error||"unknown")));
  if(data.reload){ setTimeout(()=>location.reload(), 900); }
}

// Delegated handler: buttons carry data-act/data-type/data-id instead of inline
// onclick attributes, so no HTML attribute quoting can break the script.
document.addEventListener("click", (e) => {
  const button = e.target && e.target.closest ? e.target.closest("button[data-act]") : null;
  if (!button) return;
  act(button.dataset.act, button.dataset.type, button.dataset.id);
});

// Delegated image-error handler. Image error events do not bubble, so this
// listens in the capture phase. An inline onerror attribute would put a raw
// double quote inside a double-quoted JavaScript string and kill the whole
// script block, which silently blanks this page.
document.addEventListener("error", (e) => {
  const el = e.target;
  if (!el || el.tagName !== "IMG") return;
  el.classList.add("broken");
  el.alt = el.alt || "image unavailable";
}, true);

function render(){
  document.getElementById("subtitle").textContent = STATE.project.project_id + " - source " + STATE.project.source_script.script_id + " (" + STATE.project.source_script.approval_status + ")";
  const approved = STATE.project.source_script.approval_status === "APPROVED";
  const banner = document.getElementById("banner");
  if (!approved) {
    banner.style.display = "block";
    banner.textContent = "EXPLORATION ONLY - the source script is '" + STATE.project.source_script.approval_status + "', not APPROVED. Nothing here is a production-ready package and no decision in this UI is a governance approval.";
  }
  document.getElementById("tabs").innerHTML = TABS.map(([k,l]) => '<button data-tab="'+k+'" class="'+(k===active?"active":"")+'">'+l+'</button>').join("");
  document.querySelectorAll("#tabs button").forEach(b => b.onclick = () => { active=b.dataset.tab; if (location.hash !== "#"+active) location.hash = active; render(); });
  // Only the selected section is visible. Without this the page renders the
  // content but keeps every section hidden, because the stylesheet hides all
  // sections and shows only the ones carrying the active class.
  document.querySelectorAll("main section").forEach(s => s.classList.toggle("active", s.id === "tab-" + active));

  const ov = document.getElementById("tab-overview");
  ov.innerHTML = "<h2>Episode</h2><div class='card'><pre>"+esc(JSON.stringify(STATE.episode,null,2))+"</pre></div>"
    + "<h2>Open questions</h2><div class='card'>" + (STATE.open_questions.length ? "<ul>"+STATE.open_questions.map(q=>"<li>"+esc(q)+"</li>").join("")+"</ul>" : "<p>None recorded.</p>") + "</div>"
    + "<h2>Continuity</h2><div class='card'><pre>"+esc(JSON.stringify(STATE.continuity,null,2))+"</pre></div>";

  const ad = document.getElementById("tab-artdirection");
  ad.innerHTML = "<h2>Comparison scene: "+esc(STATE.candidates.comparison_scene_id)+" (shared by every candidate)</h2>"
    + "<div class='grid'>" + STATE.candidates.candidates.map(c =>
        "<figure><img loading='lazy' src='/media/"+encodeURI(c.image_path||"")+"' alt='"+escAttr(c.style_name||c.candidate_id)+"'>"
        + "<figcaption><b>"+esc(c.candidate_id)+" - "+esc(c.style_name)+"</b>"+esc(c.description)
        + "<br><span class='pill "+ (c.selected?"APPROVED":"DRAFT")+"'>"+(c.selected?"SELECTED":"DRAFT")+"</span>"
        + "<br><button class='act' data-act='SELECT' data-type='ART_DIRECTION_CANDIDATE' data-id='"+c.candidate_id+"'>Select this direction</button>"
        + "</figcaption></figure>").join("") + "</div>";

  const sb = document.getElementById("tab-stylebible");
  sb.innerHTML = STATE.style_bible
    ? "<h2>"+esc(STATE.style_bible.style_identity)+" - Style Bible v"+esc(STATE.style_bible.version)+" ("+esc(STATE.style_bible.status)+")</h2><div class='card'><pre>"+esc(JSON.stringify(STATE.style_bible,null,2))+"</pre></div>"
    : "<p>No Style Bible created yet.</p>";

  const groups = {};
  STATE.shots.forEach(s => { const k = s.sequence_id+" / "+s.scene_id+" "+s.scene_heading; (groups[k]=groups[k]||[]).push(s); });
  let sbhtml = "";
  Object.keys(groups).forEach(k => {
    sbhtml += "<h2>"+esc(k)+"</h2><div class='grid'>" + groups[k].map(s =>
      "<figure><img loading='lazy' src='/media/"+encodeURI(s.image_path||"")+"' alt='"+escAttr(s.shot_id)+"'>"
      + "<figcaption><b>"+esc(s.shot_id)+" - "+esc(s.shot_size)+"</b>"+esc(s.description)
      + "<br><span class='pill "+esc(s.review_status)+"'>"+esc(s.review_status)+"</span>"
      + "<br><button class='act approve' data-act='APPROVE' data-type='STORYBOARD' data-id='"+s.shot_id+"'>Approve</button>"
      + "<button class='act reject' data-act='REJECT' data-type='STORYBOARD' data-id='"+s.shot_id+"'>Reject</button>"
      + "<button class='act regen' data-act='REGENERATE' data-type='STORYBOARD' data-id='"+s.shot_id+"'>Regenerate</button>"
      + "</figcaption></figure>").join("") + "</div>";
  });
  document.getElementById("tab-storyboard").innerHTML = sbhtml || "<p>No shots analysed yet.</p>";

  let blhtml = "";
  Object.keys(groups).forEach(k => {
    blhtml += "<h2>"+esc(k)+"</h2>" + groups[k].map(s =>
      "<div class='card row'><div><b>Storyboard "+esc(s.shot_id)+"</b><br><img style='max-width:100%;border:1px solid #2a3442' src='/media/"+encodeURI(s.image_path||"")+"'></div>"
      + "<div><b>Blocking "+esc(s.shot_id)+"</b><br><img style='max-width:100%;border:1px solid #2a3442' src='/media/"+encodeURI(s.blocking_image_path||"")+"'>"
      + "<br><span class='pill "+esc(s.blocking_review_status||"PENDING")+"'>"+esc(s.blocking_review_status||"PENDING")+"</span>"
      + "<br><button class='act approve' data-act='APPROVE' data-type='BLOCKING' data-id='"+s.shot_id+"'>Approve</button>"
      + "<button class='act reject' data-act='REJECT' data-type='BLOCKING' data-id='"+s.shot_id+"'>Reject</button>"
      + "</div></div>").join("");
  });
  document.getElementById("tab-blocking").innerHTML = blhtml || "<p>No blocking layouts yet.</p>";

  const jobs = document.getElementById("tab-jobs");
  jobs.innerHTML = "<h2>ComfyUI</h2><div class='card'><pre>"+esc(JSON.stringify(STATE.comfyui,null,2))+"</pre></div>"
    + "<h2>Recent review events</h2><div class='card'><table><tr><th>Time</th><th>Action</th><th>Target</th><th>Note</th></tr>"
    + STATE.events.slice().reverse().slice(0,60).map(e=>"<tr><td>"+esc(e.timestamp)+"</td><td>"+esc(e.action)+"</td><td>"+esc(e.target_type)+" "+esc(e.target_id)+"</td><td>"+esc(e.note)+"</td></tr>").join("")
    + "</table></div>";
}
render();
</script>
</body>
</html>
"""


def _collect_state(store: ProjectStore) -> dict[str, Any]:
    from .cli import _analysis, _candidate_set, _character_index, _collect_generations, _latest, _style_bible

    project = store.read("project.json")
    analysis = _analysis(store) if _latest(store, "analysis", "analysis") else {}
    candidates = _candidate_set(store) if _latest(store, "art_direction", "candidates") else {}
    style_bible = _style_bible(store) if _latest(store, "style_bibles", "style_bible") else {}
    generations = _collect_generations(store)

    by_shot: dict[tuple[str, str], dict[str, Any]] = {}
    for generation in generations:
        key = (generation.get("artifact_type", ""), generation.get("shot_id", ""))
        by_shot[key] = generation

    shots = []
    for sequence in analysis.get("sequences", []):
        for scene in sequence.get("scenes", []):
            for shot in scene.get("shots", []):
                storyboard = by_shot.get(("STORYBOARD", shot["shot_id"]))
                blocking = by_shot.get(("BLOCKING", shot["shot_id"]))
                shots.append(
                    {
                        "shot_id": shot["shot_id"],
                        "sequence_id": sequence["sequence_id"],
                        "scene_id": scene["scene_id"],
                        "scene_heading": scene.get("heading", ""),
                        "shot_size": shot.get("camera_shot_type", ""),
                        "description": shot.get("visual_description", ""),
                        "purpose": shot.get("purpose", ""),
                        "duration_sec": shot.get("estimated_duration_sec", 0.0),
                        "image_path": (storyboard or {}).get("image_path", ""),
                        "review_status": (storyboard or {}).get("review_status", "NOT_GENERATED"),
                        "blocking_image_path": (blocking or {}).get("image_path", ""),
                        "blocking_review_status": (blocking or {}).get("review_status", "NOT_GENERATED"),
                    }
                )

    candidate_list = []
    for candidate in candidates.get("candidates", []):
        manifest = candidate.get("generation_manifest", {})
        candidate_list.append(
            {
                "candidate_id": candidate["candidate_id"],
                "style_name": candidate["style_name"],
                "description": candidate["description"],
                "selected": candidate.get("selected", False),
                "image_path": manifest.get("image_path", ""),
            }
        )

    comfyui: dict[str, Any] = {"status": "NOT_CHECKED"}
    try:
        from .comfyui_client import ComfyUIClient

        client = ComfyUIClient()
        stats = client.system_stats()
        comfyui = {
            "status": "CONNECTED",
            "comfyui_version": stats["system"]["comfyui_version"],
            "devices": [
                {"name": d["name"], "vram_free": d["vram_free"]} for d in stats.get("devices", [])
            ],
        }
    except Exception as exc:  # noqa: BLE001 - the UI must still load when ComfyUI is down
        comfyui = {"status": "UNAVAILABLE", "error": str(exc)}

    return {
        "project": project,
        "episode": analysis.get("episode", {}),
        "open_questions": analysis.get("open_questions", []),
        "candidates": {
            "comparison_scene_id": candidates.get("comparison_scene_id", ""),
            "candidates": candidate_list,
        },
        "style_bible": style_bible,
        "shots": shots,
        "events": store.events(),
        "comfyui": comfyui,
        "continuity": analysis.get("continuity", {}),
    }


def _handle_action(store: ProjectStore, body: dict[str, Any]) -> dict[str, Any]:
    from .cli import _analysis, _character_index, _latest, _style_bible
    from .generation import generate_image
    from .prompt_builder import build_shot_prompt

    action = body.get("action", "")
    target_type = body.get("target_type", "")
    target_id = body.get("target_id", "")
    actor = body.get("actor", "reviewer")
    note = body.get("note", "")

    if action == "SELECT":
        from .art_direction import select_candidate

        candidate_set = _candidate_set(store)
        select_candidate(candidate_set, target_id)
        path = _latest(store, "art_direction", "candidates")
        store.update_json(
            path.relative_to(store.root).as_posix(), candidate_set, "candidate.schema.json"
        )
        _append(store, "SELECT", "ART_DIRECTION_CANDIDATE", target_id, actor, note)
        return {"status": "PASS", "message": f"Selected {target_id}", "reload": True}

    if action in {"APPROVE", "REJECT"}:
        _append(store, action, target_type, target_id, actor, note)
        _set_review_status(store, target_type, target_id, action)
        return {"status": "PASS", "message": f"{action} recorded for {target_id}", "reload": True}
    if action == "REGENERATE":
        analysis = _analysis(store)
        style_bible = _style_bible(store)
        character_index = _character_index(analysis)
        target = None
        for sequence in analysis["sequences"]:
            for scene in sequence["scenes"]:
                for shot in scene["shots"]:
                    if shot["shot_id"] == target_id:
                        target = (sequence, scene, shot)
        if target is None:
            return {"status": "FAIL", "error": f"Unknown shot {target_id}"}
        sequence, scene, shot = target
        from .comfyui_client import ComfyUIClient

        built = build_shot_prompt(style_bible, shot, scene, character_index, mode="storyboard")
        settings = dict(style_bible["global_rules"]["generation_settings"])
        settings["seed"] = (int(settings.get("seed", 1)) + 1) % (2**53)
        result = generate_image(
            ComfyUIClient(),
            store,
            artifact_type="STORYBOARD",
            relative_dir=f"storyboard/{sequence['sequence_id']}/{scene['scene_id']}/{shot['shot_id']}",
            prompt=built["prompt"],
            negative_prompt=built["negative_prompt"],
            settings=settings,
            workflow_id="txt2img_v1",
            shot_id=shot["shot_id"],
            sequence_id=sequence["sequence_id"],
            scene_id=scene["scene_id"],
            source_script_sha256=analysis["source_script_sha256"],
            filename_prefix=f"SB_{shot['shot_id']}",
            actor=actor,
        )
        _append(store, "REGENERATE", target_type, target_id, actor, note or "Regenerated")
        return {
            "status": "PASS",
            "message": f"Regenerated {target_id} in {result['elapsed_sec']}s",
            "reload": True,
        }

    return {"status": "FAIL", "error": f"Unknown action {action!r}"}


def _append(
    store: ProjectStore, action: str, target_type: str, target_id: str, actor: str, note: str
) -> None:
    store.append_event(
        {
            "event_id": new_id("EVT"),
            "timestamp": utc_now(),
            "actor": actor,
            "action": action,
            "target_type": target_type,
            "target_id": target_id,
            "note": note,
            "metadata": {},
        }
    )


def _set_review_status(store: ProjectStore, target_type: str, target_id: str, action: str) -> None:
    status = {"APPROVE": "APPROVED", "REJECT": "REJECTED"}.get(action, action)
    for path in sorted(store.root.rglob("*.json")):
        relative = path.relative_to(store.root).as_posix()
        if not relative.endswith(".json") or relative.startswith(("source/", "analysis/", "style_bibles/")):
            continue
        try:
            value = store.read(relative)
        except (ValueError, json.JSONDecodeError):
            continue
        if not isinstance(value, dict) or not value.get("generation_id"):
            continue
        if value.get("artifact_type") != target_type:
            continue
        if value.get("shot_id") != target_id and value.get("generation_id") != target_id:
            continue
        value["review_status"] = status
        store.update_json(relative, value)


def make_handler(store: ProjectStore):
    class Handler(BaseHTTPRequestHandler):
        server_version = "VisualDevelopmentReview/1.0"

        def log_message(self, format: str, *args: Any) -> None:  # noqa: A002
            return

        def _send(self, status: int, body: bytes, content_type: str) -> None:
            self.send_response(status)
            self.send_header("Content-Type", content_type)
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)

        def do_GET(self) -> None:  # noqa: N802
            path = urlparse(self.path).path
            if path in {"/", "/index.html"}:
                state = _collect_state(store)
                html = PAGE_TEMPLATE.replace("__STATE__", json.dumps(state, default=str)).replace(
                    "__PROJECT__", state["project"]["project_id"]
                )
                self._send(200, html.encode("utf-8"), "text/html; charset=utf-8")
                return
            if path == "/api/state":
                body = json.dumps(_collect_state(store), default=str).encode("utf-8")
                self._send(200, body, "application/json")
                return
            if path.startswith("/media/"):
                relative = unquote(path[len("/media/") :])
                try:
                    target = contained_path(store.root, relative)
                except ValueError:
                    self._send(403, b"Forbidden", "text/plain")
                    return
                if not target.is_file():
                    self._send(404, b"Not found", "text/plain")
                    return
                content_type = mimetypes.guess_type(target.name)[0] or "application/octet-stream"
                self._send(200, target.read_bytes(), content_type)
                return
            self._send(404, b"Not found", "text/plain")

        def do_POST(self) -> None:  # noqa: N802
            if urlparse(self.path).path != "/api/action":
                self._send(404, b"Not found", "text/plain")
                return
            length = int(self.headers.get("Content-Length", "0"))
            try:
                body = json.loads(self.rfile.read(length).decode("utf-8") or "{}")
            except json.JSONDecodeError:
                self._send(400, b"Bad request", "text/plain")
                return
            try:
                result = _handle_action(store, body)
            except Exception as exc:  # noqa: BLE001 - surface errors in the UI
                result = {"status": "FAIL", "error": str(exc)}
            self._send(
                200,
                json.dumps(result, default=str).encode("utf-8"),
                "application/json",
            )

    return Handler


def serve(project_dir: Path, host: str = "127.0.0.1", port: int = 8765) -> None:
    store = ProjectStore(project_dir)
    server = ThreadingHTTPServer((host, port), make_handler(store))
    print(f"Visual Development review UI on http://{host}:{port}")
    print("This is a local creative review tool, not a GovernanceEngine approval.")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()
