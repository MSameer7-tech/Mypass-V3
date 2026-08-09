import React, { useState } from "react";
import { Button, ButtonProps } from "../core/Button";
import { Copy, Check } from "lucide-react";
import { useSettingsStore } from "../../stores/settings/useSettingsStore";
import { useClipboardStore } from "../../stores/clipboard/useClipboardStore";
export interface CopyButtonProps extends Omit<ButtonProps, "onClick"> {
  valueToCopy: string;
  onCopySuccess?: (value: string) => void;
  label?: string;
}

export const CopyButton: React.FC<CopyButtonProps> = ({
  valueToCopy,
  onCopySuccess,
  label = "Copy",
  variant = "ghost",
  size = "sm",
  className = "",
  ...props
}) => {
  const [copied, setCopied] = useState(false);

  const handleCopy = async (e: React.MouseEvent<HTMLButtonElement>) => {
    e.stopPropagation();
    if (!valueToCopy) return;

    const { clipboardAutoClearSeconds } = useSettingsStore.getState();
    const success = await useClipboardStore.getState().copy(valueToCopy, clipboardAutoClearSeconds);

    if (success) {
      setCopied(true);
      if (onCopySuccess) {
        onCopySuccess(valueToCopy);
      }
    }

    setTimeout(() => {
      setCopied(false);
    }, 2000);
  };

  return (
    <Button
      variant={copied ? "primary" : variant}
      size={size}
      onClick={handleCopy}
      leadingIcon={copied ? Check : Copy}
      className={`transition-all duration-100 ${className}`}
      aria-label={copied ? "Copied" : (label || "Copy to clipboard")}
      aria-live="polite"
      {...props}
    >
      {copied && label ? "Copied!" : label}
    </Button>
  );
};
