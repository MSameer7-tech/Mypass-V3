import React from "react";
import { VaultCard } from "../domain/VaultCard";
import { EmptyState } from "../layout/EmptyState";
import { Skeleton } from "../core/Skeleton";
import { MockVaultEntry } from "../../mocks/vault";

export interface VaultListProps {
  entries: MockVaultEntry[];
  selectedId?: number;
  isLoading?: boolean;
  onSelectEntry: (id: number) => void;
  onToggleFavorite?: (id: number, e: React.MouseEvent) => void;
}

export const VaultList: React.FC<VaultListProps> = ({
  entries,
  selectedId,
  isLoading = false,
  onSelectEntry,
  onToggleFavorite,
}) => {
  if (isLoading) {
    return (
      <div className="flex flex-col gap-2 p-3">
        {[1, 2, 3, 4, 5].map((i) => (
          <Skeleton key={i} variant="listRow" />
        ))}
      </div>
    );
  }

  if (entries.length === 0) {
    return (
      <div className="flex items-center justify-center h-full p-4">
        <EmptyState variant="noSearchResults" />
      </div>
    );
  }

  return (
    <div className="flex-1 overflow-y-auto p-3 flex flex-col gap-2">
      {entries.map((entry) => (
        <VaultCard
          key={entry.id}
          id={entry.id}
          title={entry.title}
          username={entry.username}
          websiteUrl={entry.websiteUrl}
          favorite={entry.favorite}
          securityStatus={entry.securityStatus}
          updatedAt={entry.updatedAt}
          isSelected={selectedId === entry.id}
          onClick={() => onSelectEntry(entry.id)}
          onToggleFavorite={onToggleFavorite ? (e) => onToggleFavorite(entry.id, e) : undefined}
        />
      ))}
    </div>
  );
};
