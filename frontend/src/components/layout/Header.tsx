import { Wifi, WifiOff } from "lucide-react";
import { Button } from "@/components/ui/button";
import { useWebSocket } from "@/hooks/useWebSocket";

export function Header() {
    // 始终保持 WebSocket 连接以显示状态
    const { isConnected } = useWebSocket('ws://localhost:8000/ws/stream', true);

    return (
        <header className="h-14 border-b bg-background/95 backdrop-blur supports-[backdrop-filter]:bg-background/60 flex items-center justify-between px-4 sticky top-0 z-50">
            <div className="flex items-center gap-2 font-semibold">
                <span className="text-primary text-lg">AI Voice Assistant</span>
            </div>

            <div className="flex items-center gap-4">
                <div className="flex items-center gap-2 text-sm text-muted-foreground">
                    {isConnected ? (
                        <>
                            <Wifi className="h-4 w-4 text-green-500" />
                            <span className="text-green-500">Connected</span>
                        </>
                    ) : (
                        <>
                            <WifiOff className="h-4 w-4 text-destructive" />
                            <span>Disconnected</span>
                        </>
                    )}
                </div>
                <Button variant="ghost" size="icon" aria-label="Settings">
                    {/* Additional actions if needed */}
                </Button>
            </div>
        </header>
    );
}
