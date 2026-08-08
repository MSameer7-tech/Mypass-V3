import React from "react";
import { LucideIcon } from "lucide-react";

export type IconSize = "xs" | "sm" | "md" | "lg" | "xl";
export type IconTone = "primary" | "secondary" | "muted" | "accent" | "danger" | "success" | "warning" | "inherit";

export interface IconProps extends React.SVGProps<SVGSVGElement> {
  icon: LucideIcon;
  size?: IconSize;
  tone?: IconTone;
  className?: string;
}

const sizeMap: Record<IconSize, number> = {
  xs: 12,
  sm: 16,
  md: 20,
  lg: 24,
  xl: 32,
};

const toneMap: Record<IconTone, string> = {
  primary: "var(--text-primary)",
  secondary: "var(--text-secondary)",
  muted: "var(--text-muted)",
  accent: "var(--accent)",
  danger: "var(--danger)",
  success: "var(--success)",
  warning: "var(--warning)",
  inherit: "currentColor",
};

export const Icon: React.FC<IconProps> = ({
  icon: LucideComponent,
  size = "md",
  tone = "primary",
  className = "",
  style,
  ...props
}) => {
  const pixelSize = sizeMap[size];
  const color = toneMap[tone];

  return (
    <LucideComponent
      size={pixelSize}
      style={{ color, strokeWidth: 1.75, ...style }}
      className={`inline-block shrink-0 transition-colors duration-150 ${className}`}
      {...props}
    />
  );
};
