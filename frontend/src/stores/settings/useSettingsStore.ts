import { create } from "zustand";
import { persist } from "zustand/middleware";

export interface SettingsState {
  theme: "dark" | "light" | "system";
  compactMode: boolean;
  showFavicons: boolean;
  reducedMotion: boolean;

  // Actions
  setTheme: (theme: "dark" | "light" | "system") => void;
  setCompactMode: (compact: boolean) => void;
  setShowFavicons: (show: boolean) => void;
  setReducedMotion: (reduced: boolean) => void;
}

export const useSettingsStore = create<SettingsState>()(
  persist(
    (set) => ({
      theme: "dark",
      compactMode: false,
      showFavicons: true,
      reducedMotion: false,

      setTheme: (theme) => set({ theme }),
      setCompactMode: (compactMode) => set({ compactMode }),
      setShowFavicons: (showFavicons) => set({ showFavicons }),
      setReducedMotion: (reducedMotion) => set({ reducedMotion }),
    }),
    {
      name: "mypass-ui-settings",
    }
  )
);
