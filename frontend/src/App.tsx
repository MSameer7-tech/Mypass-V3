import { AppProviders } from "./providers/AppProviders";
import { AuthenticationRouter } from "./features/auth/providers/AuthenticationRouter";

function App() {
  return (
    <AppProviders>
      <AuthenticationRouter />
    </AppProviders>
  );
}

export default App;
