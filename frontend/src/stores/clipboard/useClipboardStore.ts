import { create } from "zustand";

interface ClipboardState {
  lastCopiedValue: string | null;
  clearTimeoutId: ReturnType<typeof setTimeout> | null;
  
  copy: (value: string, autoClearSeconds: number) => Promise<boolean>;
  clearIfOwned: () => Promise<void>;
  resetTimer: () => void;
}

export const useClipboardStore = create<ClipboardState>((set, get) => ({
  lastCopiedValue: null,
  clearTimeoutId: null,

  copy: async (value, autoClearSeconds) => {
    try {
      await navigator.clipboard.writeText(value);
      set({ lastCopiedValue: value });
      
      const { clearTimeoutId } = get();
      if (clearTimeoutId) {
        clearTimeout(clearTimeoutId);
      }
      
      if (autoClearSeconds > 0) {
        const timerId = setTimeout(async () => {
          await get().clearIfOwned();
        }, autoClearSeconds * 1000);
        set({ clearTimeoutId: timerId });
      } else {
        set({ clearTimeoutId: null });
      }
      
      return true;
    } catch (e) {
      return false;
    }
  },

  clearIfOwned: async () => {
    try {
      const { lastCopiedValue, clearTimeoutId } = get();
      if (!lastCopiedValue) return;
      
      const currentText = await navigator.clipboard.readText();
      if (currentText === lastCopiedValue) {
        await navigator.clipboard.writeText("");
      }
      
      if (clearTimeoutId) clearTimeout(clearTimeoutId);
      set({ lastCopiedValue: null, clearTimeoutId: null });
    } catch (e) {}
  },
  
  resetTimer: () => {
    const { clearTimeoutId } = get();
    if (clearTimeoutId) {
      clearTimeout(clearTimeoutId);
      set({ clearTimeoutId: null, lastCopiedValue: null });
    }
  }
}));
