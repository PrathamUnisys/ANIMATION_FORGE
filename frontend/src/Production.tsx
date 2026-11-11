import React, { useCallback, useEffect, useMemo, useState } from 'react';

/**
 * The Production workspace.
 *
 * One spine, in studio order, from the script to the handoff. The rail on the
 * left is the pipeline, the middle is the stage, and the panel on the right is
 * the inspector for whatever is selected. The prompt inspector is the place
 * where the user takes the prompt over: the generated prompt is shown as
 * generated, the user's own text sits on top of it, and the merged result is
 * what would actually be sent to ComfyUI.
 */

const STAGES: { id: string; label: string; studio: string }[] = [
  { id: 'SCRIPT', label: 'Script', studio: 'Screenplay' },
  { id: 'BREAKDOWN', label: 'Breakdown', studio: 'Script Breakdown' },
  { id: 'VISUAL_DIRECTION', label: 'Visual Direction', studio: 'Art Direction' },
  { id: 'BOARDS', label: 'Boards', studio: 'Storyboard' },
  { id: 'PREVIZ', label: 'Previz', studio: 'Animatic / Layout' },
  { id: 'CONTINUITY', label: 'Continuity', studio: 'Continuity Check' },
  { id: 'HANDOFF', label: 'Handoff', studio: 'Package / Conform' },
];

const STATUS_TONE: Record<string, string> = {
  NOT_STARTED: 'bg-slate-700 text-slate-300',
  BOARDED: 'bg-sky-800 text-sky-100',
  PREVIZ: 'bg-violet-800 text-violet-100',
  APPROVED: 'bg-emerald-800 text-emerald-100',
  BLOCKED: 'bg-red-900 text-red-200',
  DRAFT: 'bg-amber-800 text-amber-100',
  DETECTED: 'bg-slate-700 text-slate-200',
  NEEDS_REFERENCE: 'bg-amber-800 text-amber-100',
  CONFIRMED: 'bg-emerald-800 text-emerald-100',
};

const MODULE_LABELS: Record<string, string> = {
  style: 'Style (locked prefix)',
  scene_context: 'Scene context',
  environment: 'Environment',
  characters: 'Characters',
  action: 'Action',
  objects: 'Objects',
  camera: 'Camera',
  composition: 'Composition',
  lighting: 'Lighting',
  atmosphere: 'Atmosphere',
  emphasis: 'Emphasis / frame constraint',
};

/**
 * An image from the package.
 *
 * The media route is token protected and an img tag cannot send a header, so
 * the file is fetched with the same credentialed request as everything else and
 * shown from a blob URL. That works in the browser and in the desktop shell.
 */
function PackageImage({
  apiFetch,
  projectId,
  relPath,
  alt,
  className,
}: {
  apiFetch: (path: string, init?: RequestInit) => Promise<Response>;
  projectId: string;
  relPath: string;
  alt: string;
  className?: string;
}) {
  const [url, setUrl] = useState<string | null>(null);
  const [failed, setFailed] = useState(false);

  useEffect(() => {
    let alive = true;
    let objectUrl = '';
    if (!relPath) {
      setFailed(true);
      return;
    }
    apiFetch(
      `/api/visual-development/${projectId}/media?path=${encodeURIComponent(relPath)}`
    )
      .then(async (response) => {
        if (!response.ok) throw new Error(String(response.status));
        const blob = await response.blob();
        objectUrl = URL.createObjectURL(blob);
        if (alive) setUrl(objectUrl);
      })
      .catch(() => {
        if (alive) setFailed(true);
      });
    return () => {
      alive = false;
      if (objectUrl) URL.revokeObjectURL(objectUrl);
    };
  }, [apiFetch, projectId, relPath]);

  if (failed) {
    return <div className={`${className || ''} bg-slate-900 flex items-center justify-center text-[9px] text-slate-600`}>no image</div>;
  }
  if (!url) {
    return <div className={`${className || ''} bg-slate-900`} />;
  }
  return <img src={url} alt={alt} className={className} />;
}

type Token = { label: string; value: string };

