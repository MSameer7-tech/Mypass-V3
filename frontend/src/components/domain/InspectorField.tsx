import React, { useState } from "react";
import { CopyButton } from "./CopyButton";
import { Button } from "../core/Button";
import { Eye, EyeOff, ExternalLink } from "lucide-react";
import { Icon } from "../core/Icon";

export interface InspectorFieldProps {
  label: string;
  value: string;
  isSensitive?: boolean;
  copyable?: boolean;
  revealable?: boolean;
  actionUrl?: string;
  onCopySuccess?: (val: string) => void;
  className?: string;
}

export const InspectorField: React.FC<InspectorFieldProps> = ({
  label,
  value,
  isSensitive = false,
  copyable = true,
  revealable = false,
  actionUrl,
  onCopySuccess,
  className = "",
}) => {
  const [revealed, setRevealed] = useState(!isSensitive);

  const displayValue = isSensitive && !revealed ? "••••••••••••••••" : value || "—";

  return (
    <div className={`flex flex-col gap-1.5 p-3.5 bg-[var(--surface-card)] border border-[var(--border-subtle)] rounded-xl ${className}`}>
      <div className="flex items-center justify-between">
        <span className="text-xs font-semibold text-[var(--text-muted)] tracking-wider uppercase">{label}</span>
        <div className="flex items-center gap-1">
          {actionUrl && (
            <a
              href={actionUrl}
              target="_blank"
              rel="noreferrer"
              className="inline-flex items-center gap-1 text-xs text-[var(--accent)] hover:underline px-2 py-1 rounded"
            >
              Open <Icon icon={ExternalLink} size="xs" tone="accent" />
            </a>
          )}
          {revealable && (
            <Button
              variant="ghost"
              size="sm"
              onClick={() => setRevealed(!revealed)}
              leadingIcon={revealed ? EyeOff : Eye}
              className="text-xs text-[var(--text-secondary)]"
            >
              {revealed ? "Hide" : "Reveal"}
            </Button>
          )}
          {copyable && value && (
            <CopyButton valueToCopy={value} onCopySuccess={onCopySuccess} size="sm" />
          )}
        </div>
      </div>
      <div className="text-sm font-medium font-mono text-[var(--text-primary)] break-all select-text">
        {displayValue}
      </div>
    </div>
  );
};
