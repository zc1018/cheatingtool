import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { LLMConfig } from "@/components/config/LLMConfig";
import { STTConfig } from "@/components/config/STTConfig";
import { Badge } from "@/components/ui/badge";

export function Settings() {
    return (
        <div className="space-y-6 max-w-4xl mx-auto pb-10">
            <div className="flex items-center justify-between">
                <div>
                    <h2 className="text-2xl font-bold tracking-tight">Settings</h2>
                    <p className="text-sm text-muted-foreground mt-1">
                        Configure your API keys, providers, and application preferences.
                    </p>
                </div>
                <Badge variant="outline" className="text-xs">Configuration</Badge>
            </div>

            <div className="grid gap-6">
                <Card className="border-primary/20">
                    <CardHeader>
                        <CardTitle className="flex items-center gap-2">
                            <span>🤖</span>
                            LLM Configuration
                        </CardTitle>
                        <CardDescription>
                            Configure your AI provider (OpenAI, Anthropic, or Ollama) for conversation analysis.
                        </CardDescription>
                    </CardHeader>
                    <CardContent>
                        <LLMConfig />
                    </CardContent>
                </Card>

                <Card className="border-primary/20">
                    <CardHeader>
                        <CardTitle className="flex items-center gap-2">
                            <span>🎤</span>
                            Speech to Text
                        </CardTitle>
                        <CardDescription>
                            Configure transcription provider (ElevenLabs or Qwen-Audio) and language settings.
                        </CardDescription>
                    </CardHeader>
                    <CardContent>
                        <STTConfig />
                    </CardContent>
                </Card>
            </div>
        </div>
    );
}
