import React from "react";
import { Button } from "../core/Button";
import { Plus, ChevronDown, ListFilter } from "lucide-react";
import { Icon } from "../core/Icon";

export interface ToolbarProps {
  activeCategory: string;
  itemCount: number;
  onNewEntry?: () => void;
}

export const Toolbar: React.FC<ToolbarProps> = ({
  activeCategory,
  itemCount,
  onNewEntry,
}) => {
  return (
    <header className="h-[48px] w-full bg-[var(--surface-panel)] border-b border-[var(--border-subtle)] px-4 flex items-center justify-between gap-3 shrink-0 select-none">
      {/* Category Title & Item Count */}
      <div className="flex items-center gap-2.5 min-w-0">
        <h2 className="text-sm font-bold text-[var(--text-primary)] tracking-tight truncate">
          {activeCategory === "All" ? "All Items" : activeCategory}
        </h2>
        <span className="px-2 py-0.5 rounded-full bg-white/5 text-[10px] font-mono font-medium text-[var(--text-muted)] shrink-0">
          {itemCount}
        </span>
      </div>

      {/* Primary New Entry Button & Quick Sort/Filter */}
      <div className="flex items-center gap-2 shrink-0">
        <div className="flex items-center gap-1 text-xs text-[var(--text-muted)] font-medium">
          <button className="flex items-center gap-1 hover:text-[var(--text-primary)] transition-colors px-2 py-1 rounded-md hover:bg-white/5 text-[11px]" title="Sort by">
            <span>Recently Used</span>
            <Icon icon={ChevronDown} size="xs" />
          </button>
          <button className="p-1 hover:text-[var(--text-primary)] rounded-md hover:bg-white/5" title="Filter list">
            <Icon icon={ListFilter} size="xs" />
          </button>
        </div>

        {onNewEntry && (
          <Button
            variant="primary"
            size="sm"
            leadingIcon={Plus}
            onClick={onNewEntry}
            className="h-8 rounded-lg text-xs font-semibold px-3 shadow-xs hover:shadow-button-glow transition-all ml-1"
          >
            New Entry
          </Button>
        )}
      </div>
    </header>
  );
};
