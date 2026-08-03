import { describe, it, expect, beforeEach } from "vitest";
import { useVaultStore } from "../vault/useVaultStore";
import { useAuthStore } from "../auth/useAuthStore";
import { mapDTOToVaultEntry, mapVaultEntryToDTO } from "../../mappers/vaultMapper";

describe("VaultStore & AuthStore Unit Tests", () => {
  beforeEach(() => {
    useVaultStore.setState({
      entries: [
        { id: 1, title: "GitHub", username: "user1", websiteUrl: "https://github.com", favorite: false, category: "Passwords", securityStatus: "secure", strengthScore: 4, updatedAt: "now" },
        { id: 2, title: "Amazon", username: "user2", websiteUrl: "https://amazon.com", favorite: true, category: "Passwords", securityStatus: "secure", strengthScore: 3, updatedAt: "now" },
      ],
      selectedEntryId: 1,
      selectedCategory: "All",
    });

    useAuthStore.setState({
      sessionState: "UNLOCKED",
      authError: null,
    });
  });

  it("selectEntry updates selectedEntryId", () => {
    useVaultStore.getState().selectEntry(2);
    expect(useVaultStore.getState().selectedEntryId).toBe(2);
  });

  it("toggleFavorite flips favorite state for entry", () => {
    useVaultStore.getState().toggleFavorite(1);
    expect(useVaultStore.getState().entries[0].favorite).toBe(true);
  });

  it("deleteEntry removes entry and adjusts selection", () => {
    useVaultStore.getState().deleteEntry(1);
    expect(useVaultStore.getState().entries).toHaveLength(1);
    expect(useVaultStore.getState().selectedEntryId).toBe(2);
  });

  it("addEntry adds new entry with incremented id", () => {
    useVaultStore.getState().addEntry({
      title: "Google",
      username: "user3",
      websiteUrl: "https://google.com",
      favorite: false,
      category: "Passwords",
      securityStatus: "secure",
      strengthScore: 4,
      updatedAt: "just now",
    });
    expect(useVaultStore.getState().entries).toHaveLength(3);
    expect(useVaultStore.getState().selectedEntryId).toBe(3);
  });

  it("lockVault sets sessionState to LOCKED", () => {
    useAuthStore.getState().lockVault();
    expect(useAuthStore.getState().sessionState).toBe("LOCKED");
  });

  it("vaultMapper maps DTOs correctly", () => {
    const dto = {
      id: 10,
      title: "Stripe",
      username: "billing",
      password: "secretpassword123",
      website_url: "https://stripe.com",
      is_favorite: true,
      category: "Developer Keys",
      is_breached: false,
    };
    const domain = mapDTOToVaultEntry(dto);
    expect(domain.title).toBe("Stripe");
    expect(domain.favorite).toBe(true);

    const backToDto = mapVaultEntryToDTO(domain);
    expect(backToDto.title).toBe("Stripe");
    expect(backToDto.is_favorite).toBe(true);
  });
});
