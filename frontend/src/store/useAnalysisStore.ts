import { create } from 'zustand';
import type { AnalysisMessage } from '@/services/types';

interface AnalysisState {
    currentAnalysis: AnalysisMessage | null;
    setAnalysis: (analysis: AnalysisMessage) => void;
    clearAnalysis: () => void;
}

export const useAnalysisStore = create<AnalysisState>((set) => ({
    currentAnalysis: null,
    setAnalysis: (analysis) => set({ currentAnalysis: analysis }),
    clearAnalysis: () => set({ currentAnalysis: null }),
}));
