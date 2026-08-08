import React from "react";
import { Button } from "../core/Button";
import { Plus, ChevronDown } from "lucide-react";
import { Icon } from "../core/Icon";

export interface ToolbarProps {
  sortOption: string;
  onSortChange: (val: string) => void;
  onNewEntry?: () => void;
}

export const Toolbar: React.FC<ToolbarProps> = ({
  sortOption,
  onSortChange,
  onNewEntry,
}) => {
  return (
    <header className="h-[48px] w-full bg-[var(--surface-panel)] border-b border-[var(--border-subtle)] px-4 flex items-center justify-between shrink-0 select-none">
      {/* Sorting Dropdown */}
      <div className="relative flex items-center">
        <select
          value={sortOption}
          onChange={(e) => onSortChange(e.target.value)}
          className="appearance-none bg-transparent hover:bg-[var(--surface-card-hover)] text-[var(--text-primary)] text-[13px] font-medium pl-3 pr-8 py-1.5 rounded-lg border border-transparent focus:outline-none transition-colors cursor-pointer"
        >
          <option value="recent" className="bg-[var(--surface-panel)] text-[var(--text-primary)]">Recently Used</option>
          <option value="az" className="bg-[var(--surface-panel)] text-[var(--text-primary)]">Alphabetical (A-Z)</option>
          <option value="za" className="bg-[var(--surface-panel)] text-[var(--text-primary)]">Alphabetical (Z-A)</option>
          <option value="oldest" className="bg-[var(--surface-panel)] text-[var(--text-primary)]">Oldest First</option>
        </select>
        <Icon icon={ChevronDown} size="xs" className="absolute right-2 pointer-events-none text-[var(--text-muted)]" />
      </div>

      {/* Primary New Entry Button */}
      {onNewEntry && (
        <Button
          variant="primary"
          size="sm"
          leadingIcon={Plus}
          onClick={onNewEntry}
          className="h-8 rounded-lg text-xs font-semibold px-3 shadow-xs hover:shadow-button-glow transition-all"
        >
          New Entry
        </Button>
      )}
    </header>
  );
};
