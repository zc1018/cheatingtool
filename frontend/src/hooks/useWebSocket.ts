import { useEffect, useRef, useCallback } from 'react';
import { useTranscriptionStore } from '@/store/useTranscriptionStore';
import { useAnalysisStore } from '@/store/useAnalysisStore';

export function useWebSocket(url: string, enabled: boolean) {
    const wsRef = useRef<WebSocket | null>(null);
    const reconnectTimeoutRef = useRef<NodeJS.Timeout>(null);
    const { addMessage } = useTranscriptionStore();
    const { setAnalysis } = useAnalysisStore();

    const connect = useCallback(() => {
        if (!enabled) return;

        // Clean up existing
        if (wsRef.current) {
            wsRef.current.close();
        }

        try {
            const ws = new WebSocket(url);
            wsRef.current = ws;

            ws.onopen = () => {
                console.log('WebSocket connected');
            };

            ws.onmessage = (event) => {
                try {
                    const message = JSON.parse(event.data);
                    if (message.type === 'transcription') {
                        addMessage(message.data);
                    } else if (message.type === 'analysis') {
                        setAnalysis(message.data);
                    }
                } catch (error) {
                    console.error('Failed to parse websocket message:', error);
                }
            };

            ws.onclose = () => {
                console.log('WebSocket closed, reconnecting in 3s...');
                wsRef.current = null;
                if (enabled) {
                    reconnectTimeoutRef.current = setTimeout(connect, 3000);
                }
            };

            ws.onerror = (error) => {
                console.error('WebSocket error:', error);
                ws.close();
            };

        } catch (error) {
            console.error('Failed to create WebSocket:', error);
            reconnectTimeoutRef.current = setTimeout(connect, 3000);
        }
    }, [url, enabled, addMessage]);

    useEffect(() => {
        if (enabled) {
            connect();
        } else {
            wsRef.current?.close();
            if (reconnectTimeoutRef.current) clearTimeout(reconnectTimeoutRef.current);
        }

        return () => {
            wsRef.current?.close();
            if (reconnectTimeoutRef.current) clearTimeout(reconnectTimeoutRef.current);
        };
    }, [connect, enabled]);

    return { isConnected: wsRef.current?.readyState === WebSocket.OPEN };
}
