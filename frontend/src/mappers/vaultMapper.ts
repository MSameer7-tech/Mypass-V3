import { MockVaultEntry } from "../mocks/vault";

export interface VaultEntryDTO {
  id: number;
  title: string;
  username: string;
  password?: string;
  website_url?: string;
  notes?: string;
  is_favorite: boolean;
  category: string;
  is_breached?: boolean;
  updated_at?: string;
}

export function mapDTOToVaultEntry(dto: VaultEntryDTO): MockVaultEntry {
  return {
    id: dto.id,
    title: dto.title,
    username: dto.username || "",
    password: dto.password,
    websiteUrl: dto.website_url || "",
    notes: dto.notes,
    favorite: dto.is_favorite || false,
    category: (dto.category as MockVaultEntry["category"]) || "Passwords",
    securityStatus: dto.is_breached ? "breached" : "secure",
    strengthScore: dto.password && dto.password.length > 12 ? 4 : 2,
    updatedAt: dto.updated_at || "Just now",
  };
}

export function mapVaultEntryToDTO(entry: MockVaultEntry): VaultEntryDTO {
  return {
    id: entry.id,
    title: entry.title,
    username: entry.username,
    password: entry.password,
    website_url: entry.websiteUrl,
    notes: entry.notes,
    is_favorite: entry.favorite,
    category: entry.category,
    is_breached: entry.securityStatus === "breached",
    updated_at: entry.updatedAt,
  };
}
