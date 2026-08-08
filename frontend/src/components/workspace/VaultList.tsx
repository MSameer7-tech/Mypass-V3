import React from "react";
import { VaultCard } from "../domain/VaultCard";
import { EmptyState } from "../layout/EmptyState";
import { Skeleton } from "../core/Skeleton";
import { MockVaultEntry } from "../../mocks/vault";
import { motion, AnimatePresence } from "framer-motion";

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
      <AnimatePresence initial={false}>
        {entries.map((entry) => (
          <motion.div
            key={entry.id}
            layout="position"
            initial={{ opacity: 0, y: 4 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, scale: 0.97, height: 0, marginTop: 0, marginBottom: 0, overflow: "hidden" }}
            transition={{ duration: 0.2, ease: "easeOut" }}
          >
            <VaultCard
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
          </motion.div>
        ))}
      </AnimatePresence>
    </div>
  );
};
