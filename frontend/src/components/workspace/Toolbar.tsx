import React from "react";
import { SearchInput } from "../core/Input";
import { Button } from "../core/Button";
import { IconButton } from "../core/IconButton";
import { Plus, Lock, Settings } from "lucide-react";

export interface ToolbarProps {
  searchQuery: string;
  onSearchChange: (query: string) => void;
  onNewEntry?: () => void;
  onLockVault?: () => void;
  onOpenSettings?: () => void;
}

export const Toolbar: React.FC<ToolbarProps> = ({
  searchQuery,
  onSearchChange,
  onNewEntry,
  onLockVault,
  onOpenSettings,
}) => {
  return (
    <header className="h-14 w-full bg-[var(--surface-panel)] border-b border-[var(--border-subtle)] px-4 flex items-center justify-between gap-3 shrink-0 select-none">
      {/* Search Input Dominates Width */}
      <div className="flex-1 max-w-xl">
        <SearchInput
          value={searchQuery}
          onChange={(e) => onSearchChange(e.target.value)}
          onClear={() => onSearchChange("")}
          placeholder="Search vault (⌘F)..."
          className="w-full"
        />
      </div>

      {/* Primary Actions & Controls Aligned */}
      <div className="flex items-center gap-2 shrink-0">
        {onNewEntry && (
          <Button
            variant="primary"
            size="sm"
            leadingIcon={Plus}
            onClick={onNewEntry}
            className="font-bold shadow-xs px-3 py-1.5"
          >
            New Entry
          </Button>
        )}

        {onOpenSettings && (
          <IconButton
            icon={Settings}
            label="Open Settings"
            size="sm"
            variant="secondary"
            onClick={onOpenSettings}
          />
        )}

        {onLockVault && (
          <IconButton
            icon={Lock}
            label="Lock Vault"
            size="sm"
            variant="secondary"
            onClick={onLockVault}
          />
        )}
      </div>
    </header>
  );
};
