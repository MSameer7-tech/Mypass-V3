import React from "react";
import { Dialog, DialogProps } from "./Dialog";
import { Button } from "../core/Button";
import { AlertTriangle } from "lucide-react";
import { Icon } from "../core/Icon";

export interface ConfirmDialogProps extends Omit<DialogProps, "children" | "footer"> {
  confirmLabel?: string;
  cancelLabel?: string;
  isDestructive?: boolean;
  isLoading?: boolean;
  onConfirm: () => void;
}

export const ConfirmDialog: React.FC<ConfirmDialogProps> = ({
  open,
  onClose,
  title = "Confirm Action",
  description = "Are you sure you want to proceed? This action cannot be undone.",
  confirmLabel = "Confirm",
  cancelLabel = "Cancel",
  isDestructive = true,
  isLoading = false,
  onConfirm,
  size = "sm",
  ...props
}) => {
  const footer = (
    <>
      <Button variant="ghost" size="sm" onClick={onClose} disabled={isLoading}>
        {cancelLabel}
      </Button>
      <Button
        variant={isDestructive ? "destructive" : "primary"}
        size="sm"
        onClick={onConfirm}
        isLoading={isLoading}
      >
        {confirmLabel}
      </Button>
    </>
  );

  return (
    <Dialog open={open} onClose={onClose} size={size} footer={footer} {...props}>
      <div className="flex items-start gap-4">
        <div className="p-3 rounded-xl bg-[var(--danger-surface)] border border-red-900/30 shrink-0">
          <Icon icon={AlertTriangle} size="md" tone="danger" />
        </div>
        <div className="flex flex-col gap-1">
          <h3 className="text-sm font-bold text-[var(--text-primary)]">{title}</h3>
          <p className="text-xs text-[var(--text-muted)] leading-relaxed">{description}</p>
        </div>
      </div>
    </Dialog>
  );
};
