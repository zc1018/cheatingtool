
import { useAnalysisStore } from "@/store/useAnalysisStore";
import { IntentDisplay } from "./IntentDisplay";
import { ThoughtsDisplay } from "./ThoughtsDisplay";
import { SuggestionCard } from "./SuggestionCard";

export function AnalysisCard() {
    const { currentAnalysis } = useAnalysisStore();

    if (!currentAnalysis) {
        return (
            <div className="h-full flex items-center justify-center text-muted-foreground text-sm">
                Waiting for analysis...
            </div>
        );
    }

    return (
        <div className="h-full flex flex-col gap-4">
            <IntentDisplay intent={currentAnalysis.intent} confidence={currentAnalysis.confidence} />
            <ThoughtsDisplay thoughts={currentAnalysis.thoughts} />
            <SuggestionCard suggestion={currentAnalysis.suggestion} />
        </div>
    );
}
