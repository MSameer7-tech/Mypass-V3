import React, { useState } from "react";
import { Dialog } from "../../../components/overlay/Dialog";
import { PasswordInput } from "../../../components/core/Input";
import { Button } from "../../../components/core/Button";
import { PasswordStrength } from "../../../components/domain/PasswordStrength";
import { FieldGroup } from "../../../components/layout/FieldGroup";
import { Icon } from "../../../components/core/Icon";
import { ShieldAlert, Check, Lock, AlertCircle, KeyRound, Loader2 } from "lucide-react";
import { AuthRepository } from "../../../repositories/AuthRepository";

export interface ChangeMasterPasswordModalProps {
  open: boolean;
  onClose: () => void;
  onSuccess: () => void;
}

export const ChangeMasterPasswordModal: React.FC<ChangeMasterPasswordModalProps> = ({
  open,
  onClose,
  onSuccess,
}) => {
  const [currentPassword, setCurrentPassword] = useState("");
  const [newPassword, setNewPassword] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [isSubmitting, setIsSubmitting] = useState(false);

  const calculateScore = (pwd: string) => {
    if (!pwd) return 0;
    if (pwd.length < 8) return 1;
    if (pwd.length < 12) return 2;
    if (/[A-Z]/.test(pwd) && /[0-9]/.test(pwd) && /[^A-Za-z0-9]/.test(pwd)) return 4;
    return 3;
  };

  const score = calculateScore(newPassword);
  const isMinLength = newPassword.length >= 8;
  const isDifferent = newPassword.length > 0 && currentPassword.length > 0 && newPassword !== currentPassword;
  const isMatching = newPassword.length > 0 && newPassword === confirmPassword;
  const canSubmit = isMinLength && isDifferent && isMatching && currentPassword.length > 0 && !isSubmitting;

  const handleClose = () => {
    if (isSubmitting) return;
    setCurrentPassword("");
    setNewPassword("");
    setConfirmPassword("");
    setError(null);
    onClose();
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!canSubmit) return;

    setError(null);
    setIsSubmitting(true);

    try {
      const res = await AuthRepository.changeMasterPassword(currentPassword, newPassword);

      if (res.success && res.data.success) {
        handleClose();
        onSuccess();
      } else {
        const errorMsg = res.success ? "Failed to change master password." : res.error.message;
        setError(errorMsg);
      }
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : "An unexpected error occurred while rotating master password.");
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <Dialog
      open={open}
      onClose={handleClose}
      title="Change Master Password"
      description="Update the master key used to encrypt all local vault items."
      size="md"
    >
      <form onSubmit={handleSubmit} className="flex flex-col gap-4">
        {/* Warning Banner */}
        <div className="flex items-start gap-3 p-3 bg-[var(--surface-card)] border border-[var(--border-subtle)] rounded-xl text-xs text-[var(--text-secondary)]">
          <div className="p-1 rounded-md bg-amber-500/10 text-amber-500 shrink-0 mt-0.5">
            <Icon icon={ShieldAlert} size="xs" />
          </div>
          <span className="leading-relaxed">
            Changing your master password re-encrypts your vault and resets biometric unlock. You can enable biometrics again after unlocking with your new password.
          </span>
        </div>

        {/* Error Alert */}
        {error && (
          <div className="flex items-center gap-2 p-3 bg-red-500/10 border border-red-500/20 text-red-400 rounded-xl text-xs">
            <Icon icon={AlertCircle} size="xs" />
            <span className="font-medium">{error}</span>
          </div>
        )}

        {/* Current Password Field */}
        <FieldGroup label="Current Master Password" required>
          <PasswordInput
            value={currentPassword}
            onChange={(e) => setCurrentPassword(e.target.value)}
            placeholder="Enter current master password..."
            leadingIcon={Lock}
            disabled={isSubmitting}
            autoFocus
          />
        </FieldGroup>

        {/* New Password Field */}
        <FieldGroup label="New Master Password" required>
          <PasswordInput
            value={newPassword}
            onChange={(e) => setNewPassword(e.target.value)}
            placeholder="Create strong new master password..."
            leadingIcon={KeyRound}
            disabled={isSubmitting}
          />
        </FieldGroup>

        {newPassword && (
          <div className="p-3 bg-[var(--surface-card)] border border-[var(--border-subtle)] rounded-xl">
            <PasswordStrength score={score} />
          </div>
        )}

        {/* Confirm New Password Field */}
        <FieldGroup label="Confirm New Master Password" required>
          <PasswordInput
            value={confirmPassword}
            onChange={(e) => setConfirmPassword(e.target.value)}
            placeholder="Re-enter new master password..."
            leadingIcon={KeyRound}
            disabled={isSubmitting}
          />
        </FieldGroup>

        {/* Requirements Checklist */}
        <div className="flex flex-col gap-1.5 p-3 bg-[var(--surface-card)] rounded-xl text-xs">
          <div className="flex items-center gap-2 text-[var(--text-secondary)]">
            <Icon icon={Check} size="xs" tone={isMinLength ? "success" : "muted"} />
            <span>At least 8 characters long</span>
          </div>
          <div className="flex items-center gap-2 text-[var(--text-secondary)]">
            <Icon icon={Check} size="xs" tone={isDifferent ? "success" : "muted"} />
            <span>Different from current password</span>
          </div>
          <div className="flex items-center gap-2 text-[var(--text-secondary)]">
            <Icon icon={Check} size="xs" tone={isMatching ? "success" : "muted"} />
            <span>New passwords match</span>
          </div>
        </div>

        {/* Action Buttons */}
        <div className="flex items-center justify-end gap-3 pt-3 border-t border-[var(--border-subtle)] mt-2">
          <Button
            type="button"
            variant="secondary"
            size="md"
            onClick={handleClose}
            disabled={isSubmitting}
          >
            Cancel
          </Button>
          <Button
            type="submit"
            variant="primary"
            size="md"
            isLoading={isSubmitting}
            disabled={!canSubmit}
            className="font-bold min-w-[160px]"
          >
            {isSubmitting ? (
              <span className="flex items-center gap-2">
                <Loader2 size={14} className="animate-spin" />
                Re-encrypting...
              </span>
            ) : (
              "Update Password"
            )}
          </Button>
        </div>
      </form>
    </Dialog>
  );
};
