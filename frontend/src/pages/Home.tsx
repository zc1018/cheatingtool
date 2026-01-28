import { AudioVisualizer } from "@/components/audio/AudioVisualizer";
import { AudioControls } from "@/components/audio/AudioControls";
import { TranscriptionList } from "@/components/transcription/TranscriptionList";
import { AnalysisCard } from "@/components/analysis/AnalysisCard";
import { useWebSocket } from "@/hooks/useWebSocket";
import { useAudioStore } from "@/store/useAudioStore";

export function Home() {
    const { isRecording } = useAudioStore();
    // Connect WS when recording (mock URL for now)
    useWebSocket('ws://localhost:8000/ws/stream', isRecording);

    return (
        <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3 h-full">
            <div className="col-span-2 lg:col-span-2 flex flex-col gap-4 h-full">
                <div className="h-48 border rounded-lg flex flex-col items-center justify-center bg-card relative overflow-hidden">
                    <AudioVisualizer />
                    <div className="absolute bottom-4 right-4 z-10">
                        <AudioControls />
                    </div>
                </div>
                <div className="flex-1 border rounded-lg bg-background overflow-hidden relative">
                    <TranscriptionList />
                </div>
            </div>
            <div className="col-span-1 border rounded-lg p-4 bg-muted/20 h-full overflow-auto">
                <AnalysisCard />
            </div>
        </div>
    );
}
