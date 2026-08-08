import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { VaultRepository } from "../repositories/VaultRepository";
import { MockVaultEntry } from "../mocks/vault";

export const VAULT_QUERY_KEY = ["vault", "entries"];

export function useVaultEntriesQuery() {
  return useQuery<MockVaultEntry[]>({
    queryKey: VAULT_QUERY_KEY,
    queryFn: async () => {
      const res = await VaultRepository.listEntries();
      if (res.success) {
        return res.data;
      }
      throw new Error(res.error.message);
    },
  });
}

export function useCreateEntryMutation() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async (entryData: {
      title: string;
      username: string;
      password?: string;
      websiteUrl?: string;
      notes?: string;
      category?: string;
    }) => {
      const res = await VaultRepository.createEntry(entryData);
      if (!res.success) throw new Error(res.error.message);
      return res.data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: VAULT_QUERY_KEY });
    },
  });
}

export function useUpdateEntryMutation() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async ({ id, updates }: { id: number; updates: Partial<MockVaultEntry> }) => {
      const res = await VaultRepository.updateEntry(id, updates);
      if (!res.success) throw new Error(res.error.message);
      return res.data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: VAULT_QUERY_KEY });
    },
  });
}

export function useDeleteEntryMutation() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async (id: number) => {
      const res = await VaultRepository.deleteEntry(id);
      if (!res.success) throw new Error(res.error.message);
      return id;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: VAULT_QUERY_KEY });
    },
  });
}
