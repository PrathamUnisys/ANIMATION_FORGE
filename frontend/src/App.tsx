import React, { useEffect, useState } from 'react';
import { useForgeStore } from './store/useForgeStore';

type Dashboard = {
  projects: any[]; pending_approvals: any[]; recent_approvals: any[];
  recent_assets: any[]; toolchains: any[]; integrations: any[];
  creative_decisions: any[]; qc_reports: any[];
};

const NAV = ['dashboard','projects','approvals','assets','toolchains','integrations','qc'] as const;

export default function App() {
  const { activeNav, setActiveNav, activeProjectId, operatingMode } = useForgeStore();
  const [data, setData] = useState<Dashboard | null>(null);
  const [health, setHealth] = useState<any>(null);
  const [error, setError] = useState<string | null>(null);

  async function load() {
    try {
      setError(null);
      const [h, d] = await Promise.all([
        fetch('/api/health').then(r => { if(!r.ok) throw new Error('health '+r.status); return r.json(); }),
        fetch('/api/dashboard').then(r => { if(!r.ok) throw new Error('dashboard '+r.status); return r.json(); }),
      ]);
      setHealth(h); setData(d);
    } catch (e: any) { setError(e.message || String(e)); }
  }
  useEffect(() => { load(); }, []);

  const listFor = (nav: string) => {
    if (!data) return [];
    const map: Record<string, any[]> = {
      dashboard: [], projects: data.projects, approvals: data.pending_approvals,
      assets: data.recent_assets, toolchains: data.toolchains,
      integrations: data.integrations, qc: data.qc_reports,
    };
    return map[nav] || [];
  };
  const items = listFor(activeNav);

  return (
    <div className="min-h-screen bg-[#0B0F19] text-slate-100 flex">
      <aside className="w-64 bg-[#111827] border-r border-slate-800 p-4 flex flex-col">
        <h1 className="text-lg font-bold text-amber-400 tracking-wide">ANIMATION FORGE</h1>
        <p className="text-xs text-slate-400 mb-1">Project: {activeProjectId}</p>
        <p className="text-xs text-slate-500 mb-4">{operatingMode}</p>
        <nav className="flex flex-col gap-1">
          {NAV.map(n => (
            <button key={n} onClick={() => setActiveNav(n)}
              className={`text-left px-3 py-2 rounded text-sm ${activeNav===n?'bg-amber-500/20 text-amber-300':'text-slate-300 hover:bg-slate-800'}`}>
              {n.toUpperCase()}
            </button>
          ))}
        </nav>
        <div className="mt-auto pt-4 text-xs text-slate-500">
          {health ? <>API: <span className={health.status==='healthy'?'text-green-400':'text-red-400'}>{health.status}</span> · {health.architecture_version} · DB {health.database_integrity?.table_count} tbl</> : 'API: …'}
        </div>
      </aside>
      <main className="flex-1 p-6 overflow-auto">
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-xl font-semibold text-amber-400 uppercase">{activeNav}</h2>
          <button onClick={load} className="text-xs px-3 py-1 rounded bg-slate-800 hover:bg-slate-700">Refresh</button>
        </div>
        {error && <div className="mb-4 p-3 rounded bg-red-900/40 text-red-200 text-sm">Error loading API: {error} (is backend running on 127.0.0.1:8765?)</div>}
        {activeNav === 'dashboard' && data && (
          <div className="grid grid-cols-2 lg:grid-cols-4 gap-3">
            {([['Projects',data.projects.length],['Pending Approvals',data.pending_approvals.length],['Assets',data.recent_assets.length],['Toolchains',data.toolchains.length],['Integrations',data.integrations.length],['QC Reports',data.qc_reports.length],['Decisions',data.creative_decisions.length],['Recent Approvals',data.recent_approvals.length]] as const).map(([k,v])=>(
              <div key={k} className="bg-[#111827] border border-slate-800 rounded p-4"><div className="text-xs text-slate-400">{k}</div><div className="text-2xl font-bold text-amber-300">{v}</div></div>
            ))}
          </div>
        )}
        {activeNav !== 'dashboard' && (
          <div className="bg-[#111827] border border-slate-800 rounded">
            {items.length === 0 ? <div className="p-4 text-slate-400 text-sm">No records. (Backend API is connected; data is empty.)</div> :
              <pre className="p-4 text-xs overflow-auto max-h-[70vh] text-slate-300">{JSON.stringify(items, null, 2)}</pre>}
          </div>
        )}
      </main>
    </div>
  );
}
