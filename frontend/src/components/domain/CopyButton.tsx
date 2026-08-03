import React, { useState } from "react";
import { Button, ButtonProps } from "../core/Button";
import { Copy, Check } from "lucide-react";

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

  const handleCopy = (e: React.MouseEvent<HTMLButtonElement>) => {
    e.stopPropagation();
    if (!valueToCopy) return;

    setCopied(true);
    if (onCopySuccess) {
      onCopySuccess(valueToCopy);
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
