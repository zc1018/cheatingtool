import { create } from 'zustand';
import { persist } from 'zustand/middleware';

interface LLMConfig {
    provider: 'openai' | 'anthropic' | 'ollama';
    apiKey?: string;
    model: string;
    temperature: number;
    baseUrl?: string;
}

interface STTConfig {
    provider: 'openai' | 'deepgram' | 'browser';
    language: string;
}

interface ConfigState {
    llm: LLMConfig;
    stt: STTConfig;
    setLLMConfig: (config: Partial<LLMConfig>) => void;
    setSTTConfig: (config: Partial<STTConfig>) => void;
}

export const useConfigStore = create<ConfigState>()(
    persist(
        (set) => ({
            llm: {
                provider: 'openai',
                model: 'gpt-3.5-turbo',
                temperature: 0.7,
            },
            stt: {
                provider: 'browser',
                language: 'zh-CN',
            },
            setLLMConfig: (updates) =>
                set((state) => ({ llm: { ...state.llm, ...updates } })),
            setSTTConfig: (updates) =>
                set((state) => ({ stt: { ...state.stt, ...updates } })),
        }),
        {
            name: 'app-config',
        }
    )
);
