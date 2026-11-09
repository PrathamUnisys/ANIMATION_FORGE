import React, { useCallback, useEffect, useMemo, useState } from 'react';
import { invoke, isTauri } from '@tauri-apps/api/core';
import { useForgeStore } from './store/useForgeStore';

/* CR_004: Workflow Stepper, Output Viewer & Debug Explorer.
   Formatted views by default; raw source only inside the Debug toggle.
   Missing values are shown as not recorded / unavailable, never invented. */

type Step = {
  stage_number: number; stage: string; progress: string;
  capability_status: string; capability_note?: string | null;
  evidence_status: string; input_count: number; output_count: number;
  approval_state?: string | null; is_current_stage: boolean;
  blockers: string[]; warnings: string[];
};
type Project = Record<string, any>;
type Dashboard = {
  projects: any[]; pending_approvals: any[]; recent_approvals: any[];
  recent_assets: any[]; toolchains: any[]; integrations: any[];
  creative_decisions: any[]; qc_reports: any[];
};

const STAGE_ENDPOINTS: Record<string, string[]> = {
  USER_STORY_IDEA: ['project'],
  STORY_ANALYSIS: ['files', 'executions'],
  SCRIPT_DEVELOPMENT: ['scripts'],
  SCREENPLAY_APPROVAL: ['scripts', 'dashboard'],
  PRODUCTION_REQUIREMENT_ANALYSIS: ['scenes'],
  ONLINE_TOOL_RESEARCH_AND_RND: ['research'],
  TOOL_COMPARISON: ['research'],
  PROOF_OF_CONCEPT: ['tasks', 'research'],
  HUMAN_TOOLCHAIN_APPROVAL: ['research', 'dashboard'],
  PRODUCTION_PLANNING: ['tasks'],
  AUDIO_AND_VISUAL_PRODUCTION: ['audio', 'assets'],
  STORYBOARD_AND_ANIMATIC: ['shots', 'scenes', 'files'],
  ANIMATION: ['tasks', 'files'],
  POST_PRODUCTION: ['files'],
  QUALITY_CONTROL: ['qc'],
  HUMAN_FINAL_APPROVAL: ['qc', 'dashboard'],
  COMPLETED_PRODUCTION_PACKAGE: ['files', 'steps'],
};

async function apiFetch(path: string, init?: RequestInit): Promise<Response> {
  if (!isTauri()) return fetch(path, init);
  const [baseUrl, token] = await invoke<[string, string]>('get_sidecar_connection');
  const headers = { ...(init?.headers as Record<string, string> || {}), 'x-forge-token': token };
  return fetch(`${baseUrl}${path}`, { ...init, headers });
}
async function apiJson(path: string): Promise<any> {
  const r = await apiFetch(path);
  if (!r.ok) throw new Error(`${path} -> ${r.status}`);
  return r.json();
}
/** Fetch a project file as a blob URL (token header cannot be sent by <img>/<audio> tags). */
async function apiBlobUrl(projectId: string, filePath: string): Promise<string> {
  const rel = filePath.startsWith(`PROJECTS/${projectId}/`)
    ? filePath.slice(`PROJECTS/${projectId}/`.length) : filePath;
  const r = await apiFetch(`/api/projects/${projectId}/file?path=${encodeURIComponent(rel)}`);
  if (!r.ok) throw new Error(`file ${rel} -> ${r.status}`);
  const blob = await r.blob();
  return URL.createObjectURL(blob);
}
async function apiText(projectId: string, filePath: string): Promise<string> {
  const rel = filePath.startsWith(`PROJECTS/${projectId}/`)
    ? filePath.slice(`PROJECTS/${projectId}/`.length) : filePath;
  const r = await apiFetch(`/api/projects/${projectId}/file?path=${encodeURIComponent(rel)}`);
  if (!r.ok) throw new Error(`file ${rel} -> ${r.status}`);
  return r.text();
}

function Chip({ label, tone }: { label: string; tone?: string }) {
  const colors: Record<string, string> = {
    DONE: 'bg-green-900/50 text-green-200 border-green-700',
    CURRENT: 'bg-amber-900/50 text-amber-200 border-amber-700',
    BLOCKED: 'bg-red-900/50 text-red-200 border-red-700',
    NOT_STARTED: 'bg-slate-800 text-slate-300 border-slate-600',
    PLANNED_UNAVAILABLE: 'bg-purple-900/50 text-purple-200 border-purple-700',
    NOT_TRACKED: 'bg-slate-800 text-slate-400 border-slate-600',
    IMPLEMENTED: 'bg-green-900/40 text-green-200 border-green-700',
    PARTIAL: 'bg-amber-900/40 text-amber-200 border-amber-700',
    SIMULATED: 'bg-orange-900/50 text-orange-200 border-orange-600',
    UNAVAILABLE: 'bg-purple-900/50 text-purple-200 border-purple-700',
    NOT_VERIFIED: 'bg-slate-800 text-slate-300 border-slate-600',
    AVAILABLE: 'bg-green-900/40 text-green-200 border-green-700',
    MISSING: 'bg-slate-800 text-slate-400 border-slate-600',
    INCONSISTENT: 'bg-red-900/50 text-red-200 border-red-600',
    NOT_APPLICABLE: 'bg-slate-800 text-slate-400 border-slate-600',
    APPROVED: 'bg-green-900/50 text-green-200 border-green-700',
    AWAITING_HUMAN_REVIEW: 'bg-amber-900/50 text-amber-200 border-amber-700',
  };
  return <span className={`inline-block px-2 py-0.5 rounded border text-[11px] ${colors[tone || label] || 'bg-slate-800 text-slate-300 border-slate-600'}`}>{label}</span>;
}

function DebugToggle({ title, children, debug }: { title: string; children: React.ReactNode; debug: any }) {
  const [open, setOpen] = useState(false);
  return (
    <div className="border border-slate-700 rounded mb-3">
      <div className="flex items-center justify-between px-3 py-2 bg-slate-800/60">
        <span className="text-sm font-semibold">{title}</span>
        <button onClick={() => setOpen(!open)} className="text-xs px-2 py-1 rounded bg-slate-700 hover:bg-slate-600">
          {open ? 'Formatted view' : 'Source / Debug'}
        </button>
      </div>
      <div className="p-3">
        {open ? (
          <pre className="text-xs overflow-auto max-h-[60vh] text-slate-300 whitespace-pre-wrap">{typeof debug === 'string' ? debug : JSON.stringify(debug, null, 2)}</pre>
        ) : children}
      </div>
    </div>
  );
}

function KV({ k, v }: { k: string; v: any }) {
  return (
    <div className="flex gap-2 text-sm py-0.5">
      <span className="text-slate-400 w-44 shrink-0">{k}</span>
      <span className="text-slate-100">{v === null || v === undefined || v === '' ? <em className="text-slate-500">not recorded</em> : String(v)}</span>
    </div>
  );
}

