import React, { useState } from "react";
import { PasswordInput } from "../../../components/core/Input";
import { Button } from "../../../components/core/Button";
import { PasswordStrength } from "../../../components/domain/PasswordStrength";
import { FieldGroup } from "../../../components/layout/FieldGroup";
import { Shield, Check, Lock } from "lucide-react";
import { Icon } from "../../../components/core/Icon";

export interface CreateVaultScreenProps {
  onCreateVault: (password: string) => Promise<boolean>;
  isCreating?: boolean;
}

export const CreateVaultScreen: React.FC<CreateVaultScreenProps> = ({
  onCreateVault,
  isCreating = false,
}) => {
  const [password, setPassword] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [localLoading, setLocalLoading] = useState(false);

  const calculateScore = (pwd: string) => {
    if (!pwd) return 0;
    if (pwd.length < 8) return 1;
    if (pwd.length < 12) return 2;
    if (/[A-Z]/.test(pwd) && /[0-9]/.test(pwd) && /[^A-Za-z0-9]/.test(pwd)) return 4;
    return 3;
  };

  const score = calculateScore(password);
  const passwordsMatch = password.length > 0 && password === confirmPassword;

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!passwordsMatch) {
      setError("Master passwords do not match.");
      return;
    }
    if (password.length < 8) {
      setError("Master password must be at least 8 characters long.");
      return;
    }

    setError(null);
    setLocalLoading(true);
    try {
      const ok = await onCreateVault(password);
      if (!ok) {
        setError("Failed to create vault. Please try again.");
      }
    } catch (err: any) {
      setError(err?.message || "Failed to create vault.");
    } finally {
      setLocalLoading(false);
    }
  };

  return (
    <div className="h-screen w-screen bg-[var(--background)] flex items-center justify-center p-4 select-none">
      <div className="w-full max-w-md bg-[var(--surface-panel)] border border-[var(--border-subtle)] rounded-2xl shadow-2xl p-8 flex flex-col items-center gap-6">
        <div className="flex flex-col items-center gap-2 text-center">
          <div className="h-14 w-14 rounded-2xl bg-[var(--accent)] flex items-center justify-center shadow-lg shadow-[var(--accent-glowing)] mb-1">
            <Icon icon={Shield} size="lg" tone="primary" />
          </div>
          <h1 className="text-xl font-bold text-[var(--text-primary)] tracking-tight">Create Local Vault</h1>
          <p className="text-xs text-[var(--text-muted)] max-w-xs">
            Set a strong master password. It encrypts all data locally and cannot be recovered if lost.
          </p>
        </div>

        <form onSubmit={handleSubmit} className="w-full flex flex-col gap-4">
          <FieldGroup label="Master Password" required>
            <PasswordInput
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              placeholder="Create strong master password..."
              leadingIcon={Lock}
              autoFocus
            />
          </FieldGroup>

          {password && (
            <div className="p-3 bg-[var(--surface-card)] border border-[var(--border-subtle)] rounded-xl">
              <PasswordStrength score={score} />
            </div>
          )}

          <FieldGroup label="Confirm Master Password" required error={error || undefined}>
            <PasswordInput
              value={confirmPassword}
              onChange={(e) => setConfirmPassword(e.target.value)}
              placeholder="Re-enter master password..."
              leadingIcon={Lock}
            />
          </FieldGroup>

          {/* Requirements Checklist */}
          <div className="flex flex-col gap-1.5 p-3 bg-[var(--surface-card)] rounded-xl text-xs">
            <div className="flex items-center gap-2 text-[var(--text-secondary)]">
              <Icon icon={Check} size="xs" tone={password.length >= 8 ? "success" : "muted"} />
              <span>At least 8 characters long</span>
            </div>
            <div className="flex items-center gap-2 text-[var(--text-secondary)]">
              <Icon icon={Check} size="xs" tone={passwordsMatch ? "success" : "muted"} />
              <span>Passwords match</span>
            </div>
          </div>

          <Button
            type="submit"
            variant="primary"
            size="lg"
            isLoading={isCreating || localLoading}
            disabled={!passwordsMatch || password.length < 8}
            className="w-full font-bold mt-2"
          >
            Create Vault
          </Button>
        </form>
      </div>
    </div>
  );
};
