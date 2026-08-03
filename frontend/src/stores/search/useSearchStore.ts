import { create } from "zustand";

export interface SearchState {
  query: string;
  recentSearches: string[];
  commandPaletteOpen: boolean;

  // Actions
  setSearchQuery: (query: string) => void;
  setCommandPaletteOpen: (open: boolean) => void;
  clearSearch: () => void;
  addRecentSearch: (query: string) => void;
}

export const useSearchStore = create<SearchState>((set) => ({
  query: "",
  recentSearches: ["GitHub", "Amazon", "API Key"],
  commandPaletteOpen: false,

  setSearchQuery: (query) => set({ query }),
  setCommandPaletteOpen: (commandPaletteOpen) => set({ commandPaletteOpen }),
  clearSearch: () => set({ query: "" }),
  addRecentSearch: (searchTerm) =>
    set((state) => ({
      recentSearches: Array.from(new Set([searchTerm, ...state.recentSearches])).slice(0, 5),
    })),
}));
