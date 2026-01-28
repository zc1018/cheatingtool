import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { LLMConfig } from "@/components/config/LLMConfig";
import { STTConfig } from "@/components/config/STTConfig";

export function Settings() {
    return (
        <div className="space-y-6 max-w-3xl mx-auto pb-10">
            <div>
                <h3 className="text-lg font-medium">Settings</h3>
                <p className="text-sm text-muted-foreground">Manage your API keys and application preferences.</p>
            </div>
            <div className="grid gap-4">
                <Card>
                    <CardHeader>
                        <CardTitle>LLM Configuration</CardTitle>
                        <CardDescription>Configure your AI provider settings.</CardDescription>
                    </CardHeader>
                    <CardContent>
                        <LLMConfig />
                    </CardContent>
                </Card>
                <Card>
                    <CardHeader>
                        <CardTitle>Speech to Text</CardTitle>
                        <CardDescription>Configure transcription settings.</CardDescription>
                    </CardHeader>
                    <CardContent>
                        <STTConfig />
                    </CardContent>
                </Card>
            </div>
        </div>
    );
}
