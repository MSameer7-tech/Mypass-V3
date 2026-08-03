import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { mockVaultEntries, MockVaultEntry } from "../mocks/vault";

export const VAULT_QUERY_KEY = ["vault", "entries"];

export function useVaultEntriesQuery() {
  return useQuery<MockVaultEntry[]>({
    queryKey: VAULT_QUERY_KEY,
    queryFn: async () => {
      // Mock fetch simulation
      return mockVaultEntries;
    },
  });
}

export function useDeleteEntryMutation() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async (id: number) => {
      // Mock mutation simulation
      return id;
    },
    onSuccess: (deletedId) => {
      queryClient.setQueryData<MockVaultEntry[]>(VAULT_QUERY_KEY, (old) =>
        old ? old.filter((e) => e.id !== deletedId) : []
      );
    },
  });
}
