import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { useConfigStore } from "@/store/useConfigStore";

export function STTConfig() {
    const { stt, setSTTConfig } = useConfigStore();

    return (
        <div className="space-y-4">
            <div className="grid gap-2">
                <Label>Provider</Label>
                <Select
                    value={stt.provider}
                    onValueChange={(value: any) => setSTTConfig({ provider: value })}
                >
                    <SelectTrigger>
                        <SelectValue placeholder="Select provider" />
                    </SelectTrigger>
                    <SelectContent>
                        <SelectItem value="browser">Browser Native</SelectItem>
                        <SelectItem value="openai">OpenAI Whisper</SelectItem>
                        <SelectItem value="deepgram">Deepgram</SelectItem>
                    </SelectContent>
                </Select>
            </div>

            <div className="grid gap-2">
                <Label>Language</Label>
                <Input
                    value={stt.language}
                    onChange={(e) => setSTTConfig({ language: e.target.value })}
                    placeholder="e.g. zh-CN"
                />
            </div>
        </div>
    );
}
