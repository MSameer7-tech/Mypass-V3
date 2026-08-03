import React from "react";
import { SearchInput, InputProps } from "../core/Input";

export interface SearchBarProps extends InputProps {
  shortcutHint?: string;
  isLoading?: boolean;
}

export const SearchBar = React.forwardRef<HTMLInputElement, SearchBarProps>(
  ({ shortcutHint = "⌘K", isLoading = false, value, onClear, className = "", ...props }, ref) => {
    return (
      <div className="relative flex items-center w-full">
        <SearchInput
          ref={ref}
          value={value}
          onClear={onClear}
          className={`pr-14 ${className}`}
          {...props}
        />
        {shortcutHint && !value && (
          <kbd className="absolute right-3 pointer-events-none px-1.5 py-0.5 text-[10px] font-semibold font-mono text-[var(--text-muted)] bg-[var(--surface-sidebar)] border border-[var(--border-subtle)] rounded">
            {shortcutHint}
          </kbd>
        )}
      </div>
    );
  }
);

SearchBar.displayName = "SearchBar";
