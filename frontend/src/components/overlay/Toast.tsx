import React, { useEffect } from "react";
import { motion } from "framer-motion";
import { CheckCircle2, AlertCircle, AlertTriangle, Info, X } from "lucide-react";
import { Icon, IconProps } from "../core/Icon";

export type ToastVariant = "success" | "error" | "warning" | "info";

export interface ToastMessage {
  id: string;
  variant?: ToastVariant;
  title: string;
  description?: string;
  actionLabel?: string;
  onAction?: () => void;
  duration?: number;
}

export interface ToastProps {
  toast: ToastMessage;
  onDismiss: (id: string) => void;
}

const variantConfig: Record<ToastVariant, { icon: IconProps["icon"]; tone: IconProps["tone"]; border: string }> = {
  success: { icon: CheckCircle2, tone: "success", border: "border-emerald-900/50" },
  error: { icon: AlertCircle, tone: "danger", border: "border-red-900/50" },
  warning: { icon: AlertTriangle, tone: "warning", border: "border-amber-900/50" },
  info: { icon: Info, tone: "accent", border: "border-blue-900/50" },
};

export const Toast: React.FC<ToastProps> = ({ toast, onDismiss }) => {
  const { id, variant = "info", title, description, actionLabel, onAction, duration = 4000 } = toast;

  useEffect(() => {
    if (duration <= 0) return;
    const timer = setTimeout(() => onDismiss(id), duration);
    return () => clearTimeout(timer);
  }, [id, duration, onDismiss]);

  const config = variantConfig[variant];

  return (
    <motion.div
      initial={{ opacity: 0, y: 12, scale: 0.95 }}
      animate={{ opacity: 1, y: 0, scale: 1 }}
      exit={{ opacity: 0, y: 12, scale: 0.95 }}
      transition={{ duration: 0.15 }}
      className={`flex items-start gap-3 w-[340px] p-3.5 bg-[var(--surface-card)] text-[var(--text-primary)] border rounded-xl shadow-xl z-50 ${config.border}`}
    >
      <div className="mt-0.5 shrink-0">
        <Icon icon={config.icon} size="sm" tone={config.tone} />
      </div>
      <div className="flex flex-col gap-0.5 flex-1 min-w-0">
        <span className="text-xs font-bold truncate">{title}</span>
        {description && <span className="text-[11px] text-[var(--text-muted)] leading-normal">{description}</span>}
        {actionLabel && onAction && (
          <button
            onClick={() => {
              onAction();
              onDismiss(id);
            }}
            className="self-start text-[11px] font-bold text-[var(--accent)] hover:underline mt-1"
          >
            {actionLabel}
          </button>
        )}
      </div>
      <button
        onClick={() => onDismiss(id)}
        className="p-0.5 text-[var(--text-muted)] hover:text-[var(--text-primary)] shrink-0"
      >
        <Icon icon={X} size="xs" />
      </button>
    </motion.div>
  );
};
