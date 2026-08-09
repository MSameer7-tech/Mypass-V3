import React, { useEffect } from "react";
import { useAuthStore } from "../../../stores/auth/useAuthStore";
import { MOTION_TOKENS } from "../../../constants/motion";
import { motion, AnimatePresence } from "framer-motion";
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

  const renderContent = () => {
    if (sessionState === "BOOTING") {
      return (
        <motion.div key="booting" initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }} transition={{ duration: MOTION_TOKENS.duration.stateChange }} className="h-screen w-screen bg-[var(--background)] flex flex-col items-center justify-center gap-3">
          <Spinner size="lg" />
          <span className="text-xs font-semibold text-[var(--text-muted)] tracking-wide">Initializing Security Engine...</span>
        </motion.div>
      );
    }

    if (sessionState === "NO_VAULT") {
      return (
        <motion.div key="no_vault" initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }} transition={{ duration: MOTION_TOKENS.duration.stateChange }} className="h-full w-full">
          <CreateVaultScreen onCreateVault={createVault} />
        </motion.div>
      );
    }

    if (sessionState === "UNLOCKED") {
      return (
        <motion.div key="unlocked" initial={{ opacity: 0, filter: 'blur(2px)' }} animate={{ opacity: 1, filter: 'blur(0px)' }} exit={{ opacity: 0, filter: 'blur(2px)' }} transition={{ duration: 0.35, ease: "easeOut" }} className="h-full w-full">
          <WorkspaceLayout />
        </motion.div>
      );
    }

    return (
      <motion.div key="locked" initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }} transition={{ duration: MOTION_TOKENS.duration.stateChange }} className="h-full w-full">
        <UnlockScreen
          onUnlock={unlockVault}
          onBiometricUnlock={unlockVaultWithBiometrics}
          isUnlocking={sessionState === "UNLOCKING"}
          errorMessage={authError}
        />
      </motion.div>
    );
  };

  return (
    <AnimatePresence mode="wait">
      {renderContent()}
    </AnimatePresence>
  );
};
