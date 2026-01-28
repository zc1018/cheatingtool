import { create } from 'zustand';
import type { TranscriptionMessage } from '@/services/types';

interface TranscriptionState {
    messages: TranscriptionMessage[];
    addMessage: (message: TranscriptionMessage) => void;
    updateMessage: (id: string, message: Partial<TranscriptionMessage>) => void;
    clearMessages: () => void;
}

export const useTranscriptionStore = create<TranscriptionState>((set) => ({
    messages: [],
    addMessage: (message) => set((state) => {
        // If message with same ID exists, update it? Or append?
        // Usually streaming transcription sends updates for same ID until final.
        const existingIndex = state.messages.findIndex(m => m.id === message.id);
        if (existingIndex !== -1) {
            const newMessages = [...state.messages];
            newMessages[existingIndex] = { ...newMessages[existingIndex], ...message };
            return { messages: newMessages };
        }
        return { messages: [...state.messages, message] };
    }),
    updateMessage: (id, updates) => set((state) => ({
        messages: state.messages.map((msg) =>
            msg.id === id ? { ...msg, ...updates } : msg
        ),
    })),
    clearMessages: () => set({ messages: [] }),
}));