/** Minimal safe Markdown-ish renderer (headings, bold, lists, paragraphs). No HTML injection. */
function renderMarkdown(md: string) {
  const lines = md.split('\n');
  const out: React.ReactNode[] = [];
  lines.forEach((line, i) => {
    const text = line.replace(/\*\*(.+?)\*\*/g, '$1').replace(/`([^`]+)`/g, '$1');
    if (line.startsWith('# ')) out.push(<h1 key={i} className="text-xl font-bold mt-4 mb-2">{text.slice(2)}</h1>);
    else if (line.startsWith('## ')) out.push(<h2 key={i} className="text-lg font-semibold mt-4 mb-2 text-amber-300">{text.slice(3)}</h2>);
    else if (line.startsWith('### ')) out.push(<h3 key={i} className="text-base font-semibold mt-3 mb-1">{text.slice(4)}</h3>);
    else if (line.trim().startsWith('- ')) out.push(<div key={i} className="ml-4 text-sm">• {text.trim().slice(2)}</div>);
    else if (line.trim() === '') out.push(<div key={i} className="h-2" />);
    else out.push(<p key={i} className="text-sm text-slate-200 my-1">{text}</p>);
  });
  return <div>{out}</div>;
}

function MediaImage({ projectId, filePath, caption }: { projectId: string; filePath: string; caption?: string }) {
  const [url, setUrl] = useState<string | null>(null);
  const [err, setErr] = useState<string | null>(null);
  const [big, setBig] = useState(false);
  useEffect(() => {
    let alive = true; let obj = '';
    apiBlobUrl(projectId, filePath).then(u => { if (alive) { obj = u; setUrl(u); } }).catch(e => alive && setErr(String(e.message || e)));
    return () => { alive = false; if (obj) URL.revokeObjectURL(obj); };
  }, [projectId, filePath]);
  if (err) return <div className="text-xs text-red-300">Image unavailable: {err} ({filePath})</div>;
  if (!url) return <div className="text-xs text-slate-400">Loading image…</div>;
  return (
    <figure>
      <img src={url} alt={caption || filePath} onClick={() => setBig(!big)} className={`rounded border border-slate-700 cursor-pointer ${big ? 'max-w-full' : 'max-w-[220px]'}`} />
      <figcaption className="text-xs text-slate-400 mt-1">{caption || filePath}</figcaption>
    </figure>
  );
}

function AudioLine({ projectId, line }: { projectId: string; line: any }) {
  const [url, setUrl] = useState<string | null>(null);
  const [err, setErr] = useState<string | null>(null);
  useEffect(() => {
    let alive = true; let obj = '';
    if (line.file_path) apiBlobUrl(projectId, line.file_path).then(u => { if (alive) { obj = u; setUrl(u); } }).catch(e => alive && setErr(String(e.message || e)));
    return () => { alive = false; if (obj) URL.revokeObjectURL(obj); };
  }, [projectId, line.file_path]);
  return (
    <DebugToggle title={`${line.line_id} — ${line.character_id}`} debug={line}>
      <div className="text-sm space-y-1">
        <div className="text-base text-slate-50">“{line.spoken_text}”</div>
        <KV k="Scene" v={line.scene_id} />
        <KV k="Emotion direction" v={line.emotion_direction} />
        <KV k="Pronunciation" v={line.pronunciation_notes && Object.keys(line.pronunciation_notes).length ? JSON.stringify(line.pronunciation_notes) : null} />
        <KV k="TTS provider" v={line.provider_id} />
        <KV k="Model (from TTS payload)" v={line.model || 'not recorded'} />
        <KV k="Duration (recorded)" v={line.duration_sec ? `${line.duration_sec}s` : null} />
        <KV k="Approval" v={line.approval_status} />
        <KV k="Audio file" v={line.file_path} />
        <div className="mt-2">
          <span className="text-xs text-orange-300 border border-orange-600 rounded px-2 py-0.5">SIMULATED / TONE DEMO — playback is a sine tone, not spoken dialogue</span>
          {url ? <audio controls src={url} className="w-full mt-2" /> : <span className="text-xs text-slate-400 ml-2">{err || 'Loading audio…'}</span>}
        </div>
        {line.synthesis_note && <div className="text-xs text-slate-400">{line.synthesis_note}</div>}
      </div>
    </DebugToggle>
  );
}

function ScreenplayViewer({ projectId, scriptsData }: { projectId: string; scriptsData: any }) {
  const scripts = scriptsData?.scripts || [];
  const [selected, setSelected] = useState<string>('');
  const [detail, setDetail] = useState<any>(null);
  const [err, setErr] = useState<string | null>(null);
  useEffect(() => { if (scripts.length && !selected) setSelected(scripts[0].script_id); }, [scripts, selected]);
  useEffect(() => {
    if (!selected) return;
    apiJson(`/api/projects/${projectId}/scripts/${selected}`).then(setDetail).catch(e => setErr(String(e.message || e)));
  }, [projectId, selected]);
  if (!scripts.length) return <div className="text-sm text-slate-400">No screenplay revisions recorded for this project. (Stage capability: PARTIAL — demo pipeline only.)</div>;
  const s = detail?.script;
  return (
    <div>
      <div className="flex gap-2 mb-3 flex-wrap">
        {scripts.map((x: any) => (
          <button key={x.script_id} onClick={() => setSelected(x.script_id)} className={`text-xs px-2 py-1 rounded ${selected === x.script_id ? 'bg-amber-600 text-black' : 'bg-slate-700'}`}>
            v{x.version} · {x.script_id} · {x.approval_status}
          </button>
        ))}
      </div>
      {err && <div className="text-red-300 text-sm">{err}</div>}
      {s && (
        <DebugToggle title={`Screenplay ${s.script_id} (v${s.version})`} debug={{ ...s, file_content_markdown: s.file_content_markdown ? '[shown in debug below]' : null, raw_markdown: s.content_markdown }}>
          <div className="space-y-2">
            {s.db_file_consistent === false && <div className="text-sm text-red-200 border border-red-600 rounded p-2">INCONSISTENT: database screenplay differs from the SCRIPTS file. Both are preserved below; neither was silently preferred.</div>}
            <div className="flex gap-2 flex-wrap">
              <Chip label={s.approval_status} />
              <span className="text-xs text-slate-400">Agent: {s.agent_responsible} · Created: {s.created_at} · Immutable: {s.is_immutable ? 'yes' : 'no'}</span>
            </div>
            <KV k="Change summary" v={s.change_summary} />
            <KV k="Reason for changes" v={s.reason_for_changes} />
            <KV k="Reviewer comments" v={s.reviewer_comments} />
            {s.scores && Object.keys(s.scores).length > 0 && (
              <div className="text-sm"><span className="text-slate-400">Scores: </span>{Object.entries(s.scores).map(([k, v]: any) => <span key={k} className="mr-2">{k}: <b>{String(v)}</b></span>)}</div>
            )}
            {s.passes_completed && s.passes_completed.length > 0 && (
              <div className="text-sm"><span className="text-slate-400">Passes: </span>{s.passes_completed.join(', ')}</div>
            )}
            <div className="border-t border-slate-700 pt-2">{renderMarkdown(s.content_markdown || '')}</div>
            {s.file_content_markdown && s.db_file_consistent === false && (
              <div className="border-t border-slate-700 pt-2"><div className="text-xs text-slate-400 mb-1">On-disk file version ({s.file_path}):</div>{renderMarkdown(s.file_content_markdown)}</div>
            )}
          </div>
        </DebugToggle>
      )}
    </div>
  );
}

function FilesExplorer({ projectId, filesData, filterPrefix }: { projectId: string; filesData: any; filterPrefix?: string }) {
  const files: string[] = (filesData?.files || []).filter((f: string) => !filterPrefix || f.startsWith(filterPrefix));
  const [selected, setSelected] = useState<string>('');
  const [content, setContent] = useState<string | null>(null);
  const [blobUrl, setBlobUrl] = useState<string | null>(null);
  const [err, setErr] = useState<string | null>(null);
  const isImage = selected.endsWith('.png') || selected.endsWith('.jpg') || selected.endsWith('.jpeg');
  const isAudio = selected.endsWith('.wav');
  const isVideo = selected.endsWith('.mp4');
  useEffect(() => {
    setContent(null); setBlobUrl(null); setErr(null);
    if (!selected) return;
    if (isImage || isAudio || isVideo) {
      apiBlobUrl(projectId, selected).then(setBlobUrl).catch(e => setErr(String(e.message || e)));
    } else {
      apiText(projectId, selected).then(setContent).catch(e => setErr(String(e.message || e)));
    }
  }, [projectId, selected, isImage, isAudio, isVideo]);
  if (!files.length) return <div className="text-sm text-slate-400">No files under {filterPrefix || 'project folder'}.</div>;
  return (
    <div>
      <div className="flex flex-wrap gap-1 mb-3">
        {files.map((f: string) => (
          <button key={f} onClick={() => setSelected(f)} className={`text-xs px-2 py-1 rounded ${selected === f ? 'bg-amber-600 text-black' : 'bg-slate-700'}`}>{f}</button>
        ))}
      </div>
      {err && <div className="text-red-300 text-sm">{err}</div>}
      {selected && (
        <DebugToggle title={selected} debug={content ?? { path: selected, type: isImage ? 'image' : isAudio ? 'audio' : isVideo ? 'video (listed-only)' : 'text' }}>
          {isImage && blobUrl && <MediaImage projectId={projectId} filePath={selected} />}
          {isAudio && blobUrl && <audio controls src={blobUrl} className="w-full" />}
          {isVideo && <div className="text-sm text-slate-400">Video files are listed-only in this milestone (no playback implied). Path: {selected}</div>}
          {!isImage && !isAudio && !isVideo && (content !== null ? <div className="text-sm">{renderMarkdown(content)}</div> : <div className="text-xs text-slate-400">Loading…</div>)}
        </DebugToggle>
      )}
    </div>
  );
}

function StoryboardAndAnimaticStage({ projectId, data }: { projectId: string; data: Record<string, any> }) {
  const shots = data.shots?.shots || [];
  const scenes = data.scenes?.scenes || [];
  const [selectedShotId, setSelectedShotId] = useState('');
  const shot = shots.find((item: any) => item.shot_id === selectedShotId) || shots[0];

  return (
    <div>
      <div className="text-sm mb-2">Scenes: {scenes.map((s: any) => s.scene_id).join(', ') || 'none recorded'} · Shots: {shots.length}</div>
      <div className="flex gap-1 flex-wrap mb-3">
        {shots.map((s: any) => (
          <button key={s.shot_id} onClick={() => setSelectedShotId(s.shot_id)} className={`text-xs px-2 py-1 rounded ${(shot && shot.shot_id === s.shot_id) ? 'bg-amber-600 text-black' : 'bg-slate-700'}`}>{s.shot_id}</button>
        ))}
      </div>
      {shot && (
        <DebugToggle title={`${shot.shot_id} — ${shot.shot_size} · ${shot.duration_sec}s`} debug={shot}>
          <KV k="Scene" v={shot.scene_id} /><KV k="Camera angle/position" v={`${shot.camera_angle} / ${shot.camera_position}`} />
          <KV k="Movement" v={shot.camera_movement} /><KV k="Focal length" v={shot.focal_length_mm ? `${shot.focal_length_mm}mm` : null} />
          <KV k="Character placement" v={shot.character_placement} /><KV k="Character movement" v={shot.character_movement} />
          <KV k="Expression" v={shot.facial_expression} /><KV k="Lighting" v={shot.lighting} />
          <KV k="Audio cues" v={JSON.stringify(shot.audio_cues || [])} />
          <KV k="Approval" v={shot.approval_status} />
          {shot.storyboard_panel_path && <div className="mt-2"><MediaImage projectId={projectId} filePath={shot.storyboard_panel_path} caption={shot.storyboard_panel_path} /></div>}
        </DebugToggle>
      )}
      <div className="mt-4"><div className="text-sm font-semibold mb-2">Animatic manifests & panels (files)</div>
        <FilesExplorer projectId={projectId} filesData={data.files} filterPrefix="ANIMATICS/" /></div>
    </div>
  );
}

function stageViewer(projectId: string, stage: string, data: Record<string, any>, stepsData: any) {
  const d = data;
  switch (stage) {
    case 'USER_STORY_IDEA': {
      const p = d.project?.project || {};
      return (
        <DebugToggle title="Project brief" debug={p}>
          <KV k="Title" v={p.title} /><KV k="Project ID" v={p.project_id} />
          <KV k="Synopsis" v={p.synopsis} /><KV k="Genre (display)" v={p.genre} />
          <KV k="Target audience" v={p.target_audience} /><KV k="Runtime" v={p.intended_runtime_sec ? `${p.intended_runtime_sec}s` : null} />
          <KV k="Language" v={p.language} /><KV k="Creative brief" v={p.creative_brief} />
          <KV k="Visual direction" v={p.visual_direction} /><KV k="Technique" v={p.animation_technique} />
          <KV k="Status" v={p.status} /><KV k="Current stage" v={p.current_stage} />
          <KV k="Updated" v={p.updated_at} />
          <div className="text-xs text-slate-400 mt-2">Genre/style IDs live in the project schema; DB migration + UI selectors are separate work — shown here only if recorded.</div>
        </DebugToggle>
      );
    }
    case 'SCRIPT_DEVELOPMENT':
    case 'SCREENPLAY_APPROVAL':
      return <ScreenplayViewer projectId={projectId} scriptsData={d.scripts} />;
    case 'PRODUCTION_REQUIREMENT_ANALYSIS': {
      const scenes = d.scenes?.scenes || [];
      if (!scenes.length) return <div className="text-sm text-slate-400">No scenes recorded. Breakdown requires an approved script (NOT_TRACKED — no requirement-analysis record exists).</div>;
      return scenes.map((s: any) => (
        <DebugToggle key={s.scene_id} title={`${s.scene_id} — ${s.title}`} debug={s}>
          <KV k="Location" v={s.location_id} /><KV k="Duration" v={`${s.duration_sec}s`} />
          <KV k="Characters" v={(s.characters || []).join(', ')} /><KV k="Required assets" v={(s.required_assets || []).join(', ')} />
          <KV k="Animation method" v={s.animation_method} /><KV k="Shots" v={(s.required_shots || []).join(', ')} />
          <KV k="Camera" v={s.camera_requirements} /><KV k="Lighting" v={s.lighting} />
          <KV k="Audio dependencies" v={(s.audio_dependencies || []).join(', ')} />
        </DebugToggle>
      ));
    }
    case 'ONLINE_TOOL_RESEARCH_AND_RND':
    case 'TOOL_COMPARISON':
    case 'HUMAN_TOOLCHAIN_APPROVAL': {
      const reports = d.research?.research_reports || [];
      const cands = d.research?.tool_candidates || [];
      const evals = d.research?.tool_evaluations || [];
      const chains = d.research?.toolchain_profiles || [];
      return (
        <div>
          {reports.map((r: any) => (
            <DebugToggle key={r.report_id} title={`Research ${r.report_id} (${r.decision_status})`} debug={r}>
              <KV k="Date" v={r.research_date} /><KV k="Methodology" v={r.search_methodology} />
              <KV k="Markdown file" v={r.markdown_path} /><KV k="Decision" v={r.decision_status} />
              <div className="text-xs text-slate-400 mt-1">{r.research_note}</div>
              {r.sources && r.sources.length > 0 && <div className="text-sm mt-1">Sources: {r.sources.map((s: any, i: number) => <span key={i} className="mr-2">{typeof s === 'string' ? s : JSON.stringify(s)}</span>)}</div>}
            </DebugToggle>
          ))}
          {cands.length > 0 && (
            <div className="overflow-auto border border-slate-700 rounded mb-3">
              <table className="w-full text-xs">
                <thead><tr className="bg-slate-800">{['Tool', 'Category', 'Version', 'State', 'Licence', 'Commercial', 'Est. cost', 'HW compat', 'Source'].map(h => <th key={h} className="p-2 text-left">{h}</th>)}</tr></thead>
                <tbody>{cands.map((c: any) => (
                  <tr key={c.tool_id} className="border-t border-slate-800">
                    <td className="p-2">{c.name}<div className="text-slate-500">{c.tool_id}</div></td>
                    <td className="p-2">{c.category}</td><td className="p-2">{c.version}</td><td className="p-2">{c.state}</td>
                    <td className="p-2">{c.license}</td><td className="p-2">{c.commercial_use_allowed ? 'yes' : 'no'}</td>
                    <td className="p-2">{c.estimated_cost_usd}</td><td className="p-2">{c.hardware_compatible ? 'yes' : 'no'}</td>
                    <td className="p-2">{c.source_url}</td>
                  </tr>))}</tbody>
              </table>
            </div>
          )}
          {evals.map((e: any) => (
            <DebugToggle key={e.eval_id} title={`Evaluation ${e.eval_id} — ${e.tool_id}`} debug={e}>
              <KV k="Weighted total" v={e.weighted_total} /><KV k="Evaluated" v={e.evaluated_at} />
              <KV k="Evidence" v={e.evidence_notes} />
              <div className="text-sm">{Object.entries(e.scores || {}).map(([k, v]: any) => <span key={k} className="mr-2">{k}: <b>{String(v)}</b></span>)}</div>
            </DebugToggle>
          ))}
          {chains.map((t: any) => (
            <DebugToggle key={t.toolchain_id} title={`Toolchain ${t.toolchain_id} v${t.version} ${t.locked ? '(locked)' : ''}`} debug={t}>
              <KV k="Approved by" v={t.approved_by} /><KV k="Approved at" v={t.approved_at} /><KV k="File" v={t.file_path} />
              <pre className="text-xs mt-2 whitespace-pre-wrap">{JSON.stringify(t.profile, null, 2)}</pre>
            </DebugToggle>
          ))}
          {!reports.length && !cands.length && !chains.length && <div className="text-sm text-slate-400">No research/tool records for this project.</div>}
        </div>
      );
    }
    case 'PROOF_OF_CONCEPT': {
      const jobs = d.tasks?.generation_jobs || [];
      const reports = d.research?.research_reports || [];
      return (
        <div>
          {jobs.map((j: any) => (
            <DebugToggle key={j.job_id} title={`Job ${j.job_id} — ${j.status}`} debug={j}>
              <KV k="Backend" v={j.backend_type} /><KV k="Workflow" v={j.workflow_id} />
              <KV k="Submitted" v={j.submitted_at} /><KV k="Completed" v={j.completed_at} />
              <KV k="Outputs" v={(j.output_paths || []).join(', ') || 'none recorded'} />
              <KV k="Error" v={j.error_message} />
            </DebugToggle>
          ))}
          {reports.map((r: any) => <div key={r.report_id} className="text-sm"><KV k={`PoC results (${r.report_id})`} v={JSON.stringify(r.poc_results || 'none recorded')} /></div>)}
          {!jobs.length && !reports.length && <div className="text-sm text-slate-400">No proof-of-concept records. This stage is NOT_VERIFIED — no authorised test is recorded.</div>}
        </div>
      );
    }
    case 'PRODUCTION_PLANNING': {
      const tasks = d.tasks?.tasks || [];
      return <TaskViewer tasks={tasks} jobs={d.tasks?.generation_jobs || []} />;
    }
    case 'AUDIO_AND_VISUAL_PRODUCTION': {
      const lines = d.audio?.audio_lines || [];
      const assets = d.assets?.assets || [];
      return (
        <div>
          {lines.map((l: any) => <AudioLine key={l.audio_id} projectId={projectId} line={l} />)}
          {!lines.length && <div className="text-sm text-slate-400 mb-3">No dialogue lines recorded.</div>}
          <ImageGallery projectId={projectId} assets={assets} />
        </div>
      );
    }
    case 'STORYBOARD_AND_ANIMATIC':
      return <StoryboardAndAnimaticStage projectId={projectId} data={d} />;
    case 'ANIMATION':
      return (
        <div>
          <div className="text-sm text-purple-200 border border-purple-700 rounded p-2 mb-3">PLANNED_UNAVAILABLE: no animation execution capability is implemented. Drafts below are files only.</div>
          <FilesExplorer projectId={projectId} filesData={d.files} filterPrefix="DRAFTS/" />
        </div>
      );
    case 'POST_PRODUCTION':
      return <FilesExplorer projectId={projectId} filesData={d.files} filterPrefix="EDITING/" />;
    case 'QUALITY_CONTROL':
    case 'HUMAN_FINAL_APPROVAL': {
      const reports = d.qc?.qc_reports || [];
      const approvals = [...(d.dashboard?.pending_approvals || []), ...(d.dashboard?.recent_approvals || [])]
        .filter((a: any) => a.project_id === projectId);
      return (
        <div>
          {stage === 'HUMAN_FINAL_APPROVAL' && (
            <div className="mb-3">
              <div className="text-sm font-semibold mb-1">Human approvals for this project</div>
              {approvals.length === 0 && <div className="text-sm text-slate-400">No approval records found in dashboard data.</div>}
              {approvals.map((a: any) => (
                <DebugToggle key={a.approval_id} title={`${a.approval_id} — ${a.state}`} debug={a}>
                  <KV k="Target" v={`${a.target_type} ${a.target_id} rev ${a.revision}`} />
                  <KV k="Reviewer" v={a.reviewer_id} /><KV k="Decided" v={a.decided_at} /><KV k="Comments" v={a.comments} />
                </DebugToggle>
              ))}
            </div>
          )}
          {reports.map((r: any) => {
            const checks = r.checks || {};
            const passed = Object.entries(checks).filter(([, v]: any) => v === true).map(([k]) => k);
            const failed = Object.entries(checks).filter(([, v]: any) => v !== true).map(([k]) => k);
            return (
              <DebugToggle key={r.qc_id} title={`${r.qc_category} — ${r.outcome}`} debug={r}>
                <KV k="Target" v={`${r.target_type} ${r.target_id}`} /><KV k="Created" v={r.created_at} />
                <div className="text-sm mt-1"><span className="text-green-300">Passed ({passed.length}): </span>{passed.join(', ') || 'none'}</div>
                <div className="text-sm"><span className="text-red-300">Failed ({failed.length}): </span>{failed.join(', ') || 'none'}</div>
                <div className="text-sm"><span className="text-slate-400">Untested: </span>none recorded separately — checks not in the report were not run</div>
                <div className="text-sm mt-1">Recommendations: {(r.recommendations || []).join(' ') || 'none'}</div>
                <div className="text-xs text-orange-300 mt-2">SIMULATED: predetermined checks, no media inspection. Technical QC is not creative approval (grants_creative_approval: false).</div>
              </DebugToggle>
            );
          })}
          {!reports.length && <div className="text-sm text-slate-400">No QC reports recorded.</div>}
        </div>
      );
    }
    case 'COMPLETED_PRODUCTION_PACKAGE': {
      const step17 = stepsData?.steps?.find((s: any) => s.stage === 'COMPLETED_PRODUCTION_PACKAGE');
      return (
        <div>
          <div className="text-sm mb-2">Package stage progress: <Chip label={step17?.progress || 'NOT_TRACKED'} /> <span className="text-slate-400">COMPLETED is shown only when required deliverables and approvals are verifiable — currently not established.</span></div>
          <FilesExplorer projectId={projectId} filesData={d.files} />
        </div>
      );
    }
    default:
      return <div className="text-sm text-slate-400">No viewer for this stage yet. Files and provenance below remain available.</div>;
  }
}

function ImageGallery({ projectId, assets }: { projectId: string; assets: any[] }) {
  const [sel, setSel] = useState('');
  const asset = assets.find((a: any) => a.asset_id === sel) || assets[0];
  const revs = asset?.revisions || [];
  if (!assets.length) return <div className="text-sm text-slate-400">No image assets recorded. (Character/environment files, when present, are listed under Files.)</div>;
  return (
    <div>
      <div className="flex gap-1 flex-wrap mb-3">
        {assets.map((a: any) => (
          <button key={a.asset_id} onClick={() => setSel(a.asset_id)} className={`text-xs px-2 py-1 rounded ${(asset && asset.asset_id === a.asset_id) ? 'bg-amber-600 text-black' : 'bg-slate-700'}`}>{a.asset_id}</button>
        ))}
      </div>
      {asset && (
        <DebugToggle title={`${asset.asset_id} — ${asset.name} (${asset.approval_status})`} debug={asset}>
          <KV k="Type" v={asset.type} /><KV k="Description" v={asset.description} />
          <KV k="Current revision" v={asset.current_revision} /><KV k="Licence" v={asset.license_info} />
          <KV k="Created" v={asset.created_at} />
          {revs.map((r: any) => (
            <div key={r.revision_id} className="border-t border-slate-700 mt-2 pt-2">
              <div className="text-sm font-semibold">Revision {r.revision} · {r.tool_used} / {r.provider} / {r.model}</div>
              <KV k="File" v={r.file_location} /><KV k="SHA-256" v={r.file_sha256} />
              <KV k="Seed" v={r.seed} /><KV k="Prompt (recorded)" v={r.prompt} /><KV k="Negative prompt" v={r.negative_prompt} />
              <KV k="Approval" v={r.approval_status} />
              {r.file_location && <div className="mt-2"><MediaImage projectId={projectId} filePath={r.file_location} caption={r.file_location} /></div>}
            </div>
          ))}
          {!revs.length && <div className="text-xs text-slate-400 mt-1">No revisions recorded for this asset.</div>}
        </DebugToggle>
      )}
    </div>
  );
}

function TaskViewer({ tasks, jobs }: { tasks: any[]; jobs: any[] }) {
  const [dept, setDept] = useState('');
  const [status, setStatus] = useState('');
  const filtered = tasks.filter((t: any) => (!dept || t.department === dept) && (!status || t.status === status));
  const depts = [...new Set(tasks.map((t: any) => t.department))];
  const statuses = [...new Set(tasks.map((t: any) => t.status))];
  return (
    <div>
      <div className="flex gap-2 mb-3">
        <select value={dept} onChange={e => setDept(e.target.value)} className="bg-slate-800 text-sm rounded px-2 py-1">
          <option value="">All departments</option>{depts.map(d => <option key={d} value={d}>{d}</option>)}
        </select>
        <select value={status} onChange={e => setStatus(e.target.value)} className="bg-slate-800 text-sm rounded px-2 py-1">
          <option value="">All statuses</option>{statuses.map(s => <option key={s} value={s}>{s}</option>)}
        </select>
        <span className="text-xs text-slate-400">{filtered.length} / {tasks.length} tasks</span>
      </div>
      {filtered.map((t: any) => (
        <DebugToggle key={t.task_id} title={`${t.task_id} — ${t.title} (${t.status})`} debug={t}>
          <KV k="Department" v={t.department} /><KV k="Assigned agent" v={t.assigned_agent} />
          <KV k="Retries" v={`${t.retry_count} / ${t.max_retries}`} /><KV k="Error category" v={t.error_category} />
          <KV k="Dependencies" v={(t.dependencies || []).map((d: any) => `${d.depends_on_task_id} (${d.dependency_type})`).join(', ') || 'none recorded'} />
          <KV k="Selected tool" v={t.selected_tool} /><KV k="Expected outputs" v={t.expected_outputs} /><KV k="Actual outputs" v={t.actual_outputs} />
          <div className="text-xs text-slate-400">{t.tool_note}</div>
        </DebugToggle>
      ))}
      {!filtered.length && <div className="text-sm text-slate-400">No tasks match the filters / none recorded.</div>}
      {jobs.length > 0 && <div className="text-sm font-semibold mt-3 mb-1">Generation jobs</div>}
      {jobs.map((j: any) => (
        <DebugToggle key={j.job_id} title={`Job ${j.job_id} — ${j.status}`} debug={j}>
          <KV k="Backend" v={j.backend_type} /><KV k="Workflow" v={j.workflow_id} />
          <KV k="Submitted" v={j.submitted_at} /><KV k="Error" v={j.error_message} />
        </DebugToggle>
      ))}
    </div>
  );
}

function StoryContextPanel({ projectId }: { projectId: string }) {
  type Tab = 'bible' | 'brief' | 'development' | 'cards' | 'screenplay' | 'qc' | 'approval';
  const [tab, setTab] = useState<Tab>('bible');
  const [bible, setBible] = useState<any>(null);
  const [canon, setCanon] = useState<any>(null);
  const [brief, setBrief] = useState<any>(null);
  const [briefHistory, setBriefHistory] = useState<any[]>([]);
  const [revs, setRevs] = useState<any>(null);
  const [err, setErr] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);
  const [seriesId, setSeriesId] = useState('SER_BELL');
  const [episodeId, setEpisodeId] = useState('EP_BELL_01');
  const [premise, setPremise] = useState('');
  const [provider, setProvider] = useState('OLLAMA_OPENAI_COMPATIBLE');
  const [model, setModel] = useState('ornith:9b');
  const [title, setTitle] = useState('The Thirteenth Bell of St. Jude');
  // Brief form
  const [bTitle, setBTitle] = useState('');
  const [bPremise, setBPremise] = useState('');
  const [bSynopsis, setBSynopsis] = useState('');
  const [bGenre, setBGenre] = useState('GENRE_FANTASY');
  const [bSecondary, setBSecondary] = useState('GENRE_COMEDY');
  const [bChannel, setBChannel] = useState('');
  const [bProtagonist, setBProtagonist] = useState('');
  const [bObjective, setBObjective] = useState('');
  const [bOpposition, setBOpposition] = useState('');
  const [bConflict, setBConflict] = useState('');
  const [bStakes, setBStakes] = useState('');
  const [bEnding, setBEnding] = useState('');
  const [bRuntime, setBRuntime] = useState('300');
  // Development + cards + screenplay + qc
  const [analysis, setAnalysis] = useState<any>(null);
  const [hooks, setHooks] = useState<any>(null);
  const [outline, setOutline] = useState<any>(null);
  const [cards, setCards] = useState<any>(null);
  const [screenplay, setScreenplay] = useState<any>(null);
  const [qc, setQc] = useState<any>(null);
  const [critique, setCritique] = useState<any>(null);
  const [comments, setComments] = useState('');

  const load = useCallback(async () => {
    setErr(null);
    try {
      const b = await apiJson(`/api/story-bibles/${seriesId}`).catch(() => null);
      setBible(b);
      const c = await apiJson(`/api/story-bibles/${seriesId}/canon`).catch(() => null);
      setCanon(c?.canon || null);
      const r = await apiJson(`/api/story-bibles/${seriesId}/revisions`).catch(() => null);
      setRevs(r);
      try {
        const br = await apiJson(`/api/projects/${projectId}/episode-briefs/${episodeId}`);
        setBrief(br);
        const bc = br?.content || {};
        setBTitle(bc.title || ''); setBPremise(bc.premise || ''); setBSynopsis(bc.synopsis || '');
        setBGenre(bc.primary_genre_id || 'GENRE_FANTASY');
        setBSecondary((bc.secondary_genre_ids || []).join(','));
        setBChannel(bc.channel_style_id || '');
        setBProtagonist(bc.protagonist || ''); setBObjective(bc.objective || '');
        setBOpposition(bc.opposition || ''); setBConflict(bc.conflict || '');
        setBStakes(bc.stakes || ''); setBEnding(bc.ending_direction || '');
        if (bc.target_runtime_sec) setBRuntime(String(bc.target_runtime_sec));
      } catch { setBrief(null); }
      try {
        const a = await apiJson(`/api/projects/${projectId}/story/artifacts/STORY_ANALYSIS?episode_id=${encodeURIComponent(episodeId)}`).catch(() => null);
        setAnalysis(a);
        const h = await apiJson(`/api/projects/${projectId}/story/artifacts/HOOKS?episode_id=${encodeURIComponent(episodeId)}`).catch(() => null);
        setHooks(h);
        const o = await apiJson(`/api/projects/${projectId}/story/artifacts/OUTLINE?episode_id=${encodeURIComponent(episodeId)}`).catch(() => null);
        setOutline(o);
        const sc = await apiJson(`/api/projects/${projectId}/story/artifacts/SCENE_CARDS?episode_id=${encodeURIComponent(episodeId)}`).catch(() => null);
        setCards(sc);
        const sp = await apiJson(`/api/projects/${projectId}/story/artifacts/SCREENPLAY?episode_id=${encodeURIComponent(episodeId)}`).catch(() => null);
        setScreenplay(sp);
      } catch { /* artifacts may not exist yet */ }
    } catch (e: any) { setErr(String(e.message || e)); }
  }, [projectId, seriesId, episodeId]);

  useEffect(() => { load(); }, [load]);

  const postJson = async (path: string, body: any) => {
    const r = await apiFetch(path, { method: 'POST', headers: { 'content-type': 'application/json' }, body: JSON.stringify(body) });
    if (!r.ok) throw new Error(`${path} -> ${r.status}: ${await r.text().catch(() => '')}`);
    return r.json();
  };

  const createBible = async () => {
    if (!premise.trim()) { setErr('Premise is required.'); return; }
    try {
      setLoading(true);
      const payload = {
        series_id: seriesId, project_id: projectId, status: 'DRAFT',
        content: { series_id: seriesId, title: 'Series Bible', premise, genre: 'Fantasy', format: 'Short', world: { overview: '' }, characters: [] },
      };
      await postJson('/api/story-bibles', payload);
      setPremise(''); load();
    } catch (e: any) { setErr(String(e.message || e)); } finally { setLoading(false); }
  };

  const transitionBible = async (revId: string) => {
    const next = 'IN_REVIEW';
    if (bible?.status === 'IN_REVIEW') { setErr('Head is already IN_REVIEW. Use Approve (Windows dialog) for APPROVED.'); return; }
    try { await postJson(`/api/story-bibles/${revId}/transition`, { new_status: next, human_confirmed: false }); load(); }
    catch (e: any) { setErr(String(e.message || e)); }
  };
  const approveBible = async (revId: string) => {
    if (!window.confirm('Approve this Bible revision as canon? A Windows confirmation will appear.')) return;
    try { await postJson(`/api/story-bibles/${revId}/transition`, { new_status: 'APPROVED', human_confirmed: false }); load(); }
    catch (e: any) { setErr(String(e.message || e)); }
  };

  const saveBrief = async () => {
    if (!bTitle.trim() || !bPremise.trim() || !bProtagonist.trim() || !bObjective.trim() || !bConflict.trim() || !bStakes.trim() || !bEnding.trim()) {
      setErr('Required fields: title, premise, protagonist, objective, conflict, stakes, ending.'); return;
    }
    const runtime = parseInt(bRuntime, 10);
    if (!runtime || runtime < 5) { setErr('Target runtime must be at least 5 seconds.'); return; }
    try {
      setLoading(true);
      const content = {
        project_id: projectId, episode_id: episodeId, series_id: seriesId,
        title: bTitle, premise: bPremise, synopsis: bSynopsis,
        primary_genre_id: bGenre,
        secondary_genre_ids: bSecondary.split(',').map(s => s.trim()).filter(Boolean),
        channel_style_id: bChannel.trim() ? bChannel.trim() : null,
        audience: 'General', language: 'en-US', target_runtime_sec: runtime,
        protagonist: bProtagonist, objective: bObjective, opposition: bOpposition,
        conflict: bConflict, stakes: bStakes, ending_direction: bEnding,
        characters: bProtagonist ? [bProtagonist] : [], locations: [],
        clues_and_reveals: [], required_beats: [], constraints: [],
        relationship_to_canon: '',
      };
      await postJson(`/api/projects/${projectId}/episode-briefs/${episodeId}`, { content, status: 'DRAFT' });
      load();
    } catch (e: any) { setErr(String(e.message || e)); } finally { setLoading(false); }
  };

  const runStage = async (name: 'analysis' | 'hooks' | 'outline' | 'cards' | 'screenplay') => {
    const apiMap: Record<string, string> = {
      analysis: 'story/analysis', hooks: 'story/hooks', outline: 'story/outline', cards: 'story/scene-cards', screenplay: 'story/screenplay',
    };
    try {
      setLoading(true); setErr(null);
      const payload = { episode_id: episodeId, series_id: seriesId, provider_id: provider, model_id: model, title, target_audience: 'General', intended_duration_sec: parseInt(bRuntime, 10) || 300 };
      const data = await postJson(`/api/projects/${projectId}/${apiMap[name]}`, payload);
      if (name === 'analysis') setAnalysis(data);
      if (name === 'hooks') setHooks(data);
      if (name === 'outline') setOutline(data);
      if (name === 'cards') setCards(data);
      if (name === 'screenplay') setScreenplay(data);
      load();
    } catch (e: any) { setErr(String(e.message || e)); } finally { setLoading(false); }
  };

  const approveOutline = async () => {
    if (!window.confirm('Approve the latest outline? A Windows confirmation will appear.')) return;
    try { await postJson(`/api/projects/${projectId}/story/outline/approve`, { episode_id: episodeId }); load(); }
    catch (e: any) { setErr(String(e.message || e)); }
  };

  const runQc = async () => {
    const scriptId = screenplay?.content?.script_id || screenplay?.script_id;
    if (!scriptId) { setErr('No screenplay yet — generate one first.'); return; }
    try {
      const data = await postJson(`/api/projects/${projectId}/story/qc/validate`, { script_id: scriptId, episode_id: episodeId, series_id: seriesId });
      setQc(data);
    } catch (e: any) { setErr(String(e.message || e)); }
  };

  const runCritique = async () => {
    const scriptId = screenplay?.content?.script_id || screenplay?.script_id;
    if (!scriptId) { setErr('No screenplay yet — generate one first.'); return; }
    try {
      const data = await postJson(`/api/projects/${projectId}/story/qc/critique`, { script_id: scriptId, episode_id: episodeId, provider_id: provider, model_id: model });
      setCritique(data);
    } catch (e: any) { setErr(String(e.message || e)); }
  };

  const approveScreenplay = async () => {
    const approvalId = screenplay?.content?.script_id ? `APP_${screenplay.content.script_id}` : null;
    if (!approvalId) { setErr('No screenplay approval gate found.'); return; }
    if (!window.confirm(`Approve ${approvalId}? Requires exact-revision QC PASS with no BLOCKER and a creative critique. A Windows confirmation will appear.`)) return;
    try {
      const data = await postJson('/api/approvals/decide', { approval_id: approvalId, decision: 'APPROVED', comments: comments || 'Human screenplay approval (CR_006 hardening)' });
      setQc(data); load();
    } catch (e: any) { setErr(String(e.message || e)); }
  };

  const tabs: { id: Tab; label: string }[] = [
    { id: 'bible', label: 'A. Series Bible' }, { id: 'brief', label: 'B. Episode Brief' },
    { id: 'development', label: 'C. Story Development' }, { id: 'cards', label: 'D. Scene Cards' },
    { id: 'screenplay', label: 'E. Screenplay' }, { id: 'qc', label: 'F. Quality Control' }, { id: 'approval', label: 'G. Human Approval' },
  ];

  return (
    <div className="space-y-4">
      <p className="text-sm text-slate-400">Versioned Series Bible → Episode Brief → staged screenplay. AI proposals never become approved canon; approvals require the Windows reviewer.</p>
      <div className="grid grid-cols-2 gap-3">
        <label className="text-xs text-slate-400">Series ID
          <input value={seriesId} onChange={e => setSeriesId(e.target.value)} className="w-full mt-1 bg-slate-800 rounded px-2 py-1 text-sm" />
        </label>
        <label className="text-xs text-slate-400">Episode ID
          <input value={episodeId} onChange={e => setEpisodeId(e.target.value)} className="w-full mt-1 bg-slate-800 rounded px-2 py-1 text-sm" />
        </label>
        <label className="text-xs text-slate-400">Provider
          <select value={provider} onChange={e => setProvider(e.target.value)} className="w-full mt-1 bg-slate-800 rounded px-2 py-1 text-sm">
            <option value="OLLAMA_OPENAI_COMPATIBLE">OLLAMA_OPENAI_COMPATIBLE (local opencode Ollama)</option>
            <option value="DETERMINISTIC_MOCK">DETERMINISTIC_MOCK (test)</option>
          </select>
        </label>
        <label className="text-xs text-slate-400">Model
          <select value={model} onChange={e => setModel(e.target.value)} className="w-full mt-1 bg-slate-800 rounded px-2 py-1 text-sm">
            <option value="ornith:9b">ornith:9b (primary)</option>
            <option value="qwen3.5:4b">qwen3.5:4b (fallback)</option>
            <option value="mock-42">mock-42</option>
          </select>
        </label>
      </div>
      <div className="flex gap-1 flex-wrap border-b border-slate-700 pb-2">
        {tabs.map(t => (
          <button key={t.id} onClick={() => setTab(t.id)} className={`text-xs px-2 py-1 rounded ${tab === t.id ? 'bg-amber-600 text-black' : 'bg-slate-800 text-slate-300'}`}>{t.label}</button>
        ))}
      </div>
      {err && <div className="text-red-300 text-sm">{err}</div>}
      {loading && <div className="text-xs text-slate-400">Working…</div>}

      {tab === 'bible' && (
        <div className="space-y-3">
          <DebugToggle title="Series Bible (head revision)" debug={bible}>
            {bible ? (<div className="space-y-1 text-sm"><div>Revision {bible.revision} · {bible.status} · hash {String(bible.content_hash_sha256 || '').slice(0,12)}</div><div className="text-slate-300">{bible.content?.premise || '(no premise)'}</div><div className="text-xs text-slate-400">Provenance: {JSON.stringify(bible.provenance || {})}</div></div>) : <div className="text-sm text-slate-400">No Bible for this series yet.</div>}
          </DebugToggle>
          <DebugToggle title="Approved canon" debug={canon}>
            {canon ? (<div className="text-sm">Rev {canon.revision} · {canon.bible_revision_id} · hash {String(canon.content_hash_sha256 || '').slice(0,12)}</div>) : <div className="text-sm text-slate-400">No approved canon yet. Drafts are never canon.</div>}
          </DebugToggle>
          <div className="border border-slate-700 rounded p-3 space-y-2">
            <div className="text-sm font-semibold">Create / edit Bible (new revision)</div>
            <textarea value={premise} onChange={e => setPremise(e.target.value)} placeholder="Series premise…" className="w-full bg-slate-800 rounded px-2 py-1 text-sm" rows={3} />
            <div className="flex gap-2">
              <button onClick={createBible} disabled={loading} className="text-xs px-3 py-1 rounded bg-amber-600 text-black">Create DRAFT revision</button>
              {bible && <button onClick={() => transitionBible(bible.bible_revision_id)} className="text-xs px-3 py-1 rounded bg-slate-700">Submit head for review</button>}
              {bible && bible.status === 'IN_REVIEW' && <button onClick={() => approveBible(bible.bible_revision_id)} className="text-xs px-3 py-1 rounded bg-amber-600 text-black">Approve as canon (Windows)</button>}
            </div>
            <div className="text-xs text-slate-500">Direct APPROVED creation is blocked in the API; approval requires the Windows reviewer.</div>
          </div>
          <DebugToggle title="Bible revision history" debug={revs}>
            <div className="text-xs text-slate-300">{revs ? `${revs.count} revision(s)` : 'none'}</div>
          </DebugToggle>
        </div>
      )}

      {tab === 'brief' && (
        <div className="border border-slate-700 rounded p-3 space-y-2">
          <div className="text-sm font-semibold">Episode Brief (new revision on save)</div>
          <div className="grid grid-cols-2 gap-2 text-xs text-slate-400">
            <label>Title *<input value={bTitle} onChange={e => setBTitle(e.target.value)} className="w-full mt-1 bg-slate-800 rounded px-2 py-1 text-sm text-slate-100" /></label>
            <label>Runtime (sec) *<input value={bRuntime} onChange={e => setBRuntime(e.target.value)} className="w-full mt-1 bg-slate-800 rounded px-2 py-1 text-sm text-slate-100" /></label>
            <label>Primary genre *<select value={bGenre} onChange={e => setBGenre(e.target.value)} className="w-full mt-1 bg-slate-800 rounded px-2 py-1 text-sm text-slate-100"><option value="GENRE_FANTASY">GENRE_FANTASY</option><option value="GENRE_COMEDY">GENRE_COMEDY</option></select></label>
            <label>Secondary (comma IDs)<input value={bSecondary} onChange={e => setBSecondary(e.target.value)} className="w-full mt-1 bg-slate-800 rounded px-2 py-1 text-sm text-slate-100" /></label>
            <label>Channel style (optional)<input value={bChannel} onChange={e => setBChannel(e.target.value)} placeholder="empty = channel-neutral" className="w-full mt-1 bg-slate-800 rounded px-2 py-1 text-sm text-slate-100" /></label>
          </div>
          <label className="block text-xs text-slate-400">Premise *<textarea value={bPremise} onChange={e => setBPremise(e.target.value)} className="w-full mt-1 bg-slate-800 rounded px-2 py-1 text-sm text-slate-100" rows={2} /></label>
          <label className="block text-xs text-slate-400">Synopsis<textarea value={bSynopsis} onChange={e => setBSynopsis(e.target.value)} className="w-full mt-1 bg-slate-800 rounded px-2 py-1 text-sm text-slate-100" rows={2} /></label>
          <div className="grid grid-cols-2 gap-2 text-xs text-slate-400">
            <label>Protagonist *<input value={bProtagonist} onChange={e => setBProtagonist(e.target.value)} className="w-full mt-1 bg-slate-800 rounded px-2 py-1 text-sm text-slate-100" /></label>
            <label>Objective *<input value={bObjective} onChange={e => setBObjective(e.target.value)} className="w-full mt-1 bg-slate-800 rounded px-2 py-1 text-sm text-slate-100" /></label>
            <label>Opposition<input value={bOpposition} onChange={e => setBOpposition(e.target.value)} className="w-full mt-1 bg-slate-800 rounded px-2 py-1 text-sm text-slate-100" /></label>
            <label>Conflict *<input value={bConflict} onChange={e => setBConflict(e.target.value)} className="w-full mt-1 bg-slate-800 rounded px-2 py-1 text-sm text-slate-100" /></label>
            <label>Stakes *<input value={bStakes} onChange={e => setBStakes(e.target.value)} className="w-full mt-1 bg-slate-800 rounded px-2 py-1 text-sm text-slate-100" /></label>
            <label>Ending direction *<input value={bEnding} onChange={e => setBEnding(e.target.value)} className="w-full mt-1 bg-slate-800 rounded px-2 py-1 text-sm text-slate-100" /></label>
          </div>
          <button onClick={saveBrief} disabled={loading} className="text-xs px-3 py-1 rounded bg-amber-600 text-black">Save as new revision</button>
          <DebugToggle title="Current brief" debug={brief}>
            <div className="text-sm">{brief ? `${brief.brief_revision_id} · v${brief.revision} · hash ${String(brief.content_hash_sha256).slice(0,12)}` : 'No brief yet.'}</div>
          </DebugToggle>
        </div>
      )}

      {tab === 'development' && (
        <div className="space-y-3">
          <div className="flex gap-2 flex-wrap">
            <button onClick={() => runStage('analysis')} disabled={loading} className="text-xs px-2 py-1 rounded bg-slate-700">1 Analysis</button>
            <button onClick={() => runStage('hooks')} disabled={loading} className="text-xs px-2 py-1 rounded bg-slate-700">2 Hooks</button>
            <button onClick={() => runStage('outline')} disabled={loading} className="text-xs px-2 py-1 rounded bg-slate-700">3 Outline</button>
            <button onClick={approveOutline} className="text-xs px-2 py-1 rounded bg-amber-600 text-black">Approve outline (Windows)</button>
          </div>
          <DebugToggle title={`Story analysis (${analysis?.status || 'none'})`} debug={analysis}><pre className="text-xs whitespace-pre-wrap max-h-64 overflow-auto">{JSON.stringify(analysis?.content || analysis?.analysis || null, null, 2)}</pre></DebugToggle>
          <DebugToggle title="Hook alternatives" debug={hooks}><pre className="text-xs whitespace-pre-wrap max-h-64 overflow-auto">{JSON.stringify(hooks?.content?.hooks || hooks?.hooks || null, null, 2)}</pre></DebugToggle>
          <DebugToggle title={`Outline — ${outline?.status || 'none'} (rev ${outline?.revision || '–'})`} debug={outline}><pre className="text-xs whitespace-pre-wrap max-h-64 overflow-auto">{JSON.stringify(outline?.content || outline?.outline || null, null, 2)}</pre></DebugToggle>
        </div>
      )}

      {tab === 'cards' && (
        <div className="space-y-3">
          <button onClick={() => runStage('cards')} disabled={loading} className="text-xs px-2 py-1 rounded bg-slate-700">Generate scene cards</button>
          {(cards?.content || cards?.scene_cards || []).map((c: any) => (
            <DebugToggle key={c.scene_id} title={`${c.scene_id} — ${c.location} · ${c.time}`} debug={c}>
              <div className="space-y-1 text-sm">
                <KV k="Characters" v={(c.characters || []).join(', ')} />
                <KV k="Objective" v={c.objective} />
                <KV k="Conflict" v={c.conflict} />
                <KV k="Action" v={c.action} />
                <KV k="Dramatic turn" v={c.dramatic_turn} />
                <KV k="Clue / reveal" v={c.clue_or_reveal} />
                <KV k="Emotional purpose" v={c.emotional_purpose} />
                <KV k="Visual storytelling" v={c.visual_storytelling} />
                <KV k="Estimated runtime" v={c.estimated_runtime_sec ? `${c.estimated_runtime_sec}s` : null} />
              </div>
            </DebugToggle>
          ))}
          {!cards && <div className="text-sm text-slate-400">No scene cards yet. Outline must be APPROVED first.</div>}
          {cards && <div className="text-xs text-slate-500">Outline revision: {JSON.stringify(cards.source_refs_json || cards.source_refs || 'recorded in artifact')}</div>}
        </div>
      )}

      {tab === 'screenplay' && (
        <div className="space-y-3">
          <button onClick={() => runStage('screenplay')} disabled={loading} className="text-xs px-2 py-1 rounded bg-slate-700">Generate screenplay</button>
          <DebugToggle title={`Screenplay — ${screenplay?.content?.script_id || screenplay?.script_id || 'none'}`} debug={screenplay}>
            {screenplay ? (
              <div className="space-y-2">
                <div className="text-xs text-slate-400">Version {screenplay.content?.version || screenplay.version} · context {screenplay.context_hash_sha256?.slice(0,12) || '–'} · source refs {JSON.stringify(screenplay.source_refs_json || {})}</div>
                {screenplay.markdown ? renderMarkdown(screenplay.markdown) : (screenplay.content?.markdown || screenplay.markdown || <div className="text-sm text-slate-400">Fetch the script detail via the scripts API for the full text.</div>)}
              </div>
            ) : <div className="text-sm text-slate-400">No screenplay yet. Requires APPROVED outline + scene cards.</div>}
          </DebugToggle>
        </div>
      )}

      {tab === 'qc' && (
        <div className="space-y-3">
          <div className="flex gap-2">
            <button onClick={runQc} className="text-xs px-2 py-1 rounded bg-slate-700">Run deterministic validation</button>
            <button onClick={runCritique} className="text-xs px-2 py-1 rounded bg-slate-700">Run creative critique</button>
          </div>
          <DebugToggle title={`Deterministic validation — ${qc?.outcome || 'none'}`} debug={qc}>
            {qc ? (<div className="space-y-1 text-sm"><div>Outcome: {qc.outcome} · runtime est {qc.runtime_estimate?.total_sec ?? '–'}s ({qc.runtime_estimate?.method || ''})</div>{(qc.issues || []).map((i: any, idx: number) => (<div key={idx} className="text-xs"><b>{i.severity}</b> {i.scene_id && `[${i.scene_id}]`} {i.detail}</div>))}</div>) : <div className="text-sm text-slate-400">Not run yet.</div>}
          </DebugToggle>
          <DebugToggle title="Creative critique (separate from QC)" debug={critique}>
            {critique ? (<div className="space-y-2">{(critique.findings || []).map((f: any, idx: number) => (<div key={idx} className="text-xs border-b border-slate-700 pb-1"><b>{f.severity}</b> {f.scene_id} — {f.category}: {f.evidence} <span className="text-slate-400">→ {f.recommendation}</span></div>))}</div>) : <div className="text-sm text-slate-400">Not run yet.</div>}
          </DebugToggle>
        </div>
      )}

      {tab === 'approval' && (
        <div className="space-y-3">
          <div className="text-sm">Exact revision: <b>{screenplay?.content?.script_id || screenplay?.script_id || 'none'} v{screenplay?.content?.version || screenplay?.version || '–'}</b></div>
          <div className="text-xs text-slate-400">QC: {qc?.outcome || 'not run'} · Critique findings: {(critique?.findings || []).length} · Outstanding BLOCKER: {(qc?.issues || []).filter((i: any) => i.severity === 'BLOCKER').length}</div>
          <label className="block text-xs text-slate-400">Approval comments<textarea value={comments} onChange={e => setComments(e.target.value)} placeholder="Decision rationale (include acknowledge for MAJOR findings if needed)" className="w-full mt-1 bg-slate-800 rounded px-2 py-1 text-sm text-slate-100" rows={2} /></label>
          <button onClick={approveScreenplay} className="text-xs px-3 py-1 rounded bg-amber-600 text-black">Approve screenplay (Windows)</button>
          <div className="text-xs text-slate-500">APPROVED is shown only after the backend confirms the decision. Approval requires exact-revision QC PASS with no BLOCKER + a creative critique.</div>
        </div>
      )}
    </div>
  );
}

export default function App() {
  const { activeProjectId, setActiveProjectId, operatingMode } = useForgeStore();
  const [projects, setProjects] = useState<Project[]>([]);
  const [project, setProject] = useState<Project | null>(null);
  const [stepsData, setStepsData] = useState<any>(null);
  const [dashboard, setDashboard] = useState<Dashboard | null>(null);
  const [health, setHealth] = useState<any>(null);
  const [error, setError] = useState<string | null>(null);
  const [selectedStage, setSelectedStage] = useState<string>('USER_STORY_IDEA');
  const [stageData, setStageData] = useState<Record<string, any>>({});
  const [loadingStage, setLoadingStage] = useState(false);
  const [showFiles, setShowFiles] = useState(false);
  const [showProvenance, setShowProvenance] = useState(false);
  const [showStory, setShowStory] = useState(false);

  const loadProjects = useCallback(async () => {
    try {
      const [h, list] = await Promise.all([
        apiJson('/api/health'),
        apiJson('/api/projects'),
      ]);
      setHealth(h);
      const ps = list.projects || [];
      setProjects(ps);
      if (ps.length && !ps.some((p: any) => p.project_id === activeProjectId)) {
        setActiveProjectId(ps[0].project_id);
      }
    } catch (e: any) { setError(e.message || String(e)); }
  }, [activeProjectId, setActiveProjectId]);

  const loadProject = useCallback(async () => {
    if (!activeProjectId) return;
    try {
      setError(null);
      const [p, s, d] = await Promise.all([
        apiJson(`/api/projects/${activeProjectId}`),
        apiJson(`/api/projects/${activeProjectId}/steps`),
        apiJson('/api/dashboard'),
      ]);
      setProject(p.project);
      setStepsData(s);
      setDashboard(d);
    } catch (e: any) { setError(e.message || String(e)); }
  }, [activeProjectId]);

  useEffect(() => { loadProjects(); }, [loadProjects]);
  useEffect(() => { loadProject(); }, [loadProject]);

  const selectedStep = useMemo(
    () => stepsData?.steps?.find((s: Step) => s.stage === selectedStage) || null,
    [stepsData, selectedStage],
  );

  useEffect(() => {
    if (!activeProjectId || !selectedStage) return;
    const keys = STAGE_ENDPOINTS[selectedStage] || [];
    let alive = true;
    setLoadingStage(true);
    (async () => {
      const out: Record<string, any> = {};
      for (const key of keys) {
        try {
          if (key === 'project') out.project = await apiJson(`/api/projects/${activeProjectId}`);
          else if (key === 'dashboard') out.dashboard = dashboard || await apiJson('/api/dashboard');
          else if (key === 'steps') out.steps = stepsData || await apiJson(`/api/projects/${activeProjectId}/steps`);
          else out[key] = await apiJson(`/api/projects/${activeProjectId}/${key}`);
        } catch (e: any) { out[key] = { error: String(e.message || e) }; }
      }
      if (alive) { setStageData(out); setLoadingStage(false); }
    })();
    return () => { alive = false; };
  }, [activeProjectId, selectedStage, dashboard, stepsData]);

  const [filesData, setFilesData] = useState<any>(null);
  const [execData, setExecData] = useState<any>(null);
  useEffect(() => {
    if (!activeProjectId) return;
    apiJson(`/api/projects/${activeProjectId}/files`).then(setFilesData).catch(() => setFilesData(null));
    apiJson(`/api/projects/${activeProjectId}/executions`).then(setExecData).catch(() => setExecData(null));
  }, [activeProjectId]);

  return (
    <div className="min-h-screen bg-[#0B0F19] text-slate-100 flex">
      <aside className="w-80 shrink-0 bg-[#111827] border-r border-slate-800 p-4 flex flex-col overflow-auto">
        <h1 className="text-lg font-bold text-amber-400 tracking-wide">ANIMATION FORGE</h1>
        <div className="mt-3">
          <label className="text-xs text-slate-400">Project</label>
          <select
            value={activeProjectId}
            onChange={e => { setActiveProjectId(e.target.value); setSelectedStage('USER_STORY_IDEA'); }}
            className="w-full mt-1 bg-slate-800 rounded px-2 py-2 text-sm"
          >
            {projects.map((p: any) => (
              <option key={p.project_id} value={p.project_id}>
                {p.title} ({p.project_id}) — {p.current_stage}
              </option>
            ))}
          </select>
          {project && (
            <div className="text-xs text-slate-400 mt-2 space-y-0.5">
              <div>{project.title} · {project.status}</div>
              <div>Stage: {project.current_stage} · Mode: {operatingMode}</div>
              <div>Updated: {project.updated_at}</div>
            </div>
          )}
        </div>
        <nav className="mt-4 flex flex-col gap-1">
          {(stepsData?.steps || []).map((s: Step) => (
            <button
              key={s.stage}
              onClick={() => { setSelectedStage(s.stage); setShowFiles(false); setShowProvenance(false); }}
              className={`text-left px-2 py-1.5 rounded text-xs ${selectedStage === s.stage ? 'bg-amber-500/20 text-amber-300' : 'text-slate-300 hover:bg-slate-800'}`}
            >
              <div className="flex justify-between gap-1">
                <span>{s.stage_number}. {s.stage}</span><Chip label={s.progress} />
              </div>
              <div className="flex gap-1 mt-1 flex-wrap">
                <Chip label={s.capability_status} />
                <span className="text-slate-500">{s.output_count} outputs · {s.evidence_status}</span>
              </div>
            </button>
          ))}
        </nav>
        <div className="mt-3 flex flex-wrap gap-2">
          <button onClick={() => { setShowFiles(!showFiles); setShowProvenance(false); setShowStory(false); }} className={`text-xs px-2 py-1 rounded ${showFiles ? 'bg-amber-600 text-black' : 'bg-slate-700'}`}>Files</button>
          <button onClick={() => { setShowProvenance(!showProvenance); setShowFiles(false); setShowStory(false); }} className={`text-xs px-2 py-1 rounded ${showProvenance ? 'bg-amber-600 text-black' : 'bg-slate-700'}`}>Provenance / Debug</button>
          <button onClick={() => { setShowStory(!showStory); setShowFiles(false); setShowProvenance(false); }} className={`text-xs px-2 py-1 rounded ${showStory ? 'bg-amber-600 text-black' : 'bg-slate-700'}`}>Story Context (CR_006)</button>
          <button onClick={() => { loadProjects(); loadProject(); }} className="text-xs px-2 py-1 rounded bg-slate-800 hover:bg-slate-700">Refresh</button>
        </div>
        <div className="mt-auto pt-4 text-xs text-slate-500">
          {health ? <>API: <span className={health.status === 'healthy' ? 'text-green-400' : 'text-red-400'}>{health.status}</span> · {health.architecture_version} · DB {health.database_integrity?.table_count} tbl</> : 'API: …'}
        </div>
      </aside>
      <main className="flex-1 p-6 overflow-auto">
        {error && <div className="mb-4 p-3 rounded bg-red-900/40 text-red-200 text-sm">Error: {error} (is backend running on 127.0.0.1:8765?)</div>}
        {showFiles && (
          <div>
            <h2 className="text-xl font-semibold text-amber-400 uppercase mb-3">Project files</h2>
            <FilesExplorer projectId={activeProjectId} filesData={filesData} />
          </div>
        )}
        {showStory && (
          <div>
            <h2 className="text-xl font-semibold text-amber-400 uppercase mb-3">Story Context & Screenplay (CR_006)</h2>
            <StoryContextPanel projectId={activeProjectId} />
          </div>
        )}
        {showProvenance && (
          <div>
            <h2 className="text-xl font-semibold text-amber-400 uppercase mb-3">Provenance / Debug</h2>
            <div className="text-xs text-slate-400 mb-3">{execData?.agent_prompts_note || ''} Secret-like fields are redacted server-side.</div>
            {(execData?.agent_executions || []).map((ex: any) => (
              <DebugToggle key={ex.operation_id} title={`Execution ${ex.operation_id} — ${ex.agent_id} (${ex.status})`} debug={ex}>
                <KV k="Mode" v={ex.operating_mode} /><KV k="Started" v={ex.started_at} /><KV k="Completed" v={ex.completed_at} />
                <div className="text-sm mt-1">Prompt versions: {Object.entries(ex.prompt_versions || {}).map(([k, v]: any) => <span key={k} className="mr-2">{k}: {JSON.stringify(v)}</span>)}</div>
              </DebugToggle>
            ))}
            {(execData?.agent_executions || []).length === 0 && <div className="text-sm text-slate-400 mb-3">No agent executions recorded.</div>}
            <div className="text-sm font-semibold mb-1">Prompt metadata (id / version / hash)</div>
            <div className="overflow-auto border border-slate-700 rounded mb-3">
              <table className="w-full text-xs">
                <thead><tr className="bg-slate-800">{['Prompt', 'Version', 'File', 'Hash (short)', 'Modified'].map(h => <th key={h} className="p-2 text-left">{h}</th>)}</tr></thead>
                <tbody>{(execData?.agent_prompts || []).map((p: any, i: number) => (
                  <tr key={i} className="border-t border-slate-800"><td className="p-2">{p.prompt_id}</td><td className="p-2">{p.version}</td><td className="p-2">{p.file_path}</td><td className="p-2">{String(p.content_hash || '').slice(0, 12)}…</td><td className="p-2">{p.modified_date}</td></tr>
                ))}</tbody>
              </table>
            </div>
            <div className="text-sm font-semibold mb-1">Execution logs (redacted, latest 100)</div>
            {(execData?.execution_logs || []).map((l: any) => (
              <DebugToggle key={l.log_id} title={`${l.logged_at} [${l.level}] ${l.component}`} debug={l}>
                <div className="text-sm">{l.message_redacted}</div>
              </DebugToggle>
            ))}
            {(execData?.execution_logs || []).length === 0 && <div className="text-sm text-slate-400">No execution logs recorded.</div>}
          </div>
        )}
        {!showFiles && !showProvenance && selectedStep && (
          <div>
            <div className="flex items-center justify-between mb-2">
              <h2 className="text-xl font-semibold text-amber-400 uppercase">{selectedStep.stage_number}. {selectedStep.stage}</h2>
              <span className="text-xs text-slate-400">{loadingStage ? 'Loading…' : ''}</span>
            </div>
            <div className="flex gap-2 flex-wrap mb-3">
              <Chip label={selectedStep.progress} />
              <Chip label={selectedStep.capability_status} />
              <Chip label={selectedStep.evidence_status} />
              <span className="text-xs text-slate-400">Outputs: {selectedStep.output_count} · Inputs: {selectedStep.input_count} · Approval: {selectedStep.approval_state || 'n/a'}</span>
            </div>
            {selectedStep.capability_note && <div className="text-xs text-slate-400 mb-2">{selectedStep.capability_note}</div>}
            {selectedStep.blockers.map((b: string) => <div key={b} className="text-xs text-amber-300 mb-1">Blocker: {b}</div>)}
            <div className="text-xs text-slate-500 mb-3">Overview: inputs, processing/provenance and outputs for this stage are shown below. Use Source / Debug on any card for raw records, hashes and paths.</div>
            {stageData.project?.error && <div className="text-red-300 text-sm">{stageData.project.error}</div>}
            {stageViewer(activeProjectId, selectedStep.stage, stageData, stepsData)}
          </div>
        )}
      </main>
    </div>
  );
}
