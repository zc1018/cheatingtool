import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Pencil, Trash2 } from "lucide-react";
import { usePromptStore, type Prompt } from "@/store/usePromptStore";

interface PromptListProps {
    onEdit: (prompt: Prompt) => void;
}

export function PromptList({ onEdit }: PromptListProps) {
    const { prompts, deletePrompt } = usePromptStore();

    return (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {prompts.map((prompt) => (
                <Card key={prompt.id} className="relative group">
                    <CardHeader className="pb-2">
                        <CardTitle className="text-lg flex justify-between items-start">
                            {prompt.title}
                        </CardTitle>
                    </CardHeader>
                    <CardContent>
                        <p className="text-sm text-muted-foreground line-clamp-3 mb-4">
                            {prompt.content}
                        </p>
                        <div className="flex flex-wrap gap-1 mb-4">
                            {prompt.tags.map(tag => (
                                <Badge key={tag} variant="secondary" className="text-xs">
                                    {tag}
                                </Badge>
                            ))}
                        </div>
                        <div className="flex justify-end gap-2 opacity-0 group-hover:opacity-100 transition-opacity">
                            <Button variant="ghost" size="icon" onClick={() => onEdit(prompt)}>
                                <Pencil className="h-4 w-4" />
                            </Button>
                            <Button variant="ghost" size="icon" onClick={() => deletePrompt(prompt.id)} className="text-destructive hover:text-destructive">
                                <Trash2 className="h-4 w-4" />
                            </Button>
                        </div>
                    </CardContent>
                </Card>
            ))}
        </div>
    );
}
