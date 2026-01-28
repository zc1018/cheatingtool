import { useState, useEffect } from "react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Textarea } from "@/components/ui/textarea";
import { Label } from "@/components/ui/label";
import type { Prompt } from "@/store/usePromptStore";

interface PromptEditorProps {
    initialPrompt?: Prompt;
    onSave: (prompt: Omit<Prompt, 'id'>) => void;
    onCancel: () => void;
}

export function PromptEditor({ initialPrompt, onSave, onCancel }: PromptEditorProps) {
    const [title, setTitle] = useState(initialPrompt?.title || "");
    const [content, setContent] = useState(initialPrompt?.content || "");
    const [tags, setTags] = useState(initialPrompt?.tags.join(", ") || "");

    useEffect(() => {
        setTitle(initialPrompt?.title || "");
        setContent(initialPrompt?.content || "");
        setTags(initialPrompt?.tags.join(", ") || "");
    }, [initialPrompt]);

    const handleSubmit = (e: React.FormEvent) => {
        e.preventDefault();
        onSave({
            title,
            content,
            tags: tags.split(",").map(t => t.trim()).filter(Boolean),
        });
    };

    return (
        <form onSubmit={handleSubmit} className="space-y-4">
            <div className="space-y-2">
                <Label htmlFor="title">Title</Label>
                <Input
                    id="title"
                    value={title}
                    onChange={(e) => setTitle(e.target.value)}
                    placeholder="Prompt Title"
                    required
                />
            </div>

            <div className="space-y-2">
                <Label htmlFor="content">Content</Label>
                <Textarea
                    id="content"
                    value={content}
                    onChange={(e) => setContent(e.target.value)}
                    placeholder="You are a helpful assistant..."
                    className="min-h-[200px]"
                    required
                />
            </div>

            <div className="space-y-2">
                <Label htmlFor="tags">Tags (comma separated)</Label>
                <Input
                    id="tags"
                    value={tags}
                    onChange={(e) => setTags(e.target.value)}
                    placeholder="coding, assistant, general"
                />
            </div>

            <div className="flex justify-end gap-2">
                <Button type="button" variant="outline" onClick={onCancel}>Cancel</Button>
                <Button type="submit">Save</Button>
            </div>
        </form>
    );
}
