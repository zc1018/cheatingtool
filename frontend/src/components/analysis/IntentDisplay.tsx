import { Badge } from "@/components/ui/badge";

interface IntentDisplayProps {
    intent?: string;
    confidence?: number;
}

export function IntentDisplay({ intent, confidence }: IntentDisplayProps) {
    if (!intent) return null;

    return (
        <div className="flex items-center gap-2 mb-2">
            <span className="text-sm font-medium text-muted-foreground">Intent:</span>
            <Badge variant="outline" className="text-primary border-primary">
                {intent}
            </Badge>
            {confidence && (
                <span className="text-xs text-muted-foreground">
                    ({Math.round(confidence * 100)}%)
                </span>
            )}
        </div>
    );
}
