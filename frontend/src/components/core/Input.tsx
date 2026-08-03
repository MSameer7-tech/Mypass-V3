import React, { useState } from "react";
import { Icon, IconProps } from "./Icon";
import { Eye, EyeOff, Search, X } from "lucide-react";

export interface InputProps extends React.InputHTMLAttributes<HTMLInputElement> {
  label?: string;
  error?: string;
  helperText?: string;
  leadingIcon?: IconProps["icon"];
  trailingIcon?: IconProps["icon"];
  onClear?: () => void;
  shortcutBadge?: string;
}

export const Input = React.forwardRef<HTMLInputElement, InputProps>(
  ({ label, error, helperText, leadingIcon, trailingIcon, onClear, shortcutBadge, className = "", id, ...props }, ref) => {
    const inputId = id || (label ? label.toLowerCase().replace(/\s+/g, "-") : undefined);

    return (
      <div className="flex flex-col gap-1.5 w-full">
        {label && (
          <label htmlFor={inputId} className="text-xs font-semibold text-[var(--text-secondary)]">
            {label}
          </label>
        )}
        <div className="relative flex items-center w-full">
          {leadingIcon && (
            <div className="absolute left-3.5 pointer-events-none flex items-center">
              <Icon icon={leadingIcon} size="sm" tone="muted" />
            </div>
          )}
          <input
            id={inputId}
            ref={ref}
            className={`w-full h-10 px-3.5 bg-[var(--surface-card)] text-[var(--text-primary)] text-sm rounded-[14px] border border-transparent hover:border-[var(--border-subtle)] placeholder:text-[var(--text-muted)] focus:outline-none focus:border-[var(--border-focus)] focus:bg-[var(--surface-card-hover)] transition-all duration-150 disabled:opacity-50 disabled:cursor-not-allowed ${
              leadingIcon ? "pl-10" : ""
            } ${trailingIcon || onClear || shortcutBadge ? "pr-12" : ""} ${
              error ? "border-[var(--danger)] focus:border-[var(--danger)] focus:ring-[var(--danger)]" : ""
            } ${className}`}
            {...props}
          />
          {onClear && props.value ? (
            <button
              type="button"
              onClick={onClear}
              className="absolute right-3.5 p-1 rounded-md text-[var(--text-muted)] hover:text-[var(--text-primary)] hover:bg-white/5 focus:outline-none transition-colors"
            >
              <Icon icon={X} size="xs" />
            </button>
          ) : shortcutBadge ? (
            <div className="absolute right-3.5 pointer-events-none flex items-center">
              <kbd className="px-1.5 py-0.5 text-[10px] font-mono font-medium rounded-md bg-white/5 text-[var(--text-muted)] border border-[var(--border-subtle)]">
                {shortcutBadge}
              </kbd>
            </div>
          ) : !onClear && trailingIcon ? (
            <div className="absolute right-3.5 pointer-events-none flex items-center">
              <Icon icon={trailingIcon} size="sm" tone="muted" />
            </div>
          ) : null}
        </div>
        {error ? (
          <span className="text-xs text-[var(--danger)] font-medium">{error}</span>
        ) : helperText ? (
          <span className="text-xs text-[var(--text-muted)]">{helperText}</span>
        ) : null}
      </div>
    );
  }
);

Input.displayName = "Input";

export const PasswordInput = React.forwardRef<HTMLInputElement, InputProps>(
  (props, ref) => {
    const [showPassword, setShowPassword] = useState(false);

    return (
      <div className="relative w-full">
        <Input
          ref={ref}
          type={showPassword ? "text" : "password"}
          {...props}
        />
        <button
          type="button"
          onClick={() => setShowPassword(!showPassword)}
          className="absolute right-3.5 top-8 -translate-y-1/2 p-1 text-[var(--text-muted)] hover:text-[var(--text-primary)] focus:outline-none transition-colors"
          tabIndex={-1}
          aria-label={showPassword ? "Hide password" : "Show password"}
        >
          <Icon icon={showPassword ? EyeOff : Eye} size="sm" tone="muted" />
        </button>
      </div>
    );
  }
);

PasswordInput.displayName = "PasswordInput";

export const SearchInput = React.forwardRef<HTMLInputElement, InputProps>(
  (props, ref) => {
    return (
      <Input
        ref={ref}
        type="search"
        leadingIcon={Search}
        placeholder="Search vault..."
        shortcutBadge="⌘F"
        {...props}
      />
    );
  }
);

SearchInput.displayName = "SearchInput";
