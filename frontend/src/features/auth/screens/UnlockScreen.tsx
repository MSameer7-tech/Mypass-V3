import React, { useState } from "react";
import { motion } from "framer-motion";
import { PasswordInput } from "../../../components/core/Input";
import { Button } from "../../../components/core/Button";
import { Badge } from "../../../components/core/Badge";
import { Shield, Fingerprint, Lock } from "lucide-react";
import { Icon } from "../../../components/core/Icon";

export interface UnlockScreenProps {
  onUnlock: (password: string) => Promise<boolean>;
  onBiometricUnlock?: () => Promise<boolean>;
  isUnlocking?: boolean;
  errorMessage?: string | null;
  onForgotPassword?: () => void;
}

export const UnlockScreen: React.FC<UnlockScreenProps> = ({
  onUnlock,
  onBiometricUnlock,
  isUnlocking = false,
  errorMessage,
  onForgotPassword,
}) => {
  const [password, setPassword] = useState("");
  const [shake, setShake] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!password || isUnlocking) return;

    const success = await onUnlock(password);
    if (!success) {
      setShake(true);
      setTimeout(() => setShake(false), 500);
    }
  };

  const handleTouchID = async (e: React.MouseEvent) => {
    e.preventDefault();
    if (isUnlocking || !onBiometricUnlock) return;
    
    const success = await onBiometricUnlock();
    if (!success) {
      setShake(true);
      setTimeout(() => setShake(false), 500);
    }
  };

  return (
    <div className="h-screen w-screen bg-[var(--background)] flex items-center justify-center p-4 select-none">
      <motion.div
        animate={shake ? { x: [-8, 8, -6, 6, -3, 3, 0] } : {}}
        transition={{ duration: 0.4 }}
        className="w-full max-w-sm bg-[var(--surface-panel)] border border-[var(--border-subtle)] rounded-2xl shadow-2xl p-8 flex flex-col items-center gap-6"
      >
        {/* Branding Header */}
        <div className="flex flex-col items-center gap-2 text-center">
          <div className="h-14 w-14 rounded-2xl bg-[var(--accent)] flex items-center justify-center shadow-lg shadow-blue-500/20 mb-1">
            <Icon icon={Shield} size="lg" tone="primary" />
          </div>
          <h1 className="text-xl font-bold text-[var(--text-primary)] tracking-tight">MyPass v3</h1>
          <p className="text-xs text-[var(--text-muted)]">Local-First Secure Password Vault</p>
        </div>

        {/* Unlock Form */}
        <form onSubmit={handleSubmit} className="w-full flex flex-col gap-4">
          <PasswordInput
            label="Master Password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            placeholder="Enter master password..."
            autoFocus
            leadingIcon={Lock}
            error={errorMessage || undefined}
          />

          <Button
            type="submit"
            variant="primary"
            size="lg"
            isLoading={isUnlocking}
            disabled={!password}
            className="w-full font-bold"
          >
            Unlock Vault
          </Button>
        </form>

        {/* Touch ID Alternative */}
        <div className="w-full flex flex-col items-center gap-3 pt-4 border-t border-[var(--border-subtle)]">
          <Button
            type="button"
            variant="secondary"
            size="sm"
            leadingIcon={Fingerprint}
            onClick={handleTouchID}
            isLoading={isUnlocking}
            className="w-full"
          >
            Unlock with Touch ID
          </Button>

          {onForgotPassword && (
            <button
              onClick={onForgotPassword}
              className="text-xs text-[var(--text-muted)] hover:text-[var(--text-primary)] hover:underline mt-1"
            >
              Forgot Master Password?
            </button>
          )}
        </div>

        <Badge variant="outline" className="text-[10px]">AES-256-GCM • Offline</Badge>
      </motion.div>
    </div>
  );
};
