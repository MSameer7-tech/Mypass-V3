import React, { useState } from "react";
import { FaviconAvatar } from "../domain/FaviconAvatar";
import { IconButton } from "../core/IconButton";
import { Badge } from "../core/Badge";
import { Card } from "../core/Card";
import { CopyButton } from "../domain/CopyButton";
import { Eye, EyeOff, ExternalLink, Edit3, Trash2, Shield, Calendar, Key, Globe, Check } from "lucide-react";
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
    <div className="h-full w-full bg-[var(--background)] p-8 overflow-y-auto flex flex-col justify-between select-text border-l border-[var(--border-subtle)]">
      <div className="flex flex-col gap-7">
        {/* 1. Header Section */}
        <div className="flex items-start justify-between border-b border-[var(--border-subtle)] pb-6">
          <div className="flex items-center gap-4">
            <FaviconAvatar title={entry.title} websiteUrl={entry.websiteUrl} size="lg" className="h-16 w-16 rounded-2xl text-2xl font-bold shrink-0 shadow-md bg-[var(--surface-card)] border border-[var(--border-subtle)]" />
            <div className="flex flex-col gap-1">
              <div className="flex items-center gap-2.5">
                <h2 className="text-2xl font-bold text-[var(--text-primary)] tracking-tight">{entry.title}</h2>
                <Badge variant="outline" className="text-xs bg-[var(--surface-card)] border-[var(--border-subtle)] text-[var(--text-muted)] px-2.5 py-0.5">{entry.category || "Passwords"}</Badge>
              </div>
              {entry.websiteUrl ? (
                <a
                  href={entry.websiteUrl}
                  target="_blank"
                  rel="noreferrer"
                  className="text-xs font-medium text-[var(--accent)] hover:underline flex items-center gap-1 w-fit mt-0.5"
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
              <IconButton icon={Edit3} label="Edit Entry" size="sm" variant="secondary" onClick={onEdit} className="h-9 w-9 rounded-xl bg-[var(--surface-card)] border border-[var(--border-subtle)] hover:bg-[var(--surface-card-hover)]" />
            )}
            {onDelete && (
              <IconButton icon={Trash2} label="Delete Entry" size="sm" variant="destructive" onClick={onDelete} className="h-9 w-9 rounded-xl bg-red-950/40 border border-red-800/40 hover:bg-red-900/60 text-red-400" />
            )}
          </div>
        </div>

        {/* 2. CREDENTIALS Section */}
        <div className="flex flex-col gap-3">
          <h4 className="text-xs font-bold text-[var(--text-muted)] uppercase tracking-wider">CREDENTIALS</h4>

          <Card variant="default" className="flex flex-col gap-3 p-4 bg-[var(--surface-card)] border border-[var(--border-subtle)] rounded-xl">
            {/* Username Field */}
            <div className="flex items-center justify-between">
              <div className="flex flex-col gap-0.5 min-w-0">
                <span className="text-[11px] font-medium text-[var(--text-muted)]">Username / Email</span>
                <span className="text-sm font-semibold text-[var(--text-primary)] truncate">{entry.username || "—"}</span>
              </div>
              <CopyButton valueToCopy={entry.username || ""} label="" className="h-8 w-8 p-0 min-w-0" />
            </div>

            <div className="border-t border-[var(--border-subtle)]" />

            {/* Password Field */}
            <div className="flex items-center justify-between">
              <div className="flex flex-col gap-0.5 min-w-0">
                <span className="text-[11px] font-medium text-[var(--text-muted)]">Password</span>
                <span className="text-sm font-mono font-semibold text-[var(--text-primary)] tracking-wider">
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
                  className="h-8 w-8 text-[var(--text-muted)] hover:text-[var(--text-primary)]"
                />
                <CopyButton valueToCopy={entry.password || ""} label="" className="h-8 w-8 p-0 min-w-0" />
                {entry.websiteUrl && (
                  <IconButton
                    icon={Globe}
                    label="Open website"
                    size="sm"
                    variant="ghost"
                    onClick={handleOpenUrl}
                    className="h-8 w-8 text-[var(--text-muted)] hover:text-[var(--text-primary)]"
                  />
                )}
              </div>
            </div>
          </Card>
        </div>

        {/* 3. SECURITY ANALYSIS Section */}
        <div className="flex flex-col gap-3">
          <h4 className="text-xs font-bold text-[var(--text-muted)] uppercase tracking-wider">SECURITY ANALYSIS</h4>
          <Card variant="default" className="flex flex-col gap-3 p-4 bg-[var(--surface-card)] border border-[var(--border-subtle)] rounded-xl">
            <div className="flex items-center justify-between">
              <span className="text-xs font-semibold text-[var(--text-secondary)]">Password Strength</span>
              <div className="flex items-center gap-1 px-2.5 py-0.5 rounded-full bg-emerald-950/60 border border-emerald-800/60 text-[11px] font-bold text-emerald-400">
                <Icon icon={Check} size="xs" className="text-emerald-400" />
                <span>Very Strong</span>
              </div>
            </div>

            {/* Segmented Strength Bar */}
            <div className="flex items-center gap-1.5 h-2 w-full mt-1">
              <div className="flex-1 h-full rounded-full bg-emerald-500" />
              <div className="flex-1 h-full rounded-full bg-emerald-500" />
              <div className="flex-1 h-full rounded-full bg-emerald-500" />
              <div className="flex-1 h-full rounded-full bg-emerald-500" />
              <div className="flex-1 h-full rounded-full bg-emerald-500" />
            </div>
          </Card>
        </div>

        {/* 4. SECURE NOTES Section */}
        <div className="flex flex-col gap-3">
          <h4 className="text-xs font-bold text-[var(--text-muted)] uppercase tracking-wider">SECURE NOTES</h4>
          <Card variant="default" className="flex items-center justify-between p-4 bg-[var(--surface-card)] border border-[var(--border-subtle)] rounded-xl text-xs font-medium text-[var(--text-secondary)]">
            <span>{entry.notes || "Main developer GitHub account."}</span>
            {onEdit && (
              <IconButton icon={Edit3} label="Edit Notes" size="sm" variant="ghost" onClick={onEdit} className="h-7 w-7 text-[var(--text-muted)] hover:text-[var(--text-primary)] shrink-0" />
            )}
          </Card>
        </div>

        {/* 5. METADATA Section */}
        <div className="flex flex-col gap-3">
          <h4 className="text-xs font-bold text-[var(--text-muted)] uppercase tracking-wider">METADATA</h4>
          <div className="grid grid-cols-3 gap-3 text-xs">
            <div className="p-3.5 bg-[var(--surface-card)] border border-[var(--border-subtle)] rounded-xl flex items-center gap-3">
              <Icon icon={Calendar} size="sm" tone="muted" />
              <div className="flex flex-col">
                <span className="text-[10px] text-[var(--text-muted)] font-medium">Last Updated</span>
                <span className="font-semibold text-[var(--text-primary)] mt-0.5">{entry.updatedAt || "Just now"}</span>
              </div>
            </div>
            <div className="p-3.5 bg-[var(--surface-card)] border border-[var(--border-subtle)] rounded-xl flex items-center gap-3">
              <Icon icon={Calendar} size="sm" tone="muted" />
              <div className="flex flex-col">
                <span className="text-[10px] text-[var(--text-muted)] font-medium">Created</span>
                <span className="font-semibold text-[var(--text-primary)] mt-0.5">Jan 12, 2024</span>
              </div>
            </div>
            <div className="p-3.5 bg-[var(--surface-card)] border border-[var(--border-subtle)] rounded-xl flex items-center gap-3">
              <Icon icon={Key} size="sm" tone="muted" />
              <div className="flex flex-col">
                <span className="text-[10px] text-[var(--text-muted)] font-medium">Record ID</span>
                <span className="font-semibold text-[var(--text-primary)] font-mono mt-0.5">#00{entry.id}</span>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Footer Encryption Badge */}
      <div className="flex items-center justify-center gap-2 pt-6 text-[11px] font-medium text-[var(--text-muted)] border-t border-[var(--border-subtle)]">
        <Icon icon={Shield} size="xs" tone="muted" />
        <span>Encrypted with AES-256-GCM & Argon2id</span>
      </div>
    </div>
  );
};
