import { create } from "zustand";
import { AuthRepository } from "../../repositories/AuthRepository";

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

  // Actions
  checkVaultStatus: () => Promise<void>;
  unlockVault: (masterPassword: string) => Promise<boolean>;
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
      set({ sessionState: "UNLOCKED", lastActivityTimestamp: Date.now() });
      return true;
    }

    set({
      sessionState: "LOCKED",
      authError: res.success ? "Invalid password" : res.error.message,
    });
    return false;
  },

  lockVault: () => {
    set({ sessionState: "LOCKING" });
    AuthRepository.lock();
    set({ sessionState: "LOCKED", lastActivityTimestamp: Date.now() });
  },

  createVault: async (masterPassword) => {
    set({ sessionState: "UNLOCKING", authError: null });
    const res = await AuthRepository.unlock(masterPassword);
    if (res.success) {
      set({ sessionState: "UNLOCKED", lastActivityTimestamp: Date.now() });
      return true;
    }
    set({ sessionState: "NO_VAULT", authError: "Failed to create vault." });
    return false;
  },

  resetActivityTimer: () => {
    if (get().sessionState === "UNLOCKED") {
      set({ lastActivityTimestamp: Date.now() });
    }
  },

  setAutoLockMinutes: (minutes) => set({ autoLockMinutes: minutes }),
}));
