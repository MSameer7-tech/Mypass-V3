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
    ? "bg-[var(--surface-card-selected)] text-[var(--text-primary)] font-semibold shadow-xs"
    : "text-[var(--text-secondary)] hover:bg-white/5 hover:text-[var(--text-primary)]";

  return (
    <button
      disabled={isDisabled}
      className={`flex items-center justify-between w-full h-8 px-2.5 text-xs rounded-lg transition-all duration-150 select-none focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-[var(--border-focus)] disabled:opacity-40 disabled:pointer-events-none ${activeStyle} ${className}`}
      {...props}
    >
      <div className="flex items-center gap-2.5 min-w-0">
        <Icon icon={icon} size="sm" tone={isSelected ? "accent" : "muted"} />
        <span className="truncate">{title}</span>
      </div>
      <div className="flex items-center gap-1.5 shrink-0 ml-2">
        {badge}
        {count !== undefined && (
          <span className="px-1.5 py-0.5 text-[10px] font-mono font-medium rounded-full bg-white/5 text-[var(--text-muted)]">
            {count}
          </span>
        )}
        {shortcut && (
          <kbd className="px-1 text-[10px] font-mono text-[var(--text-muted)] opacity-60">
            {shortcut}
          </kbd>
        )}
      </div>
    </button>
  );
};
