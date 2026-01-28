import { useRef, useEffect } from "react";
import { useTranscriptionStore } from "@/store/useTranscriptionStore";
import { TranscriptionItem } from "./TranscriptionItem";
import { ScrollArea } from "@/components/ui/scroll-area";

export function TranscriptionList() {
    const { messages } = useTranscriptionStore();
    const bottomRef = useRef<HTMLDivElement>(null);

    useEffect(() => {
        // Auto scroll to bottom
        if (bottomRef.current) {
            bottomRef.current.scrollIntoView({ behavior: "smooth" });
        }
    }, [messages]);

    return (
        <ScrollArea className="h-full w-full p-4">
            {messages.length === 0 && (
                <div className="text-center text-muted-foreground py-10">
                    No transcription yet. Start recording...
                </div>
            )}
            {messages.map((msg) => (
                <TranscriptionItem key={msg.id} message={msg} />
            ))}
            <div ref={bottomRef} />
        </ScrollArea>
    );
}
