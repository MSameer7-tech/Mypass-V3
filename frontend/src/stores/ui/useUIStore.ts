import { create } from "zustand";

export type DialogType = "newEntry" | "editEntry" | "deleteConfirm" | "settings" | null;
export type SheetType = "details" | "audit" | null;

export interface UIState {
  activeDialog: DialogType;
  activeSheet: SheetType;
  loadingMessage: string | null;

  // Actions
  openDialog: (dialog: DialogType) => void;
  closeDialog: () => void;
  openSheet: (sheet: SheetType) => void;
  closeSheet: () => void;
  setLoadingMessage: (msg: string | null) => void;
}

export const useUIStore = create<UIState>((set) => ({
  activeDialog: null,
  activeSheet: null,
  loadingMessage: null,

  openDialog: (activeDialog) => set({ activeDialog }),
  closeDialog: () => set({ activeDialog: null }),
  openSheet: (activeSheet) => set({ activeSheet }),
  closeSheet: () => set({ activeSheet: null }),
  setLoadingMessage: (loadingMessage) => set({ loadingMessage }),
}));
