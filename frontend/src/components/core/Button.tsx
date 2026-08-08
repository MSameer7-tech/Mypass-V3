import React from "react";
import { Icon, IconProps } from "./Icon";
import { Loader2 } from "lucide-react";
import { motion, HTMLMotionProps } from "framer-motion";
import { MOTION_TOKENS } from "../../constants/motion";

export type ButtonVariant = "primary" | "secondary" | "ghost" | "destructive" | "link";
export type ButtonSize = "sm" | "md" | "lg" | "icon";

export interface ButtonProps extends Omit<HTMLMotionProps<"button">, "ref"> {
  variant?: ButtonVariant;
  size?: ButtonSize;
  isLoading?: boolean;
  leadingIcon?: IconProps["icon"];
  trailingIcon?: IconProps["icon"];
  children?: React.ReactNode;
}

const variantStyles: Record<ButtonVariant, string> = {
  primary: "bg-[var(--accent)] hover:bg-[var(--accent-hover)] text-white shadow-sm border border-[var(--accent)]",
  secondary: "bg-[var(--surface-card)] hover:bg-[var(--surface-card-hover)] text-[var(--text-primary)] border border-[var(--border-subtle)]",
  ghost: "bg-transparent hover:bg-[var(--surface-card-hover)] text-[var(--text-secondary)] hover:text-[var(--text-primary)] border border-transparent",
  destructive: "bg-[var(--danger-surface)] hover:bg-red-950/40 text-[var(--danger)] border border-red-900/40",
  link: "bg-transparent text-[var(--accent)] hover:underline border border-transparent p-0",
};

const sizeStyles: Record<ButtonSize, string> = {
  sm: "h-8 px-3 text-xs gap-1.5 rounded-md",
  md: "h-10 px-4 text-sm gap-2 rounded-lg",
  lg: "h-12 px-6 text-base gap-2.5 rounded-lg",
  icon: "h-9 w-9 p-0 rounded-lg justify-center",
};

export const Button = React.forwardRef<HTMLButtonElement, ButtonProps>(
  (
    {
      variant = "primary",
      size = "md",
      isLoading = false,
      leadingIcon,
      trailingIcon,
      disabled,
      children,
      className = "",
      ...props
    },
    ref
  ) => {
    const isButtonDisabled = disabled || isLoading;
    
    const tapScale = 0.98;

    return (
      <motion.button
        ref={ref as any}
        disabled={isButtonDisabled}
        whileTap={isButtonDisabled ? undefined : { scale: tapScale }}
        transition={{ duration: MOTION_TOKENS.duration.press, ease: MOTION_TOKENS.ease.out }}
        className={`inline-flex items-center justify-center font-medium transition-colors duration-150 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-[var(--border-focus)] disabled:opacity-50 disabled:pointer-events-none ${variantStyles[variant]} ${sizeStyles[size]} ${className}`}
        {...props}
      >
        {isLoading ? (
          <Loader2 className="animate-spin h-4 w-4 shrink-0 text-current" />
        ) : (
          <>
            {leadingIcon && <Icon icon={leadingIcon} size={size === "sm" ? "xs" : "sm"} tone="inherit" />}
            {children}
            {trailingIcon && <Icon icon={trailingIcon} size={size === "sm" ? "xs" : "sm"} tone="inherit" />}
          </>
        )}
      </motion.button>
    );
  }
);

Button.displayName = "Button";
