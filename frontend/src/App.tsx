import { AppProviders } from "./providers/AppProviders";
import { AuthenticationRouter } from "./features/auth/providers/AuthenticationRouter";
import { MotionConfig } from "framer-motion";

function App() {
  return (
    <MotionConfig reducedMotion="user">
      <AppProviders>
        <AuthenticationRouter />
      </AppProviders>
    </MotionConfig>
  );
}

export default App;
