import React, { useState } from "react";
import { Button, ButtonProps } from "../core/Button";
import { Copy, Check } from "lucide-react";
import { useSettingsStore } from "../../stores/settings/useSettingsStore";
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

    try {
      await navigator.clipboard.writeText(valueToCopy);
    } catch (err) {
      console.error("Failed to copy", err);
    }

    setCopied(true);
    if (onCopySuccess) {
      onCopySuccess(valueToCopy);
    }

    const { clipboardAutoClearSeconds } = useSettingsStore.getState();
    if (clipboardAutoClearSeconds > 0) {
      setTimeout(async () => {
        try {
          const currentText = await navigator.clipboard.readText();
          // Only clear if the clipboard still contains what we copied
          if (currentText === valueToCopy) {
            await navigator.clipboard.writeText("");
          }
        } catch (e) {
          // ignore error if unable to read/write
        }
      }, clipboardAutoClearSeconds * 1000);
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
      {...props}
    >
      {copied ? "Copied!" : label}
    </Button>
  );
};
