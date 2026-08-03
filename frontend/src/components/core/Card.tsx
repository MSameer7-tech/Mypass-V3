import React from "react";

export type CardVariant = "default" | "elevated" | "interactive" | "section";

export interface CardProps extends React.HTMLAttributes<HTMLDivElement> {
  variant?: CardVariant;
  isSelected?: boolean;
  children: React.ReactNode;
}

const variantStyles: Record<CardVariant, string> = {
  default: "bg-[var(--surface-card)] border border-[var(--border-subtle)] rounded-xl p-4",
  elevated: "bg-[var(--surface-panel)] border border-[var(--border-subtle)] shadow-lg rounded-xl p-4",
  interactive: "bg-[var(--surface-card)] hover:bg-[var(--surface-card-hover)] active:bg-[var(--surface-card-selected)] border border-[var(--border-subtle)] rounded-xl p-4 cursor-pointer transition-all duration-100",
  section: "bg-[var(--surface-panel)] border border-[var(--border-subtle)] rounded-xl p-5",
};

export const Card: React.FC<CardProps> = ({
  variant = "default",
  isSelected = false,
  children,
  className = "",
  ...props
}) => {
  const selectedStyle = isSelected
    ? "bg-[var(--surface-card-selected)] border-[var(--border-focus)] ring-1 ring-[var(--border-focus)]"
    : "";

  return (
    <div className={`${variantStyles[variant]} ${selectedStyle} ${className}`} {...props}>
      {children}
    </div>
  );
};
