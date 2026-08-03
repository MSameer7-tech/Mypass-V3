import React from "react";
import { Button, ButtonProps } from "../core/Button";

export interface ToolbarButtonProps extends ButtonProps {
  label: string;
}

export const ToolbarButton: React.FC<ToolbarButtonProps> = ({
  label,
  variant = "ghost",
  size = "sm",
  className = "",
  children,
  ...props
}) => {
  return (
    <Button
      variant={variant}
      size={size}
      aria-label={label}
      title={label}
      className={`text-xs font-semibold text-[var(--text-secondary)] hover:text-[var(--text-primary)] ${className}`}
      {...props}
    >
      {children || label}
    </Button>
  );
};
