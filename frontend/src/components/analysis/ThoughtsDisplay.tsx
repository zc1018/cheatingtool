import { cn } from "@/lib/utils";
import { useState } from "react";
import { ChevronDown, ChevronRight } from "lucide-react";

interface ThoughtsDisplayProps {
    thoughts?: string;
}

export function ThoughtsDisplay({ thoughts }: ThoughtsDisplayProps) {
    const [isExpanded, setIsExpanded] = useState(false);

    if (!thoughts) return null;

    return (
        <div className="border rounded-md p-2 bg-muted/50 mb-4">
            <button
                className="flex items-center gap-1 text-xs font-semibold text-muted-foreground w-full hover:text-foreground transition-colors"
                onClick={() => setIsExpanded(!isExpanded)}
            >
                {isExpanded ? <ChevronDown className="h-3 w-3" /> : <ChevronRight className="h-3 w-3" />}
                Thinking Process
            </button>

            <div className={cn(
                "grid transition-all duration-200 ease-in-out text-sm mt-1",
                isExpanded ? "grid-rows-[1fr] opacity-100" : "grid-rows-[0fr] opacity-0"
            )}>
                <div className="overflow-hidden">
                    <p className="whitespace-pre-wrap text-muted-foreground">
                        {thoughts}
                    </p>
                </div>
            </div>
        </div>
    );
}
