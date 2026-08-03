import React from "react";

export interface FieldGroupProps {
  label?: string;
  description?: string;
  error?: string;
  required?: boolean;
  children: React.ReactNode;
  className?: string;
}

export const FieldGroup: React.FC<FieldGroupProps> = ({
  label,
  description,
  error,
  required = false,
  children,
  className = "",
}) => {
  return (
    <div className={`flex flex-col gap-1.5 w-full ${className}`}>
      {label && (
        <label className="text-xs font-semibold text-[var(--text-secondary)] flex items-center gap-1">
          {label}
          {required && <span className="text-[var(--danger)]">*</span>}
        </label>
      )}
      {children}
      {error ? (
        <span className="text-xs font-medium text-[var(--danger)]">{error}</span>
      ) : description ? (
        <span className="text-xs text-[var(--text-muted)]">{description}</span>
      ) : null}
    </div>
  );
};
