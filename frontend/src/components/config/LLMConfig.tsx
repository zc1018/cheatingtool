import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { useState, useEffect } from "react";
import { useConfigStore } from "@/store/useConfigStore";

export function LLMConfig() {
    const { llm, setLLMConfig } = useConfigStore();
    const [models, setModels] = useState<string[]>([]);
    const [isCustom, setIsCustom] = useState(false);

    // 根据提供商更新可用模型
    useEffect(() => {
        setIsCustom(llm.provider === "custom");

        const modelMap: Record<string, string[]> = {
            openai: ["gpt-4o", "gpt-4o-mini", "gpt-4-turbo", "gpt-3.5-turbo"],
            anthropic: ["claude-3-5-sonnet-20241022", "claude-3-opus-20240229", "claude-3-sonnet-20240229", "claude-3-haiku-20240307"],
            ollama: ["llama2", "llama3", "mistral", "qwen", "gemma"],
            kimi: ["moonshot-v1-8k", "moonshot-v1-32k", "moonshot-v1-128k"],
            glm: ["glm-4", "glm-4-0520", "glm-4-air", "glm-4-flash", "glm-3-turbo"],
            custom: [],  // 用户自定义
        };

        setModels(modelMap[llm.provider] || []);

        // 如果不是自定义提供商，自动设置默认模型
        if (llm.provider !== "custom" && !models.includes(llm.model)) {
            const defaultModel = modelMap[llm.provider]?.[0];
            if (defaultModel) {
                setLLMConfig({ model: defaultModel });
            }
        }
    }, [llm.provider]);

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
                        <SelectItem value="openai">🤖 OpenAI</SelectItem>
                        <SelectItem value="anthropic">🧠 Anthropic</SelectItem>
                        <SelectItem value="ollama">🦙 Ollama (Local)</SelectItem>
                        <SelectItem value="kimi">🌙 Kimi (月之暗面)</SelectItem>
                        <SelectItem value="glm">🔮 GLM (智谱AI)</SelectItem>
                        <SelectItem value="custom">⚡ Custom API</SelectItem>
                    </SelectContent>
                </Select>
            </div>

            <div className="grid gap-2">
                <Label>Model</Label>
                {isCustom ? (
                    <Input
                        value={llm.model}
                        onChange={(e) => setLLMConfig({ model: e.target.value })}
                        placeholder="Enter custom model name"
                    />
                ) : (
                    <Select value={llm.model} onValueChange={(value: any) => setLLMConfig({ model: value })}>
                        <SelectTrigger>
                            <SelectValue placeholder="Select model" />
                        </SelectTrigger>
                        <SelectContent>
                            {models.map((model) => (
                                <SelectItem key={model} value={model}>
                                    {model}
                                </SelectItem>
                            ))}
                        </SelectContent>
                    </Select>
                )}
            </div>

            {isCustom && (
                <div className="grid gap-2">
                    <Label>Base URL</Label>
                    <Input
                        value={llm.baseUrl || ''}
                        onChange={(e) => setLLMConfig({ baseUrl: e.target.value })}
                        placeholder="https://api.example.com/v1"
                    />
                    <p className="text-xs text-muted-foreground">
                        Custom API endpoint URL
                    </p>
                </div>
            )}

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

            <div className="grid gap-2">
                <Label>Max Tokens</Label>
                <Input
                    type="number"
                    min={1} max={32000} step={100}
                    value={llm.maxTokens || 2000}
                    onChange={(e) => setLLMConfig({ maxTokens: parseInt(e.target.value) })}
                />
            </div>
        </div>
    );
}
