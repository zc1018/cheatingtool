import { useState } from "react";
import { Button } from "@/components/ui/button";
import { Plus } from "lucide-react";
import { PromptList } from "@/components/prompts/PromptList";
import { PromptEditor } from "@/components/prompts/PromptEditor";
import { usePromptStore, type Prompt } from "@/store/usePromptStore";
import { Sheet, SheetContent, SheetHeader, SheetTitle } from "@/components/ui/sheet";

export function Prompts() {
    const [isSheetOpen, setIsSheetOpen] = useState(false);
    const [editingPrompt, setEditingPrompt] = useState<Prompt | undefined>(undefined);
    const { addPrompt, updatePrompt } = usePromptStore();

    const handleEdit = (prompt: Prompt) => {
        setEditingPrompt(prompt);
        setIsSheetOpen(true);
    };

    const handleNew = () => {
        setEditingPrompt(undefined);
        setIsSheetOpen(true);
    };

    const handleSave = (data: Omit<Prompt, 'id'>) => {
        if (editingPrompt) {
            updatePrompt(editingPrompt.id, data);
        } else {
            addPrompt(data);
        }
        setIsSheetOpen(false);
    };

    return (
        <div className="space-y-6 pb-10">
            <div className="flex items-center justify-between">
                <h3 className="text-lg font-medium">Prompts Library</h3>
                <Button size="sm" className="gap-2" onClick={handleNew}>
                    <Plus className="h-4 w-4" />
                    New Prompt
                </Button>
            </div>

            <PromptList onEdit={handleEdit} />

            <Sheet open={isSheetOpen} onOpenChange={setIsSheetOpen}>
                <SheetContent className="sm:max-w-xl">
                    <SheetHeader>
                        <SheetTitle>{editingPrompt ? 'Edit Prompt' : 'New Prompt'}</SheetTitle>
                    </SheetHeader>
                    <div className="mt-6">
                        <PromptEditor
                            initialPrompt={editingPrompt}
                            onSave={handleSave}
                            onCancel={() => setIsSheetOpen(false)}
                        />
                    </div>
                </SheetContent>
            </Sheet>
        </div>
    );
}
