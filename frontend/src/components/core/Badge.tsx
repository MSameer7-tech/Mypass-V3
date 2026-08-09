import React from "react";

export type BadgeVariant = "default" | "success" | "warning" | "danger" | "outline";

export interface BadgeProps extends React.HTMLAttributes<HTMLSpanElement> {
  variant?: BadgeVariant;
  children: React.ReactNode;
}

const variantStyles: Record<BadgeVariant, string> = {
  default: "bg-[var(--surface-card-selected)] text-[var(--text-primary)] border border-[var(--border-subtle)]",
  success: "bg-[var(--success-surface)] text-[var(--success)] border border-[var(--success-border)]",
  warning: "bg-[var(--warning-surface)] text-[var(--warning)] border border-[var(--warning-border)]",
  danger: "bg-[var(--danger-surface)] text-[var(--danger)] border border-[var(--danger-border)]",
  outline: "bg-transparent text-[var(--text-secondary)] border border-[var(--border-subtle)]",
};

export const Badge: React.FC<BadgeProps> = ({
  variant = "default",
  children,
  className = "",
  ...props
}) => {
  return (
    <span
      className={`inline-flex items-center px-2 py-0.5 text-xs font-semibold rounded-md ${variantStyles[variant]} ${className}`}
      {...props}
    >
      {children}
    </span>
  );
};
