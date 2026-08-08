import React, { useEffect } from "react";
import { useAuthStore } from "../../../stores/auth/useAuthStore";
import { UnlockScreen } from "../screens/UnlockScreen";
import { CreateVaultScreen } from "../screens/CreateVaultScreen";
import { WorkspaceLayout } from "../../../components/workspace/WorkspaceLayout";
import { useSessionLifecycle } from "../hooks/useSessionLifecycle";
import { Spinner } from "../../../components/core/Spinner";

export const AuthenticationRouter: React.FC = () => {
  const sessionState = useAuthStore((s) => s.sessionState);
  const authError = useAuthStore((s) => s.authError);
  const checkVaultStatus = useAuthStore((s) => s.checkVaultStatus);
  const unlockVault = useAuthStore((s) => s.unlockVault);
  const createVault = useAuthStore((s) => s.createVault);

  useSessionLifecycle();

  useEffect(() => {
    checkVaultStatus();
  }, [checkVaultStatus]);

  const unlockVaultWithBiometrics = useAuthStore((s) => s.unlockVaultWithBiometrics);

  if (sessionState === "BOOTING") {
    return (
      <div className="h-screen w-screen bg-[var(--background)] flex flex-col items-center justify-center gap-3">
        <Spinner size="lg" />
        <span className="text-xs font-semibold text-[var(--text-muted)] tracking-wide">Initializing Security Engine...</span>
      </div>
    );
  }

  if (sessionState === "NO_VAULT") {
    return (
      <CreateVaultScreen
        onCreateVault={createVault}
      />
    );
  }

  if (sessionState === "UNLOCKED") {
    return <WorkspaceLayout />;
  }

  return (
    <UnlockScreen
      onUnlock={unlockVault}
      onBiometricUnlock={unlockVaultWithBiometrics}
      isUnlocking={sessionState === "UNLOCKING"}
      errorMessage={authError}
    />
  );
};
