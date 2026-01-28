import { Mic, Square } from "lucide-react";
import { Button } from "@/components/ui/button";
import { useAudioStore } from "@/store/useAudioStore";

export function AudioControls() {
    const { isRecording, toggleRecording } = useAudioStore();

    return (
        <div className="flex items-center gap-4">
            <Button
                variant={isRecording ? "destructive" : "default"}
                size="lg"
                className="rounded-full w-16 h-16"
                onClick={toggleRecording}
            >
                {isRecording ? <Square className="h-6 w-6" /> : <Mic className="h-6 w-6" />}
            </Button>
        </div>
    );
}
