import { create } from 'zustand';

export type OperatingMode =
  | 'PRODUCTION_MODE'
  | 'CREATIVE_MODE'
  | 'SCRIPTWRITING_MODE'
  | 'REVIEW_MODE'
  | 'TOOL_RND_MODE'
  | 'EXPERIMENT_MODE'
  | 'ARCHITECTURE_MODE'
  | 'MAINTENANCE_MODE';

interface ForgeState {
  activeNav: string;
  activeProjectId: string;
  operatingMode: OperatingMode;
  setActiveNav: (nav: string) => void;
  setActiveProjectId: (id: string) => void;
  setOperatingMode: (mode: OperatingMode) => void;
}

export const useForgeStore = create<ForgeState>((set) => ({
  activeNav: 'dashboard',
  activeProjectId: 'PROJECT_001',
  operatingMode: 'PRODUCTION_MODE',
  setActiveNav: (activeNav) => set({ activeNav }),
  setActiveProjectId: (activeProjectId) => set({ activeProjectId }),
  setOperatingMode: (operatingMode) => set({ operatingMode }),
}));
