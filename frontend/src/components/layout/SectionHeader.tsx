import React from "react";

export interface SectionHeaderProps {
  title: string;
  subtitle?: string;
  action?: React.ReactNode;
  className?: string;
}

export const SectionHeader: React.FC<SectionHeaderProps> = ({
  title,
  subtitle,
  action,
  className = "",
}) => {
  return (
    <div className={`flex items-center justify-between pb-3 border-b border-[var(--border-subtle)] ${className}`}>
      <div className="flex flex-col gap-0.5">
        <h2 className="text-lg font-bold text-[var(--text-primary)] tracking-tight">{title}</h2>
        {subtitle && <p className="text-xs text-[var(--text-muted)]">{subtitle}</p>}
      </div>
      {action && <div className="flex items-center gap-2">{action}</div>}
    </div>
  );
};
