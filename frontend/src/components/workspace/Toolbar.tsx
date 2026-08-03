import React from "react";
import { SearchBar } from "../layout/SearchBar";
import { Button } from "../core/Button";
import { ToolbarButton } from "../layout/ToolbarButton";
import { Plus, Lock, Settings } from "lucide-react";

export interface ToolbarProps {
  searchQuery: string;
  onSearchChange: (query: string) => void;
  onNewEntry: () => void;
  onLockVault: () => void;
  onOpenSettings: () => void;
}

export const Toolbar: React.FC<ToolbarProps> = ({
  searchQuery,
  onSearchChange,
  onNewEntry,
  onLockVault,
  onOpenSettings,
}) => {
  return (
    <header className="flex items-center justify-between gap-3 p-3 bg-[var(--surface-panel)] border-b border-[var(--border-subtle)]">
      <div className="flex-1 max-w-sm">
        <SearchBar
          value={searchQuery}
          onChange={(e) => onSearchChange(e.target.value)}
          onClear={() => onSearchChange("")}
        />
      </div>
      <div className="flex items-center gap-2">
        <Button variant="primary" size="sm" leadingIcon={Plus} onClick={onNewEntry}>
          New Entry
        </Button>
        <ToolbarButton label="Settings" onClick={onOpenSettings}>
          <Settings className="h-4 w-4 text-[var(--text-secondary)]" />
        </ToolbarButton>
        <ToolbarButton label="Lock Vault" onClick={onLockVault}>
          <Lock className="h-4 w-4 text-[var(--text-secondary)]" />
        </ToolbarButton>
      </div>
    </header>
  );
};
