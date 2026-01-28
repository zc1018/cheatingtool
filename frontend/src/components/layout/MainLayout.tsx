import type { ReactNode } from "react";
import { Header } from "./Header";
import { Sidebar } from "./Sidebar";
// Actually I didn't install sonner, so I will omit toaster for now or use shadcn's toaster if I added it. 
// I didn't add toast.

interface MainLayoutProps {
    children: ReactNode;
}

export function MainLayout({ children }: MainLayoutProps) {
    return (
        <div className="flex h-screen w-full bg-background overflow-hidden text-foreground">
            <Sidebar />
            <div className="flex flex-col flex-1 h-full overflow-hidden">
                <Header />
                <main className="flex-1 overflow-auto p-4 md:p-6 lg:p-8">
                    {children}
                </main>
            </div>
        </div>
    );
}
