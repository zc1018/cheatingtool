import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Copy } from "lucide-react";

interface SuggestionCardProps {
    suggestion?: string;
}

export function SuggestionCard({ suggestion }: SuggestionCardProps) {
    if (!suggestion) return null;

    const copyToClipboard = () => {
        navigator.clipboard.writeText(suggestion);
    };

    return (
        <Card className="bg-primary/5 border-primary/20">
            <CardHeader className="pb-2 flex flex-row items-center justify-between space-y-0">
                <CardTitle className="text-sm font-medium text-primary">Suggested Reply</CardTitle>
                <Button variant="ghost" size="icon" className="h-6 w-6" onClick={copyToClipboard}>
                    <Copy className="h-3 w-3" />
                </Button>
            </CardHeader>
            <CardContent>
                <p className="text-sm leading-relaxed">
                    {suggestion}
                </p>
            </CardContent>
        </Card>
    );
}
