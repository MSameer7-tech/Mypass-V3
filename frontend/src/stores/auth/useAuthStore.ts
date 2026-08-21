import { create } from "zustand";
import { AuthRepository } from "../../repositories/AuthRepository";
import { useClipboardStore } from "../clipboard/useClipboardStore";

export type SessionState =
  | "BOOTING"
  | "NO_VAULT"
  | "LOCKED"
  | "UNLOCKING"
  | "UNLOCKED"
  | "LOCKING"
  | "ERROR";

export interface AuthState {
  sessionState: SessionState;
  user: { name: string; email: string } | null;
  autoLockMinutes: number;
  lastActivityTimestamp: number;
  authError: string | null;
  failedUnlockAttempts: number;

  // Actions
  checkVaultStatus: () => Promise<void>;
  unlockVault: (masterPassword: string) => Promise<boolean>;
  unlockVaultWithBiometrics: () => Promise<boolean>;
  lockVault: () => void;
  createVault: (masterPassword: string) => Promise<boolean>;
  resetActivityTimer: () => void;
  setAutoLockMinutes: (minutes: number) => void;
}

export const useAuthStore = create<AuthState>((set, get) => ({
  sessionState: "BOOTING",
  user: { name: "Sameer", email: "sameer@mypass.app" },
  autoLockMinutes: 15,
  lastActivityTimestamp: Date.now(),
  authError: null,
  failedUnlockAttempts: 0,

  checkVaultStatus: async () => {
    set({ sessionState: "BOOTING", authError: null });
    const res = await AuthRepository.status();
    if (res.success) {
      set({ sessionState: res.data.sessionState });
    } else {
      set({ sessionState: "LOCKED" });
    }
  },

  unlockVault: async (masterPassword) => {
    set({ sessionState: "UNLOCKING", authError: null });
    
    const res = await AuthRepository.unlock(masterPassword);

    if (res.success && res.data.success) {
      set({ sessionState: "UNLOCKED", lastActivityTimestamp: Date.now(), failedUnlockAttempts: 0 });
      return true;
    }

    set({
      sessionState: "LOCKED",
      authError: res.success ? "Invalid password" : res.error.message,
      failedUnlockAttempts: get().failedUnlockAttempts + 1
    });
    return false;
  },

  unlockVaultWithBiometrics: async () => {
    set({ sessionState: "UNLOCKING", authError: null });
    const res = await AuthRepository.biometricUnlock();

    if (res.success && res.data.success) {
      set({ sessionState: "UNLOCKED", lastActivityTimestamp: Date.now() });
      return true;
    }

    set({
      sessionState: "LOCKED",
      authError: res.success ? "Biometric authentication failed" : res.error.message,
    });
    return false;
  },

  lockVault: () => {
    set({ sessionState: "LOCKING" });
    AuthRepository.lock();
    useClipboardStore.getState().clearIfOwned();
    set({ sessionState: "LOCKED", lastActivityTimestamp: Date.now() });
  },

  createVault: async (masterPassword) => {
    set({ authError: null });
    const res = await AuthRepository.unlock(masterPassword);
    if (res.success && res.data.success) {
      set({ sessionState: "UNLOCKED", lastActivityTimestamp: Date.now() });
      return true;
    }
    const errorMsg = res.success ? "Failed to initialize vault." : res.error.message;
    set({ sessionState: "NO_VAULT", authError: errorMsg });
    return false;
  },

  resetActivityTimer: () => {
    if (get().sessionState === "UNLOCKED") {
      set({ lastActivityTimestamp: Date.now() });
    }
  },

  setAutoLockMinutes: (minutes) => set({ autoLockMinutes: minutes }),
}));
