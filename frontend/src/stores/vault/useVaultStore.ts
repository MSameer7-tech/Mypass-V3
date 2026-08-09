import { create } from "zustand";
import { MockVaultEntry } from "../../mocks/vault";

export interface VaultState {
  entries: MockVaultEntry[];
  selectedEntryId: number | null;
  selectedCategory: string;
  sortOrder: "title" | "updatedAt";
  isLoading: boolean;
  error: string | null;

  // Semantic Actions
  selectEntry: (id: number | null) => void;
  toggleFavorite: (id: number) => void;
  deleteEntry: (id: number) => void;
  addEntry: (entry: Omit<MockVaultEntry, "id">) => void;
  updateEntry: (id: number, updates: Partial<MockVaultEntry>) => void;
  clearSelection: () => void;
  setSelectedCategory: (category: string) => void;
  setEntries: (entries: MockVaultEntry[]) => void;
}

export const useVaultStore = create<VaultState>((set) => ({
  entries: [],
  selectedEntryId: 1,
  selectedCategory: "All",
  sortOrder: "title",
  isLoading: false,
  error: null,

  selectEntry: (id) => set({ selectedEntryId: id }),

  toggleFavorite: (id) =>
    set((state) => ({
      entries: state.entries.map((entry) =>
        entry.id === id ? { ...entry, favorite: !entry.favorite } : entry
      ),
    })),

  deleteEntry: (id) =>
    set((state) => {
      const newEntries = state.entries.filter((entry) => entry.id !== id);
      const newSelectedId =
        state.selectedEntryId === id
          ? newEntries.length > 0
            ? newEntries[0].id
            : null
          : state.selectedEntryId;

      return {
        entries: newEntries,
        selectedEntryId: newSelectedId,
      };
    }),

  addEntry: (newEntryData) =>
    set((state) => {
      const newId = Math.max(0, ...state.entries.map((e) => e.id)) + 1;
      const createdEntry: MockVaultEntry = {
        ...newEntryData,
        id: newId,
      };
      return {
        entries: [createdEntry, ...state.entries],
        selectedEntryId: newId,
      };
    }),

  updateEntry: (id, updates) =>
    set((state) => ({
      entries: state.entries.map((entry) =>
        entry.id === id ? { ...entry, ...updates } : entry
      ),
    })),

  clearSelection: () => set({ selectedEntryId: null }),

  setSelectedCategory: (category) => set({ selectedCategory: category }),

  setEntries: (entries) => set({ entries }),
}));
