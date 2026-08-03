import React, { useState } from "react";
import { FaviconAvatar } from "../domain/FaviconAvatar";
import { SecurityBadge } from "../domain/SecurityBadge";
import { PasswordStrength } from "../domain/PasswordStrength";
import { IconButton } from "../core/IconButton";
import { Badge } from "../core/Badge";
import { Card } from "../core/Card";
import { CopyButton } from "../domain/CopyButton";
import { Eye, EyeOff, ExternalLink, Edit3, Trash2, Shield, Calendar, Key, Globe } from "lucide-react";
import { Icon } from "../core/Icon";
import { MockVaultEntry } from "../../mocks/vault";

export interface InspectorProps {
  entry?: MockVaultEntry | null;
  onEdit?: () => void;
  onDelete?: () => void;
}

export const Inspector: React.FC<InspectorProps> = ({ entry, onEdit, onDelete }) => {
  const [showPassword, setShowPassword] = useState(false);

  if (!entry) {
    return (
      <div className="h-full w-full flex flex-col items-center justify-center p-8 text-center bg-[var(--background)] select-none">
        <div className="h-16 w-16 rounded-2xl bg-[var(--surface-card)] border border-[var(--border-subtle)] flex items-center justify-center mb-4 shadow-sm">
          <Icon icon={Shield} size="lg" tone="muted" />
        </div>
        <h3 className="text-base font-bold text-[var(--text-primary)]">No Entry Selected</h3>
        <p className="text-xs text-[var(--text-muted)] max-w-xs mt-1">
          Select an item from the vault list to view credentials, security health, and metadata.
        </p>
      </div>
    );
  }

  const handleOpenUrl = () => {
    if (entry.websiteUrl) {
      window.open(entry.websiteUrl, "_blank", "noopener,noreferrer");
    }
  };

  return (
    <div className="h-full w-full bg-[var(--background)] p-8 overflow-y-auto flex flex-col gap-7 select-text border-l border-[var(--border-subtle)]">
      {/* 1. Header Section */}
      <div className="flex items-start justify-between border-b border-[var(--border-subtle)] pb-6">
        <div className="flex items-center gap-4">
          <FaviconAvatar title={entry.title} websiteUrl={entry.websiteUrl} size="lg" className="h-14 w-14 rounded-2xl text-xl font-bold shrink-0 shadow-md" />
          <div className="flex flex-col gap-1">
            <div className="flex items-center gap-2">
              <h2 className="text-xl font-bold text-[var(--text-primary)] tracking-tight">{entry.title}</h2>
              <Badge variant="outline">{entry.category || "Passwords"}</Badge>
            </div>
            {entry.websiteUrl ? (
              <a
                href={entry.websiteUrl}
                target="_blank"
                rel="noreferrer"
                className="text-xs font-medium text-[var(--accent)] hover:underline flex items-center gap-1 w-fit"
              >
                <span>{entry.websiteUrl}</span>
                <Icon icon={ExternalLink} size="xs" tone="accent" />
              </a>
            ) : (
              <span className="text-xs text-[var(--text-muted)]">No website URL</span>
            )}
          </div>
        </div>

        <div className="flex items-center gap-2">
          {onEdit && (
            <IconButton icon={Edit3} label="Edit Entry" size="sm" variant="secondary" onClick={onEdit} />
          )}
          {onDelete && (
            <IconButton icon={Trash2} label="Delete Entry" size="sm" variant="destructive" onClick={onDelete} />
          )}
        </div>
      </div>

      {/* 2. Credentials Section */}
      <div className="flex flex-col gap-3">
        <h4 className="text-xs font-bold text-[var(--text-muted)] uppercase tracking-wider">Credentials</h4>

        <Card variant="default" className="flex flex-col gap-3 p-4">
          {/* Username Field */}
          <div className="flex items-center justify-between">
            <div className="flex flex-col gap-0.5 min-w-0">
              <span className="text-[11px] font-medium text-[var(--text-muted)]">Username / Email</span>
              <span className="text-sm font-semibold text-[var(--text-primary)] truncate">{entry.username || "—"}</span>
            </div>
            <CopyButton valueToCopy={entry.username || ""} label="Username" />
          </div>

          <div className="border-t border-[var(--border-subtle)]" />

          {/* Password Field */}
          <div className="flex items-center justify-between">
            <div className="flex flex-col gap-0.5 min-w-0">
              <span className="text-[11px] font-medium text-[var(--text-muted)]">Password</span>
              <span className="text-sm font-mono font-semibold text-[var(--text-primary)] tracking-wide">
                {showPassword ? entry.password || "••••••••••••" : "••••••••••••••••"}
              </span>
            </div>

            <div className="flex items-center gap-1.5 shrink-0">
              <IconButton
                icon={showPassword ? EyeOff : Eye}
                label={showPassword ? "Hide password" : "Reveal password"}
                size="sm"
                variant="ghost"
                onClick={() => setShowPassword(!showPassword)}
              />
              <CopyButton valueToCopy={entry.password || ""} label="Password" />
              {entry.websiteUrl && (
                <IconButton
                  icon={Globe}
                  label="Open website"
                  size="sm"
                  variant="ghost"
                  onClick={handleOpenUrl}
                />
              )}
            </div>
          </div>
        </Card>
      </div>

      {/* 3. Security & Health Section */}
      <div className="flex flex-col gap-3">
        <h4 className="text-xs font-bold text-[var(--text-muted)] uppercase tracking-wider">Security Analysis</h4>
        <Card variant="default" className="flex flex-col gap-3 p-4">
          <div className="flex items-center justify-between">
            <span className="text-xs text-[var(--text-secondary)]">Security Rating</span>
            <SecurityBadge status={entry.securityStatus} />
          </div>
          <PasswordStrength score={entry.strengthScore} />
        </Card>
      </div>

      {/* 4. Encrypted Notes Section */}
      {entry.notes && (
        <div className="flex flex-col gap-3">
          <h4 className="text-xs font-bold text-[var(--text-muted)] uppercase tracking-wider">Secure Notes</h4>
          <Card variant="default" className="p-4 text-xs leading-relaxed text-[var(--text-secondary)] whitespace-pre-wrap font-mono">
            {entry.notes}
          </Card>
        </div>
      )}

      {/* 5. Metadata Section */}
      <div className="flex flex-col gap-3">
        <h4 className="text-xs font-bold text-[var(--text-muted)] uppercase tracking-wider">Metadata</h4>
        <div className="grid grid-cols-2 gap-3 text-xs">
          <div className="p-3 bg-[var(--surface-card)] border border-[var(--border-subtle)] rounded-xl flex items-center gap-2.5">
            <Icon icon={Calendar} size="xs" tone="muted" />
            <div className="flex flex-col">
              <span className="text-[10px] text-[var(--text-muted)]">Last Updated</span>
              <span className="font-semibold text-[var(--text-primary)]">{entry.updatedAt}</span>
            </div>
          </div>
          <div className="p-3 bg-[var(--surface-card)] border border-[var(--border-subtle)] rounded-xl flex items-center gap-2.5">
            <Icon icon={Key} size="xs" tone="muted" />
            <div className="flex flex-col">
              <span className="text-[10px] text-[var(--text-muted)]">Record ID</span>
              <span className="font-semibold text-[var(--text-primary)] font-mono">#00{entry.id}</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};
