import { create } from "zustand";
import { persist } from "zustand/middleware";

export interface SettingsState {
  theme: "dark" | "light" | "system";
  compactMode: boolean;
  showFavicons: boolean;
  reducedMotion: boolean;
  autoLockMinutes: number;
  clipboardAutoClearSeconds: number;
  confirmBeforeDelete: boolean;

  // Actions
  setTheme: (theme: "dark" | "light" | "system") => void;
  setCompactMode: (compact: boolean) => void;
  setShowFavicons: (show: boolean) => void;
  setReducedMotion: (reduced: boolean) => void;
  setAutoLockMinutes: (minutes: number) => void;
  setClipboardAutoClearSeconds: (seconds: number) => void;
  setConfirmBeforeDelete: (confirm: boolean) => void;
}

export const useSettingsStore = create<SettingsState>()(
  persist(
    (set) => ({
      theme: "dark",
      compactMode: false,
      showFavicons: true,
      reducedMotion: false,
      autoLockMinutes: 15,
      clipboardAutoClearSeconds: 30,
      confirmBeforeDelete: true,

      setTheme: (theme) => set({ theme }),
      setCompactMode: (compactMode) => set({ compactMode }),
      setShowFavicons: (showFavicons) => set({ showFavicons }),
      setReducedMotion: (reducedMotion) => set({ reducedMotion }),
      setAutoLockMinutes: (autoLockMinutes) => set({ autoLockMinutes }),
      setClipboardAutoClearSeconds: (clipboardAutoClearSeconds) => set({ clipboardAutoClearSeconds }),
      setConfirmBeforeDelete: (confirmBeforeDelete) => set({ confirmBeforeDelete }),
    }),
    {
      name: "mypass-ui-settings",
    }
  )
);
