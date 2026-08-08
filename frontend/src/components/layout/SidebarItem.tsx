import React from "react";
import { Icon, IconProps } from "../core/Icon";

export interface SidebarItemProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  icon: IconProps["icon"];
  title: string;
  count?: number;
  isSelected?: boolean;
  isDisabled?: boolean;
  shortcut?: string;
  badge?: React.ReactNode;
}

export const SidebarItem: React.FC<SidebarItemProps> = ({
  icon,
  title,
  count,
  isSelected = false,
  isDisabled = false,
  shortcut,
  badge,
  className = "",
  ...props
}) => {
  const activeStyle = isSelected
    ? "bg-[var(--surface-card-selected)] text-[var(--text-primary)] font-semibold"
    : "text-[var(--text-secondary)] hover:bg-[var(--surface-card-hover)] hover:text-[var(--text-primary)] font-medium";

  return (
    <button
      disabled={isDisabled}
      className={`flex items-center justify-between w-full h-[34px] px-3 text-[13px] rounded-lg transition-all duration-150 select-none focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-[var(--border-focus)] disabled:opacity-40 disabled:pointer-events-none ${activeStyle} ${className}`}
      {...props}
    >
      <div className="flex items-center gap-2.5 min-w-0">
        <Icon icon={icon} size="sm" tone={isSelected ? "accent" : "muted"} />
        <span className="truncate">{title}</span>
      </div>
      <div className="flex items-center gap-1.5 shrink-0 ml-2">
        {badge}
        {count !== undefined && (
          <span className="px-2 py-0.5 text-[11px] font-mono font-medium rounded-full bg-[var(--surface-card-hover)] text-[var(--text-muted)]">
            {count}
          </span>
        )}
        {shortcut && (
          <kbd className="px-1 text-[11px] font-mono text-[var(--text-muted)] opacity-60">
            {shortcut}
          </kbd>
        )}
      </div>
    </button>
  );
};
