import type { TranscriptionMessage } from "@/services/types";
import { cn } from "@/lib/utils";
import { Avatar, AvatarFallback } from "@/components/ui/avatar";

interface TranscriptionItemProps {
    message: TranscriptionMessage;
}

export function TranscriptionItem({ message }: TranscriptionItemProps) {
    const isUser = message.role === 'user';

    return (
        <div className={cn("flex gap-3 mb-4", isUser ? "flex-row-reverse" : "flex-row")}>
            <Avatar className="h-8 w-8">
                <AvatarFallback>{isUser ? 'U' : 'AI'}</AvatarFallback>
            </Avatar>
            <div className={cn(
                "max-w-[80%] rounded-lg p-3 text-sm",
                isUser
                    ? "bg-primary text-primary-foreground"
                    : "bg-muted text-foreground",
                !message.final && "opacity-70 animate-pulse"
            )}>
                <p>{message.text}</p>
                <div className="text-xs opacity-50 mt-1 flex justify-between">
                    <span>{new Date(message.timestamp).toLocaleTimeString()}</span>
                    {!message.final && <span>...</span>}
                </div>
            </div>
        </div>
    );
}
