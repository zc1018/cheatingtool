import { create } from 'zustand';
import { persist } from 'zustand/middleware';

export interface Prompt {
    id: string;
    title: string;
    content: string;
    tags: string[];
}

interface PromptState {
    prompts: Prompt[];
    addPrompt: (prompt: Omit<Prompt, 'id'>) => void;
    updatePrompt: (id: string, updates: Partial<Prompt>) => void;
    deletePrompt: (id: string) => void;
}

export const usePromptStore = create<PromptState>()(
    persist(
        (set) => ({
            prompts: [
                {
                    id: '1',
                    title: 'Default Assistant',
                    content: 'You are a helpful AI assistant.',
                    tags: ['general'],
                },
                {
                    id: '2',
                    title: 'Software Engineer',
                    content: 'You are an expert software engineer.',
                    tags: ['coding'],
                }
            ],
            addPrompt: (prompt) => set((state) => ({
                prompts: [...state.prompts, { ...prompt, id: Math.random().toString(36).substring(7) }]
            })),
            updatePrompt: (id, updates) => set((state) => ({
                prompts: state.prompts.map((p) => p.id === id ? { ...p, ...updates } : p)
            })),
            deletePrompt: (id) => set((state) => ({
                prompts: state.prompts.filter((p) => p.id !== id)
            })),
        }),
        {
            name: 'prompt-storage',
        }
    )
);
