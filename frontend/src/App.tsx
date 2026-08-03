import { AppProviders } from "./providers/AppProviders";
import { WorkspaceLayout } from "./components/workspace/WorkspaceLayout";

function App() {
  return (
    <AppProviders>
      <WorkspaceLayout />
    </AppProviders>
  );
}

export default App;
