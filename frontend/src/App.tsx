import { MainLayout } from "./components/layout/MainLayout";
import { Home } from "./pages/Home";
import { Settings } from "./pages/Settings";
import { Prompts } from "./pages/Prompts";
import { useAppStore } from "./store/useAppStore";

function App() {
  const { currentView } = useAppStore();

  return (
    <MainLayout>
      {currentView === 'home' && <Home />}
      {currentView === 'settings' && <Settings />}
      {currentView === 'prompts' && <Prompts />}
    </MainLayout>
  )
}

export default App;
