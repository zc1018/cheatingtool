import { Home, Settings, FileText, Mic } from "lucide-react";
import { cn } from "@/lib/utils";
import { Button } from "@/components/ui/button";
import { useAppStore } from "@/store/useAppStore";

export function Sidebar() {
    const { currentView, setView } = useAppStore();

    const navItems = [
        { id: 'home', label: 'Home', icon: Home, view: 'home' as const },
        { id: 'prompts', label: 'Prompts', icon: FileText, view: 'prompts' as const },
        { id: 'settings', label: 'Settings', icon: Settings, view: 'settings' as const },
    ];

    return (
        <aside className="w-64 border-r bg-muted/40 h-screen flex-col hidden md:flex">
            <div className="p-4 border-b flex items-center gap-2 h-14">
                <Mic className="h-6 w-6 text-primary" />
                <span className="font-bold">Cheating Tool</span>
            </div>
            <nav className="flex-1 p-4 space-y-2">
                {navItems.map((item) => (
                    <Button
                        key={item.id}
                        variant={currentView === item.view ? "secondary" : "ghost"}
                        className={cn(
                            "w-full justify-start gap-2",
                            currentView === item.view && "font-semibold"
                        )}
                        onClick={() => setView(item.view)}
                    >
                        <item.icon className="h-4 w-4" />
                        {item.label}
                    </Button>
                ))}
            </nav>
            <div className="p-4 border-t text-xs text-muted-foreground text-center">
                v0.1.0-alpha
            </div>
        </aside>
    );
}
