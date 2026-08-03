import React, { useEffect } from "react";
import { AnimatePresence, motion, TargetAndTransition } from "framer-motion";
import { X } from "lucide-react";
import { Icon } from "../core/Icon";

export type SheetSide = "left" | "right" | "top" | "bottom";

export interface SheetProps {
  open: boolean;
  onClose: () => void;
  title?: string;
  description?: string;
  side?: SheetSide;
  children: React.ReactNode;
  className?: string;
}

const slideVariants: Record<SheetSide, { initial: TargetAndTransition; animate: TargetAndTransition; exit: TargetAndTransition; layoutStyle: string }> = {
  right: {
    initial: { x: "100%" },
    animate: { x: 0 },
    exit: { x: "100%" },
    layoutStyle: "right-0 top-0 bottom-0 w-[420px] max-w-full border-l",
  },
  left: {
    initial: { x: "-100%" },
    animate: { x: 0 },
    exit: { x: "-100%" },
    layoutStyle: "left-0 top-0 bottom-0 w-[320px] max-w-full border-r",
  },
  top: {
    initial: { y: "-100%" },
    animate: { y: 0 },
    exit: { y: "-100%" },
    layoutStyle: "top-0 left-0 right-0 h-[300px] border-b",
  },
  bottom: {
    initial: { y: "100%" },
    animate: { y: 0 },
    exit: { y: "100%" },
    layoutStyle: "bottom-0 left-0 right-0 h-[400px] border-t",
  },
};

export const Sheet: React.FC<SheetProps> = ({
  open,
  onClose,
  title,
  description,
  side = "right",
  children,
  className = "",
}) => {
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.key === "Escape" && open) onClose();
    };
    if (open) window.addEventListener("keydown", handleKeyDown);
    return () => window.removeEventListener("keydown", handleKeyDown);
  }, [open, onClose]);

  const config = slideVariants[side];

  return (
    <AnimatePresence>
      {open && (
        <div className="fixed inset-0 z-50">
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            onClick={onClose}
            className="fixed inset-0 bg-black/60 backdrop-blur-xs"
          />
          <motion.div
            initial={config.initial}
            animate={config.animate}
            exit={config.exit}
            transition={{ type: "spring", stiffness: 400, damping: 32 }}
            className={`fixed bg-[var(--surface-panel)] border-[var(--border-subtle)] shadow-2xl flex flex-col z-10 ${config.layoutStyle} ${className}`}
          >
            {(title || description) && (
              <div className="flex items-start justify-between p-4 border-b border-[var(--border-subtle)]">
                <div className="flex flex-col gap-0.5">
                  {title && <h2 className="text-sm font-bold text-[var(--text-primary)]">{title}</h2>}
                  {description && <p className="text-xs text-[var(--text-muted)]">{description}</p>}
                </div>
                <button
                  onClick={onClose}
                  className="p-1 rounded text-[var(--text-muted)] hover:text-[var(--text-primary)]"
                >
                  <Icon icon={X} size="sm" />
                </button>
              </div>
            )}
            <div className="p-4 flex-1 overflow-y-auto">{children}</div>
          </motion.div>
        </div>
      )}
    </AnimatePresence>
  );
};
