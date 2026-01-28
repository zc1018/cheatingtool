import { useEffect, useRef } from 'react';
import WaveSurfer from 'wavesurfer.js';
import { useAudioStore } from '@/store/useAudioStore';

export function AudioVisualizer() {
    const containerRef = useRef<HTMLDivElement>(null);
    const wavesurferRef = useRef<WaveSurfer | null>(null);
    const { isRecording } = useAudioStore();

    useEffect(() => {
        if (!containerRef.current) return;

        wavesurferRef.current = WaveSurfer.create({
            container: containerRef.current,
            waveColor: 'rgb(200, 200, 200)',
            progressColor: 'rgb(100, 0, 100)',
            height: 100,
            cursorWidth: 0,
            barWidth: 2,
            barGap: 3,
        });

        return () => {
            wavesurferRef.current?.destroy();
        };
    }, []);

    useEffect(() => {
        // In a real app, this would receive stream data.
        // For now we might simulate or just listen to mic if implemented.
        // If we want real mic visualization, we need to attach the specific plugin or feed data.
        // WaveSurfer is better for playback. For real-time mic, we might need Microphone plugin.

        // For this prototype, I'll just leave the structure.

        if (isRecording) {
            // Start Microphone plugin if available
        } else {
            // Stop
        }

    }, [isRecording]);

    return (
        <div className="w-full h-full flex flex-col items-center justify-center bg-background rounded-lg p-4">
            <div ref={containerRef} className="w-full" />
            {!isRecording && <div className="text-muted-foreground text-sm mt-2">Ready to start</div>}
            {isRecording && <div className="text-red-500 text-sm mt-2 animate-pulse">Recording...</div>}
        </div>
    );
}
