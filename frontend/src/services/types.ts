export interface TranscriptionMessage {
    id: string;
    role: 'user' | 'assistant' | 'other';
    text: string;
    timestamp: number;
    final: boolean;
}

export interface AnalysisMessage {
    type: 'analysis';
    intent?: string;
    thoughts?: string;
    suggestion?: string;
    confidence?: number;
}

export interface WebSocketMessage {
    type: 'transcription' | 'analysis' | 'pong';
    data: any;
}
