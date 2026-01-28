import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";

// I didn't install slider. I'll use Input type="number" or install slider.
// I'll stick to Input for simplicity or verify installation.
import { useConfigStore } from "@/store/useConfigStore";

export function LLMConfig() {
    const { llm, setLLMConfig } = useConfigStore();

    return (
        <div className="space-y-4">
            <div className="grid gap-2">
                <Label>Provider</Label>
                <Select
                    value={llm.provider}
                    onValueChange={(value: any) => setLLMConfig({ provider: value })}
                >
                    <SelectTrigger>
                        <SelectValue placeholder="Select provider" />
                    </SelectTrigger>
                    <SelectContent>
                        <SelectItem value="openai">OpenAI</SelectItem>
                        <SelectItem value="anthropic">Anthropic</SelectItem>
                        <SelectItem value="ollama">Ollama</SelectItem>
                    </SelectContent>
                </Select>
            </div>

            <div className="grid gap-2">
                <Label>Model</Label>
                <Input
                    value={llm.model}
                    onChange={(e) => setLLMConfig({ model: e.target.value })}
                    placeholder="e.g. gpt-4"
                />
            </div>

            <div className="grid gap-2">
                <Label>API Key</Label>
                <Input
                    type="password"
                    value={llm.apiKey || ''}
                    onChange={(e) => setLLMConfig({ apiKey: e.target.value })}
                    placeholder="sk-..."
                />
            </div>

            <div className="grid gap-2">
                <Label>Temperature ({llm.temperature})</Label>
                <Input
                    type="number"
                    min={0} max={1} step={0.1}
                    value={llm.temperature}
                    onChange={(e) => setLLMConfig({ temperature: parseFloat(e.target.value) })}
                />
            </div>
        </div>
    );
}
