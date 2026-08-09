import React, { useEffect } from "react";
import { AnimatePresence, motion } from "framer-motion";
import { X } from "lucide-react";
import { Icon } from "../core/Icon";
import { MOTION_TOKENS } from "../../constants/motion";

export type DialogSize = "sm" | "md" | "lg" | "xl";

export interface DialogProps {
  open: boolean;
  onClose: () => void;
  title?: string;
  description?: string;
  footer?: React.ReactNode;
  size?: DialogSize;
  children: React.ReactNode;
  className?: string;
}

const sizeStyles: Record<DialogSize, string> = {
  sm: "max-w-sm",
  md: "max-w-md",
  lg: "max-w-lg",
  xl: "max-w-xl",
};

export const Dialog: React.FC<DialogProps> = ({
  open,
  onClose,
  title,
  description,
  footer,
  size = "md",
  children,
  className = "",
}) => {
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.key === "Escape" && open) {
        onClose();
      }
    };
    if (open) {
      window.addEventListener("keydown", handleKeyDown);
    }
    return () => window.removeEventListener("keydown", handleKeyDown);
  }, [open, onClose]);

  return (
    <AnimatePresence>
      {open && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4">
          {/* Backdrop */}
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            transition={{ duration: MOTION_TOKENS.duration.hover }}
            onClick={onClose}
            className="fixed inset-0 bg-black/60 backdrop-blur-xs"
          />

          {/* Dialog Window */}
          <motion.div
            initial={{ opacity: 0, scale: 0.97, y: 4 }}
            animate={{ opacity: 1, scale: 1, y: 0 }}
            exit={{ opacity: 0, scale: 0.97, y: 4 }}
            transition={{ duration: MOTION_TOKENS.duration.transition, ease: MOTION_TOKENS.ease.out }}
            className={`relative w-full bg-[var(--surface-panel)] border border-[var(--border-subtle)] rounded-2xl shadow-2xl overflow-hidden z-10 ${sizeStyles[size]} ${className}`}
            role="dialog"
            aria-modal="true"
          >
            {/* Header */}
            {(title || description) && (
              <div className="flex items-start justify-between p-6 pb-4 border-b border-[var(--border-subtle)]">
                <div className="flex flex-col gap-0.5 pr-6">
                  {title && <h2 className="text-base font-bold text-[var(--text-primary)]">{title}</h2>}
                  {description && <p className="text-xs text-[var(--text-muted)]">{description}</p>}
                </div>
                <button
                  type="button"
                  onClick={onClose}
                  className="p-1 rounded-lg text-[var(--text-muted)] hover:text-[var(--text-primary)] hover:bg-[var(--surface-card-hover)] transition-colors"
                  aria-label="Close dialog"
                >
                  <Icon icon={X} size="sm" />
                </button>
              </div>
            )}

            {/* Body */}
            <div className="p-6 overflow-y-auto max-h-[75vh]">{children}</div>

            {/* Footer */}
            {footer && (
              <div className="flex items-center justify-end gap-2 p-6 pt-4 bg-[var(--surface-card)] border-t border-[var(--border-subtle)]">
                {footer}
              </div>
            )}
          </motion.div>
        </div>
      )}
    </AnimatePresence>
  );
};
