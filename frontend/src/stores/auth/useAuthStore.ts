import { create } from "zustand";

export type SessionState = "UNLOCKED" | "LOCKED" | "UNINITIALIZED";

export interface AuthState {
  sessionState: SessionState;
  isLocked: boolean;
  isUnlocking: boolean;
  user: { name: string; email: string } | null;
  autoLockMinutes: number;

  // Semantic Actions
  lockVault: () => void;
  unlockVault: (masterPassword?: string) => Promise<boolean>;
  setSessionState: (state: SessionState) => void;
}

export const useAuthStore = create<AuthState>((set) => ({
  sessionState: "UNLOCKED",
  isLocked: false,
  isUnlocking: false,
  user: { name: "Sameer", email: "sameer@mypass.app" },
  autoLockMinutes: 15,

  lockVault: () => set({ sessionState: "LOCKED", isLocked: true }),

  unlockVault: async (_masterPassword) => {
    set({ isUnlocking: true });
    // Mock unlock delay
    await new Promise((resolve) => setTimeout(resolve, 300));
    set({ sessionState: "UNLOCKED", isLocked: false, isUnlocking: false });
    return true;
  },

  setSessionState: (sessionState) =>
    set({ sessionState, isLocked: sessionState === "LOCKED" }),
}));
