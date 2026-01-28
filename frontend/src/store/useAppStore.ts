import { create } from 'zustand';

interface AppState {
    currentView: 'home' | 'settings' | 'prompts';
    setView: (view: 'home' | 'settings' | 'prompts') => void;
    isSidebarOpen: boolean;
    toggleSidebar: () => void;
}

export const useAppStore = create<AppState>((set) => ({
    currentView: 'home',
    setView: (view) => set({ currentView: view }),
    isSidebarOpen: true,
    toggleSidebar: () => set((state) => ({ isSidebarOpen: !state.isSidebarOpen })),
}));