export default function ProductionWorkspace({
  apiFetch,
  apiJson,
  onOpenMedia,
}: {
  apiFetch: (path: string, init?: RequestInit) => Promise<Response>;
  apiJson: (path: string) => Promise<any>;
  onOpenMedia: (projectId: string, relPath: string) => void;
}) {
  const [packages, setPackages] = useState<any[]>([]);
  const [projectId, setProjectId] = useState('');
  const [pipeline, setPipeline] = useState<any>(null);
  const [breakdown, setBreakdown] = useState<any>(null);
  const [animatic, setAnimatic] = useState<any>(null);
  // A stage can be linked to directly: ?stage=BOARDS opens the boards.
  const [stage, setStage] = useState<string>(() => {
    const requested = new URLSearchParams(window.location.search).get('stage');
    return requested && STAGES.some((s) => s.id === requested) ? requested : 'SCRIPT';
  });
  const [selected, setSelected] = useState<string>('');
  const [error, setError] = useState<string | null>(null);
  const [busy, setBusy] = useState<string | null>(null);

  // The visual development packages are their own namespace, separate from
  // the Animation Forge projects, so the workspace picks one explicitly.
  useEffect(() => {
    apiJson('/api/visual-development/projects')
      .then((r) => {
        const list = r.projects || [];
        setPackages(list);
        if (list.length) setProjectId((current) => current || list[0].project_id);
      })
      .catch((e: any) => setError(e.message || String(e)));
  }, [apiJson]);

  const load = useCallback(async () => {
    if (!projectId) return;
    try {
      setError(null);
      const [pipe, brk, anim] = await Promise.all([
        apiJson(`/api/production/${projectId}/pipeline`),
        apiJson(`/api/production/${projectId}/breakdown`),
        apiJson(`/api/production/${projectId}/animatic`),
      ]);
      setPipeline(pipe);
      setBreakdown(brk);
      setAnimatic(anim);
    } catch (e: any) {
      setError(e.message || String(e));
    }
  }, [projectId, apiJson]);

  useEffect(() => { load(); }, [load]);

  const shots: any[] = pipeline?.shots || [];
  const candidates: any[] = pipeline?.candidates || [];

  // A stage that is opened directly, by link, still needs something selected.
  useEffect(() => {
    if (selected) return;
    if (stage === 'VISUAL_DIRECTION' && candidates.length) setSelected(candidates[0].candidate_id);
    else if ((stage === 'BOARDS' || stage === 'PREVIZ') && shots.length) setSelected(shots[0].shot_id);
  }, [stage, candidates, shots, selected]);

  const targetKind = selected.startsWith('SHT_') ? 'SHOT' : selected.startsWith('ART_') ? 'ART_DIRECTION_CANDIDATE' : '';

  const chooseStage = (id: string) => {
    setStage(id);
    // Selecting a stage moves the selection to something that belongs to it.
    if (id === 'BOARDS' || id === 'PREVIZ') setSelected(shots[0]?.shot_id || '');
    else if (id === 'VISUAL_DIRECTION') setSelected(candidates[0]?.candidate_id || '');
    else setSelected('');
  };

  const approveStyleBible = async () => {
    setBusy('approve style bible');
    setError(null);
    try {
      const response = await apiFetch(
        `/api/production/${projectId}/style-bible/approve`,
        { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: '{}' }
      );
      if (!response.ok) {
        const text = await response.text();
        throw new Error(text || `approve -> ${response.status}`);
      }
      await load();
    } catch (e: any) {
      setError(e.message || String(e));
    } finally {
      setBusy(null);
    }
  };

  // A human decision. The endpoint already exists; the workspace was simply
  // never calling it, which left the status chips as decoration.
  const decide = async (
    action: string,
    targetType: string,
    targetId: string,
    note = ''
  ) => {
    setBusy(`${action} ${targetId}`);
    setError(null);
    try {
      const response = await apiFetch(
        `/api/visual-development/${projectId}/decision`,
        {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            action,
            target_type: targetType,
            target_id: targetId,
            actor: 'frontend',
            note,
          }),
        }
      );
      if (!response.ok) {
        const text = await response.text();
        throw new Error(text || `decision -> ${response.status}`);
      }
      await load();
    } catch (e: any) {
      setError(e.message || String(e));
    } finally {
      setBusy(null);
    }
  };

  return (
    <div className="flex gap-4 min-h-[34rem]">
      {/* The pipeline rail. */}
      <div className="w-56 shrink-0">
        <select
          value={projectId}
          onChange={(e) => { setProjectId(e.target.value); setSelected(''); }}
          className="w-full bg-slate-800 rounded px-2 py-1 text-xs mb-3"
        >
          {packages.length === 0 && <option value="">no visual development packages</option>}
          {packages.map((p: any) => (
            <option key={p.project_id} value={p.project_id}>
              {p.title} ({p.source_script?.approval_status})
            </option>
          ))}
        </select>
        <div className="flex items-center justify-between gap-2 mb-2">
          <span className="text-[10px] text-slate-500">
            {pipeline?.stages?.length || 0} stages
          </span>
          <button
            onClick={load}
            className="text-[10px] px-2 py-0.5 rounded bg-slate-700 text-slate-200"
          >
            Refresh
          </button>
        </div>
        {STAGES.map((entry, index) => {
          const state = (pipeline?.stages || []).find((s: any) => s.stage_id === entry.id);
          const active = stage === entry.id;
          return (
            <button
              key={entry.id}
              onClick={() => chooseStage(entry.id)}
              className={`w-full text-left px-3 py-2 rounded mb-1 border ${
                active
                  ? 'bg-amber-600 text-black border-amber-500'
                  : 'bg-[#111827] border-slate-800 text-slate-300 hover:bg-slate-800'
              }`}
            >
              <div className="flex items-center justify-between gap-2">
                <span className="text-xs font-semibold">
                  {index + 1}. {entry.label}
                </span>
                <span
                  className={`w-2 h-2 rounded-full shrink-0 ${
                    state?.complete ? 'bg-emerald-400' : 'bg-slate-600'
                  }`}
                  title={state?.complete ? 'complete' : 'not started'}
                />
              </div>
              <div className="text-[10px] opacity-70">{entry.studio}</div>
            </button>
          );
        })}
        {pipeline?.shot_statuses && (
          <div className="mt-3 text-[11px] text-slate-400 space-y-1">
            <div className="font-semibold text-slate-300">Shots</div>
            {Object.entries(pipeline.shot_statuses).map(([status, count]) => (
              <div key={status} className="flex justify-between gap-2">
                <span className="inline-block px-1.5 rounded text-[10px] ${STATUS_TONE[status] || ''}">
                  <span className={STATUS_TONE[status] || ''}>■</span> {status.replace('_', ' ')}
                </span>
                <span>{String(count)}</span>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* The stage. */}
      <div className="flex-1 min-w-0 overflow-auto">
        {error && <div className="p-2 rounded bg-red-900/40 text-red-200 text-xs mb-3">{error}</div>}
        {busy && <div className="p-2 rounded bg-amber-900/30 text-amber-200 text-xs mb-3">{busy}</div>}

        {stage === 'SCRIPT' && (
          <ScriptStage
            pipeline={pipeline}
            projectId={projectId}
            apiJson={apiJson}
            onOpenMedia={onOpenMedia}
          />
        )}
        {stage === 'BREAKDOWN' && <BreakdownStage breakdown={breakdown} />}
        {stage === 'VISUAL_DIRECTION' && (
          <VisualDirectionStage
            apiFetch={apiFetch}
            candidates={candidates}
            selected={selected}
            onSelect={setSelected}
            projectId={projectId}
            onOpenMedia={onOpenMedia}
            onDecide={decide}
            busy={busy}
            pipeline={pipeline}
            onApproveStyleBible={approveStyleBible}
          />
        )}
        {(stage === 'BOARDS' || stage === 'PREVIZ') && (
          <BoardsStage
            apiFetch={apiFetch}
            shots={shots}
            selected={selected}
            onSelect={setSelected}
            projectId={projectId}
            onOpenMedia={onOpenMedia}
            showBlocking={stage === 'PREVIZ'}
            animatic={animatic}
            onDecide={decide}
            busy={busy}
          />
        )}
        {stage === 'CONTINUITY' && <ContinuityStage pipeline={pipeline} />}
        {stage === 'HANDOFF' && <HandoffStage pipeline={pipeline} projectId={projectId} />}
      </div>

      {/* The inspector. */}
      <div className="w-[26rem] shrink-0 border-l border-slate-800 pl-4 overflow-auto">
        {selected && targetKind ? (
          <PromptInspector
            key={selected}
            apiFetch={apiFetch}
            apiJson={apiJson}
            projectId={projectId}
            targetId={selected}
            kind={targetKind}
            onSaved={load}
          />
        ) : (
          <div className="text-xs text-slate-500">
            Select a direction or a shot to open its prompt.
          </div>
        )}
      </div>
    </div>
  );
}

/**
 * The animatic video, fetched as a blob.
 *
 * The media route is token protected and a video tag cannot send a header,
 * so the file is fetched with the credentialed request and played from a blob
 * URL.
 */
function useAnimaticVideo(
  apiFetch: (path: string, init?: RequestInit) => Promise<Response>,
  projectId: string,
  relPath: string
) {
  const [url, setUrl] = useState<string | null>(null);

  useEffect(() => {
    let alive = true;
    let objectUrl = '';
    if (!relPath || !projectId) {
      setUrl(null);
      return;
    }
    apiFetch(
      `/api/visual-development/${projectId}/media?path=${encodeURIComponent(relPath)}`
    )
      .then(async (response) => {
        if (!response.ok) throw new Error(String(response.status));
        const blob = await response.blob();
        objectUrl = URL.createObjectURL(blob);
        if (alive) setUrl(objectUrl);
      })
      .catch(() => {
        if (alive) setUrl(null);
      });
    return () => {
      alive = false;
      if (objectUrl) URL.revokeObjectURL(objectUrl);
    };
  }, [apiFetch, projectId, relPath]);

  return url;
}

/* ------------------------------------------------------------------ stages */

function ScriptStage({
  pipeline,
  projectId,
  apiJson,
  onOpenMedia,
}: {
  pipeline: any;
  projectId: string;
  apiJson: (path: string) => Promise<any>;
  onOpenMedia: (projectId: string, relPath: string) => void;
}) {
  const link = pipeline?.link || {};
  const episode = pipeline?.episode || {};
  const [script, setScript] = useState<any>(null);
  const [showScript, setShowScript] = useState(false);

  useEffect(() => {
    if (!projectId) return;
    apiJson(`/api/production/${projectId}/script`)
      .then(setScript)
      .catch(() => setScript(null));
  }, [projectId, apiJson]);

  return (
    <div>
      <h3 className="text-lg font-semibold text-amber-300 mb-2">Script</h3>
      <div className="text-xs text-slate-400 mb-3">
        {link.script_id || 'no script linked'} &middot;{' '}
        <span className={link.approval_status === 'APPROVED' ? 'text-emerald-300' : 'text-amber-300'}>
          {link.approval_status || 'unknown'}
        </span>
        {link.source_sha256 && (
          <span className="text-slate-500"> &middot; sha256 {link.source_sha256.slice(0, 12)}&hellip;</span>
        )}
      </div>
      <div className="card bg-[#111827] border border-slate-800 rounded p-3 text-xs space-y-1">
        <div><span className="text-slate-400">Title</span> {episode.title || '-'}</div>
        <div><span className="text-slate-400">Genre</span> {episode.genre || '-'}</div>
        <div><span className="text-slate-400">Runtime</span> {episode.target_runtime_sec || '-'} s</div>
        <div><span className="text-slate-400">Logline</span> {episode.logline || '-'}</div>
      </div>
      <button
        onClick={() => setShowScript(!showScript)}
        className="text-xs px-2 py-1 rounded bg-slate-700 text-slate-200 mt-3"
      >
        {showScript ? 'Hide the script' : 'Read the script'}
      </button>
      {showScript && script?.text && (
        <pre className="text-[11px] text-slate-300 bg-[#0b0f19] border border-slate-800 rounded p-3 mt-2 max-h-96 overflow-auto whitespace-pre-wrap">
          {script.text}
        </pre>
      )}
      {pipeline?.open_questions?.length > 0 && (
        <div className="mt-3 text-xs text-amber-200 bg-amber-900/20 border border-amber-800 rounded p-2">
          <div className="font-semibold mb-1">Open questions &mdash; the script does not say this:</div>
          <ul className="list-disc ml-4">
            {pipeline.open_questions.map((q: string, i: number) => <li key={i}>{q}</li>)}
          </ul>
        </div>
      )}
    </div>
  );
}

function BreakdownStage({ breakdown }: { breakdown: any }) {
  if (!breakdown || breakdown.status === 'NOT_RUN') {
    return (
      <div className="text-xs text-slate-400">
        No breakdown yet. Run <code className="text-amber-300">breakdown</code> for this project.
      </div>
    );
  }
  const taxonomy: any[] = breakdown.taxonomy || [];
  const colors = Object.fromEntries(taxonomy.map((t: any) => [t.category, t.color]));
  const labels = Object.fromEntries(taxonomy.map((t: any) => [t.category, t.label]));
  return (
    <div>
      <h3 className="text-lg font-semibold text-amber-300 mb-1">Script breakdown</h3>
      <div className="text-xs text-slate-400 mb-3">
        {breakdown.summary.scene_count} scenes &middot; {breakdown.summary.element_count} elements &middot;{' '}
        {breakdown.summary.total_page_eighths} eighths of a page
      </div>
      <div className="flex flex-wrap gap-1 mb-3">
        {Object.entries(breakdown.summary.by_category)
          .filter(([, count]: any) => count > 0)
          .map(([category, count]: any) => (
            <span
              key={category}
              className="text-[10px] px-2 py-0.5 rounded"
              style={{ background: (colors as any)[category] || '#444', color: '#fff' }}
            >
              {labels[category] || category}: {String(count)}
            </span>
          ))}
      </div>
      {(breakdown.scenes || []).map((scene: any) => (
        <div key={scene.scene_id} className="mb-3 bg-[#111827] border border-slate-800 rounded p-3">
          <div className="flex items-baseline justify-between gap-2 mb-2">
            <span className="text-xs font-semibold text-slate-200">{scene.heading}</span>
            <span className="text-[10px] text-slate-500">
              {scene.shot_count} shots &middot; {scene.page_eighths} eighths
            </span>
          </div>
          <div className="flex flex-wrap gap-1">
            {scene.elements.map((element: any, i: number) => (
              <span
                key={i}
                title={`${element.category} &middot; ${element.detail || ''}`}
                className="text-[10px] px-2 py-0.5 rounded text-white"
                style={{ background: (colors as any)[element.category] || '#444', opacity: element.source === 'INFERRED' ? 0.6 : 1 }}
              >
                {element.name}
                {element.quantity > 1 ? ` ×${element.quantity}` : ''}
                {element.source === 'INFERRED' ? ' (inferred)' : ''}
              </span>
            ))}
            {scene.elements.length === 0 && (
              <span className="text-[10px] text-slate-500">nothing tagged</span>
            )}
          </div>
          {scene.untagged_categories?.length > 0 && (
            <div className="text-[10px] text-slate-500 mt-2">
              Not tagged in this scene: {scene.untagged_categories.join(', ')}
            </div>
          )}
        </div>
      ))}
    </div>
  );
}

function VisualDirectionStage({
  apiFetch,
  candidates,
  selected,
  onSelect,
  projectId,
  onDecide,
  busy,
  pipeline,
  onApproveStyleBible,
}: {
  apiFetch: (path: string, init?: RequestInit) => Promise<Response>;
  candidates: any[];
  selected: string;
  onSelect: (id: string) => void;
  projectId: string;
  onOpenMedia: (projectId: string, relPath: string) => void;
  onDecide: (action: string, targetType: string, targetId: string, note?: string) => void;
  busy: string | null;
  pipeline: any;
  onApproveStyleBible: () => void;
}) {
  const styleIdentity = pipeline?.art_direction?.style_identity || '';
  const styleApproved = pipeline?.style_bible_approved === true;
  return (
    <div>
      <h3 className="text-lg font-semibold text-amber-300 mb-1">Visual direction</h3>
      <div className="text-xs text-slate-400 mb-1">
        Every candidate uses the same scene and the same seed, so the only difference is the direction.
      </div>
      {styleIdentity && (
        <div className="text-xs mb-3 flex items-center gap-2">
          <span className="text-slate-300">Style Bible: {styleIdentity}</span>
          {styleApproved ? (
            <span className="text-[10px] px-1.5 py-0.5 rounded bg-emerald-800 text-emerald-100">
              Approved
            </span>
          ) : (
            <button
              onClick={onApproveStyleBible}
              disabled={busy !== null}
              className="text-[10px] px-2 py-0.5 rounded bg-amber-600 text-black disabled:opacity-50"
            >
              Approve the Style Bible
            </button>
          )}
        </div>
      )}
      <div className="grid grid-cols-2 xl:grid-cols-3 gap-3">
        {candidates.map((candidate: any) => (
          <button
            key={candidate.candidate_id}
            onClick={() => onSelect(candidate.candidate_id)}
            className={`text-left bg-[#111827] border rounded overflow-hidden ${
              selected === candidate.candidate_id ? 'border-amber-500' : 'border-slate-800'
            }`}
          >
            {candidate.image_path ? (
              <PackageImage
                apiFetch={apiFetch}
                projectId={projectId}
                relPath={candidate.image_path}
                alt={candidate.candidate_id}
                className="w-full aspect-square object-cover"
              />
            ) : (
              <div className="w-full aspect-square bg-slate-900 flex items-center justify-center text-[10px] text-slate-600">
                not generated
              </div>
            )}
            <div className="p-2">
              <div className="text-xs font-semibold text-slate-200">
                {candidate.candidate_id} &middot; {candidate.style_name}
              </div>
              <div className="text-[10px] text-slate-400 mt-0.5">{candidate.description}</div>
              <div className="mt-1 flex items-center gap-1">
                {candidate.selected ? (
                  <span className="text-[10px] px-1.5 py-0.5 rounded bg-emerald-800 text-emerald-100">
                    Selected
                  </span>
                ) : (
                  <button
                    onClick={() => onDecide('SELECT', 'ART_DIRECTION_CANDIDATE', candidate.candidate_id)}
                    disabled={busy !== null}
                    className="text-[10px] px-2 py-0.5 rounded bg-amber-600 text-black disabled:opacity-50"
                  >
                    Select this direction
                  </button>
                )}
                <button
                  onClick={() => onSelect(candidate.candidate_id)}
                  className="text-[10px] px-2 py-0.5 rounded bg-slate-700 text-slate-200"
                >
                  Inspect prompt
                </button>
              </div>
            </div>
          </button>
        ))}
      </div>
    </div>
  );
}

function BoardsStage({
  apiFetch,
  shots,
  selected,
  onSelect,
  projectId,
  showBlocking,
  animatic,
  onDecide,
  busy,
}: {
  apiFetch: (path: string, init?: RequestInit) => Promise<Response>;
  shots: any[];
  selected: string;
  onSelect: (id: string) => void;
  projectId: string;
  onOpenMedia: (projectId: string, relPath: string) => void;
  showBlocking: boolean;
  animatic: any;
  onDecide: (action: string, targetType: string, targetId: string, note?: string) => void;
  busy: string | null;
}) {
  const entries: any[] = animatic?.entries || [];
  const videoUrl = useAnimaticVideo(apiFetch, projectId, animatic?.video_relative_path || '');

  return (
    <div>
      <h3 className="text-lg font-semibold text-amber-300 mb-1">
        {showBlocking ? 'Previz' : 'Boards'}
      </h3>
      <div className="text-xs text-slate-400 mb-3">
        One frame per shot, in shot order. Each shot carries its own prompt and its own status.
      </div>

      {showBlocking && (
        <div className="bg-[#111827] border border-slate-800 rounded p-3 mb-4">
          <div className="flex items-baseline justify-between gap-2 mb-2">
            <span className="text-xs font-semibold text-slate-200">Animatic</span>
            <span className="text-[10px] text-slate-500">
              {entries.length} shots
              {animatic?.summary?.total_duration_sec
                ? ` · ${animatic.summary.total_duration_sec}s`
                : ''}
              {animatic?.summary?.voice_line_count
                ? ` · ${animatic.summary.voice_line_count} voice lines`
                : ''}
            </span>
          </div>
          {videoUrl ? (
            <video
              src={videoUrl}
              controls
              className="w-full max-w-md rounded border border-slate-700"
            />
          ) : (
            <div className="text-[11px] text-slate-500">
              No animatic has been rendered for this package yet. Run the{' '}
              <code className="text-amber-300">animatic</code> command to cut the boards to time.
            </div>
          )}
        </div>
      )}
      <div className="space-y-2">
        {shots.map((shot: any) => (
          <button
            key={shot.shot_id}
            onClick={() => onSelect(shot.shot_id)}
            className={`w-full text-left flex gap-3 bg-[#111827] border rounded p-2 ${
              selected === shot.shot_id ? 'border-amber-500' : 'border-slate-800'
            }`}
          >
            <div className="w-24 shrink-0 space-y-1">
              {shot.board_image_path ? (
                <PackageImage
                  apiFetch={apiFetch}
                  projectId={projectId}
                  relPath={shot.board_image_path}
                  alt={shot.shot_id}
                  className="w-full rounded border border-slate-700"
                />
              ) : (
                <div className="w-full aspect-square bg-slate-900 rounded flex items-center justify-center text-[9px] text-slate-600">
                  no board
                </div>
              )}
              {showBlocking && shot.blocking_image_path && (
                <PackageImage
                  apiFetch={apiFetch}
                  projectId={projectId}
                  relPath={shot.blocking_image_path}
                  alt="blocking"
                  className="w-full rounded border border-slate-700"
                />
              )}
            </div>
            <div className="min-w-0 flex-1">
              <div className="flex items-center gap-2 flex-wrap">
                <span className="text-xs font-semibold text-slate-200">{shot.shot_id}</span>
                <span className={`text-[10px] px-1.5 py-0.5 rounded ${STATUS_TONE[shot.status] || 'bg-slate-700 text-slate-300'}`}>
                  {String(shot.status || 'NOT_STARTED').replace('_', ' ')}
                </span>
                <span className="text-[10px] text-slate-500">{shot.shot_size}</span>
                <span className="text-[10px] text-slate-500">{shot.duration_sec}s</span>
              </div>
              <div className="text-[11px] text-slate-400 mt-1">{shot.scene_heading}</div>
              <div className="text-[11px] text-slate-300 mt-0.5 line-clamp-2">{shot.description}</div>
              <div className="mt-1 flex gap-1">
                <button
                  onClick={(e) => {
                    e.stopPropagation();
                    onDecide('APPROVE', 'STORYBOARD', shot.shot_id);
                  }}
                  disabled={busy !== null}
                  className="text-[10px] px-2 py-0.5 rounded bg-emerald-800 text-emerald-100 disabled:opacity-50"
                >
                  Approve
                </button>
                <button
                  onClick={(e) => {
                    e.stopPropagation();
                    onDecide('REJECT', 'STORYBOARD', shot.shot_id);
                  }}
                  disabled={busy !== null}
                  className="text-[10px] px-2 py-0.5 rounded bg-red-900 text-red-200 disabled:opacity-50"
                >
                  Reject
                </button>
                <button
                  onClick={(e) => {
                    e.stopPropagation();
                    onSelect(shot.shot_id);
                  }}
                  className="text-[10px] px-2 py-0.5 rounded bg-slate-700 text-slate-200"
                >
                  Inspect prompt
                </button>
              </div>
            </div>
          </button>
        ))}
      </div>
    </div>
  );
}

function ContinuityStage({ pipeline }: { pipeline: any }) {
  const checks: any[] = pipeline?.continuity_checks || [];
  const tone: Record<string, string> = {
    PASS: 'bg-emerald-800 text-emerald-100',
    FAIL: 'bg-red-900 text-red-200',
    REVIEW: 'bg-amber-900 text-amber-100',
    NOT_CHECKED: 'bg-slate-700 text-slate-300',
  };
  return (
    <div>
      <h3 className="text-lg font-semibold text-amber-300 mb-2">Continuity</h3>
      <div className="text-xs text-slate-400 mb-2">
        Continuity status:{' '}
        <span className="text-slate-200">{pipeline?.continuity_status || 'NOT_RUN'}</span>
      </div>
      {checks.length === 0 ? (
        <p className="text-xs text-slate-500">
          No continuity report has been run for this package yet.
        </p>
      ) : (
        <div className="space-y-1">
          {checks.map((check: any) => (
            <div
              key={check.check_id}
              className="flex gap-2 items-start bg-[#111827] border border-slate-800 rounded p-2"
            >
              <span
                className={`text-[10px] px-1.5 py-0.5 rounded shrink-0 ${tone[check.status] || 'bg-slate-700 text-slate-300'}`}
              >
                {check.status}
              </span>
              <div className="min-w-0">
                <div className="text-[11px] text-slate-200">{check.check_id}</div>
                <div className="text-[11px] text-slate-400">{check.message}</div>
              </div>
            </div>
          ))}
        </div>
      )}
      <p className="text-xs text-slate-500 mt-3">
        Image-to-image identity is reported as NOT_CHECKED: there is no vision model in the local
        stack to judge it.
      </p>
    </div>
  );
}

function HandoffStage({ pipeline, projectId }: { pipeline: any; projectId: string }) {
  const link = pipeline?.link || {};
  return (
    <div>
      <h3 className="text-lg font-semibold text-amber-300 mb-2">Handoff</h3>
      <div className="text-xs text-slate-400 mb-3">
        The package the engine team receives, with the shot intent, the references and the provenance.
      </div>
      <div className="text-xs text-slate-400 space-y-1">
        <div>Script: {link.script_id || '-'} ({link.approval_status || '-'})</div>
        {pipeline?.handoff_paths?.json && (
          <div className="text-emerald-300">
            Package: <code>{pipeline.handoff_paths.json}</code>
            {pipeline?.handoff_paths?.markdown && (
              <>
                {' '}
                and <code>{pipeline.handoff_paths.markdown}</code>
              </>
            )}
          </div>
        )}
        <div>Generations: {pipeline?.generations?.total ?? 0}</div>
        <div>
          Art direction {pipeline?.generations?.art_direction ?? 0} &middot; storyboard{' '}
          {pipeline?.generations?.storyboard ?? 0} &middot; blocking {pipeline?.generations?.blocking ?? 0}
        </div>
        <div>Prompt overrides in this project: {(pipeline?.overrides || []).length}</div>
      </div>
    </div>
  );
}

/* --------------------------------------------------------------- inspector */

function PromptInspector({
  apiFetch,
  apiJson,
  projectId,
  targetId,
  kind,
  onSaved,
}: {
  apiFetch: (path: string, init?: RequestInit) => Promise<Response>;
  apiJson: (path: string) => Promise<any>;
  projectId: string;
  targetId: string;
  kind: string;
  onSaved: () => void;
}) {
  const [state, setState] = useState<any>(null);
  const [extra, setExtra] = useState('');
  const [replace, setReplace] = useState('');
  const [useReplace, setUseReplace] = useState(false);
  const [negativeExtra, setNegativeExtra] = useState('');
  const [excluded, setExcluded] = useState<string[]>([]);
  const [settings, setSettings] = useState<Record<string, string>>({});
  const [workflowId, setWorkflowId] = useState('');
  const [workflows, setWorkflows] = useState<any[]>([]);
  const [presets, setPresets] = useState<any[]>([]);
  const [status, setStatus] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [busy, setBusy] = useState(false);
  const [rendered, setRendered] = useState<string | null>(null);
  const [workflowText, setWorkflowText] = useState('');
  const [workflowReport, setWorkflowReport] = useState<any>(null);
  const [showWorkflowEditor, setShowWorkflowEditor] = useState(false);

  const load = useCallback(async () => {
    try {
      setError(null);
      // One missing endpoint must never blank the inspector. Each panel is
      // loaded on its own and reports its own failure.
      const settled = await Promise.allSettled([
        apiJson(`/api/production/${projectId}/prompts/${targetId}`),
        apiJson(`/api/production/${projectId}/workflows`),
        apiJson('/api/production/presets'),
      ]);
      const [promptResult, workflowResult, presetResult] = settled;
      if (promptResult.status === 'fulfilled') {
        setState(promptResult.value);
      } else {
        setError(`prompt -> ${promptResult.reason?.message || promptResult.reason}`);
      }
      if (workflowResult.status === 'fulfilled') {
        setWorkflows(workflowResult.value.workflows || []);
      }
      if (presetResult.status === 'fulfilled') {
        setPresets(presetResult.value.presets || []);
      }
      if (promptResult.status === 'fulfilled') {
        const override = promptResult.value.override || null;
        setExtra(override?.prompt_extra || '');
        setReplace(override?.prompt_replace || '');
        setUseReplace(Boolean(override?.prompt_replace));
        setNegativeExtra(override?.negative_extra || '');
        setExcluded(override?.exclude_modules || []);
        setWorkflowId(override?.workflow_id || '');
        const next: Record<string, string> = {};
        for (const [key, value] of Object.entries(override?.settings_override || {})) {
          next[key] = String(value);
        }
        setSettings(next);
      }
    } catch (e: any) {
      setError(e.message || String(e));
    }
  }, [projectId, targetId, apiJson]);

  useEffect(() => { load(); }, [load]);

  const save = async () => {
    setBusy(true);
    setError(null);
    setStatus(null);
    try {
      const body: any = {
        target_id: targetId,
        kind,
        prompt_extra: extra,
        prompt_replace: useReplace ? replace : null,
        negative_extra: negativeExtra,
        exclude_modules: excluded,
        settings_override: settings,
        workflow_id: workflowId || null,
        actor: 'frontend',
      };
      const response = await apiFetch(`/api/production/${projectId}/prompts/${targetId}`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(body),
      });
      if (!response.ok) {
        const text = await response.text();
        throw new Error(text || `save -> ${response.status}`);
      }
      setStatus('Saved. The next generation will use this.');
      await load();
      onSaved();
    } catch (e: any) {
      setError(e.message || String(e));
    } finally {
      setBusy(false);
    }
  };

  // A workflow the user built can be pasted in. It is validated against the
  // live server before it is stored, so a graph that would write the prompt
  // into the wrong node is refused.
  const attachWorkflow = async () => {
    setBusy(true);
    setError(null);
    setWorkflowReport(null);
    try {
      let workflow: any;
      try {
        workflow = JSON.parse(workflowText);
      } catch (parseError: any) {
        throw new Error(`That is not valid JSON: ${parseError.message}`);
      }
      const response = await apiFetch(`/api/production/${projectId}/workflow/import`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ workflow }),
      });
      const result = await response.json();
      if (!response.ok) throw new Error(result.detail || `import -> ${response.status}`);
      setWorkflowReport(result.report);
      if (result.stored) {
        setWorkflowId(result.workflow_id);
        setWorkflowText('');
        setShowWorkflowEditor(false);
        setStatus(`Workflow ${result.workflow_id} validated and attached.`);
        await load();
      }
    } catch (e: any) {
      setError(e.message || String(e));
    } finally {
      setBusy(false);
    }
  };

  const render = async () => {
    setBusy(true);
    setError(null);
    setStatus(null);
    setRendered(null);
    try {
      const response = await apiFetch(`/api/production/${projectId}/generate`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          target_id: targetId,
          kind,
          artifact_type: kind === 'ART_DIRECTION_CANDIDATE' ? 'ART_DIRECTION' : 'STORYBOARD',
        }),
      });
      if (!response.ok) {
        const text = await response.text();
        throw new Error(text || `generate -> ${response.status}`);
      }
      const result = await response.json();
      setRendered(result.image_path || '');
      setStatus(
        `Rendered in ${result.elapsed_sec ?? '?'} s. The image is a new revision; the previous one was kept.`
      );
      await load();
      onSaved();
    } catch (e: any) {
      setError(e.message || String(e));
    } finally {
      setBusy(false);
    }
  };

  const reset = async () => {
    setBusy(true);
    try {
      await apiFetch(`/api/production/${projectId}/prompts/${targetId}`, { method: 'DELETE' });
      setStatus('Override removed. The generated prompt is back.');
      await load();
      onSaved();
    } catch (e: any) {
      setError(e.message || String(e));
    } finally {
      setBusy(false);
    }
  };

  const modules: Record<string, string> = state?.modules || {};
  const moduleNames = Object.keys(modules);

  return (
    <div>
      <h3 className="text-sm font-semibold text-amber-300 mb-1">{targetId}</h3>
      <div className="text-[10px] text-slate-500 mb-2">{kind.replace('_', ' ').toLowerCase()}</div>
      {error && <div className="text-[11px] text-red-300 bg-red-900/30 rounded p-2 mb-2">{error}</div>}
      {status && <div className="text-[11px] text-emerald-300 bg-emerald-900/25 rounded p-2 mb-2">{status}</div>}

      <div className="text-[10px] uppercase tracking-wide text-slate-500 mb-1">
        Generated prompt (read only)
      </div>
      <div className="text-[11px] text-slate-400 bg-[#0b0f19] border border-slate-800 rounded p-2 mb-3 max-h-40 overflow-auto">
        {state?.generated_prompt || 'loading...'}
      </div>

      <div className="text-[10px] uppercase tracking-wide text-slate-500 mb-1">
        Modules you can drop
      </div>
      <div className="flex flex-wrap gap-1 mb-3">
        {moduleNames
          .filter((name) => (modules[name] || '').trim().length > 0)
          .map((name) => {
            const on = excluded.includes(name);
            return (
              <button
                key={name}
                onClick={() => setExcluded(on ? excluded.filter((n) => n !== name) : [...excluded, name])}
                className={`text-[10px] px-2 py-0.5 rounded border ${
                  on
                    ? 'bg-red-900/50 border-red-700 text-red-200 line-through'
                    : 'bg-slate-800 border-slate-700 text-slate-300'
                }`}
                title={`Drop the ${(MODULE_LABELS[name] || name).toLowerCase()} from the prompt`}
              >
                {MODULE_LABELS[name] || name}
              </button>
            );
          })}
      </div>

      <label className="block text-[10px] uppercase tracking-wide text-slate-500 mb-1">
        Your own text (added to the prompt)
      </label>
      <textarea
        value={extra}
        onChange={(e) => setExtra(e.target.value)}
        rows={4}
        placeholder="e.g. hold the camera lower, 1920s archive photograph, heavy grain"
        className="w-full text-[11px] bg-slate-800 rounded px-2 py-1.5 mb-1 font-mono"
      />

      <label className="flex items-center gap-2 text-[10px] text-slate-400 mb-1">
        <input type="checkbox" checked={useReplace} onChange={(e) => setUseReplace(e.target.checked)} />
        Replace the generated prompt entirely instead of adding to it
      </label>
      {useReplace && (
        <textarea
          value={replace}
          onChange={(e) => setReplace(e.target.value)}
          rows={3}
          placeholder="the whole prompt, in your own words"
          className="w-full text-[11px] bg-slate-800 rounded px-2 py-1.5 mb-1 font-mono"
        />
      )}

      <label className="block text-[10px] uppercase tracking-wide text-slate-500 mb-1">
        Your own negative prompt
      </label>
      <textarea
        value={negativeExtra}
        onChange={(e) => setNegativeExtra(e.target.value)}
        rows={2}
        placeholder="e.g. modern digital render, 3d render"
        className="w-full text-[11px] bg-slate-800 rounded px-2 py-1.5 mb-3 font-mono"
      />

      <div className="text-[10px] uppercase tracking-wide text-slate-500 mb-1">
        Generation preset
      </div>
      <select
        value={settings.preset || ''}
        onChange={(e) => {
          const next = { ...settings };
          if (!e.target.value) delete next.preset;
          else next.preset = e.target.value;
          setSettings(next);
        }}
        className="w-full bg-slate-800 rounded px-2 py-1 text-[11px] mb-1"
      >
        <option value="">keep the current settings</option>
        {presets.map((preset: any) => (
          <option key={preset.preset_id} value={preset.preset_id}>
            {preset.label} — {preset.measured}
          </option>
        ))}
      </select>
      {presets.length > 0 && (
        <div className="text-[10px] text-slate-500 mb-3">
          {presets.find((p: any) => p.preset_id === settings.preset)?.note || ''}
        </div>
      )}

      <div className="text-[10px] uppercase tracking-wide text-slate-500 mb-1">Generation settings</div>
      <div className="grid grid-cols-2 gap-1 mb-3">
        {['seed', 'steps', 'cfg', 'model', 'sampler', 'scheduler', 'width', 'height'].map((key) => (
          <label key={key} className="text-[10px] text-slate-500 flex items-center gap-1">
            <span className="w-16 shrink-0">{key}</span>
            <input
              value={settings[key] ?? ''}
              placeholder={state?.settings?.[key] !== undefined ? String(state.settings[key]) : ''}
              onChange={(e) => {
                const next = { ...settings };
                if (!e.target.value) delete next[key];
                else next[key] = e.target.value;
                setSettings(next);
              }}
              className="w-full bg-slate-800 rounded px-1 py-0.5 text-[11px] text-slate-200"
            />
          </label>
        ))}
      </div>

      <div className="text-[10px] uppercase tracking-wide text-slate-500 mb-1">Your ComfyUI workflow</div>
      <select
        value={workflowId}
        onChange={(e) => setWorkflowId(e.target.value)}
        className="w-full bg-slate-800 rounded px-2 py-1 text-[11px] mb-1"
      >
        <option value="">use the built-in workflow</option>
        {workflows.map((w: any) => (
          <option key={w.workflow_id} value={w.workflow_id}>{w.workflow_id}</option>
        ))}
      </select>
      <button
        onClick={() => setShowWorkflowEditor(!showWorkflowEditor)}
        className="text-[10px] px-2 py-0.5 rounded bg-slate-700 text-slate-200 mb-2"
      >
        {showWorkflowEditor ? 'Close the workflow editor' : 'Attach a workflow of your own'}
      </button>
      {showWorkflowEditor && (
        <div className="mb-3">
          <textarea
            value={workflowText}
            onChange={(e) => setWorkflowText(e.target.value)}
            rows={5}
            placeholder='Paste the workflow JSON exported from ComfyUI with File -> Export Workflow (API).'
            className="w-full text-[10px] bg-slate-800 rounded px-2 py-1 mb-1 font-mono"
          />
          <button
            onClick={attachWorkflow}
            disabled={busy || !workflowText.trim()}
            className="text-[10px] px-2 py-0.5 rounded bg-amber-600 text-black disabled:opacity-50"
          >
            Validate and attach
          </button>
          {workflowReport && (
            <div className="text-[10px] mt-1">
              {workflowReport.status === 'PASS' ? (
                <span className="text-emerald-300">
                  Every node class is accepted and the graph can take a prompt.
                </span>
              ) : (
                <span className="text-red-300">
                  Refused:{' '}
                  {[
                    ...(workflowReport.missing_nodes || []),
                    ...(workflowReport.missing_inputs || []),
                    ...(workflowReport.unknown_inputs || []),
                    ...(workflowReport.errors || []),
                  ]
                    .slice(0, 6)
                    .join(', ')}
                </span>
              )}
            </div>
          )}
        </div>
      )}

      <div className="flex gap-2 flex-wrap">
        <button
          onClick={render}
          disabled={busy}
          className="text-xs px-3 py-1 rounded bg-emerald-600 text-black disabled:opacity-50"
        >
          {busy ? 'Rendering...' : kind === 'ART_DIRECTION_CANDIDATE' ? 'Render this direction' : 'Render this shot'}
        </button>
        <button
          onClick={save}
          disabled={busy}
          className="text-xs px-3 py-1 rounded bg-amber-600 text-black disabled:opacity-50"
        >
          Save prompt
        </button>
        <button
          onClick={reset}
          disabled={busy}
          className="text-xs px-3 py-1 rounded bg-slate-700 text-slate-200 disabled:opacity-50"
        >
          Back to generated
        </button>
      </div>
      {rendered && (
        <div className="text-[10px] text-emerald-300 mt-2">
          New revision: <code>{rendered}</code>
        </div>
      )}

      {state?.changed && (
        <div className="mt-3 text-[10px] uppercase tracking-wide text-slate-500 mb-1">
          What will be sent
        </div>
      )}
      {state?.changed && (
        <div className="text-[11px] text-emerald-200 bg-emerald-950/30 border border-emerald-900 rounded p-2 max-h-40 overflow-auto font-mono">
          {state.effective_prompt}
        </div>
      )}
      {state?.applied_overrides?.length > 0 && (
        <div className="text-[10px] text-slate-500 mt-2">
          Applied: {state.applied_overrides.join(', ')}
        </div>
      )}
    </div>
  );
}
