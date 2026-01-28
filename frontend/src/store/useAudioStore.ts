import { create } from 'zustand';

interface AudioState {
    isRecording: boolean;
    setRecording: (recording: boolean) => void;
    toggleRecording: () => void;
}

export const useAudioStore = create<AudioState>((set) => ({
    isRecording: false,
    setRecording: (recording) => set({ isRecording: recording }),
    toggleRecording: () => set((state) => ({ isRecording: !state.isRecording })),
}));
