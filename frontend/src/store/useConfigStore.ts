import { create } from 'zustand';
import { persist } from 'zustand/middleware';

interface LLMConfig {
    provider: 'openai' | 'anthropic' | 'ollama' | 'kimi' | 'glm' | 'custom';
    apiKey?: string;
    model: string;
    temperature: number;
    baseUrl?: string;
    maxTokens?: number;
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
                model: 'gpt-4o',
                temperature: 0.7,
                maxTokens: 2000,
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
