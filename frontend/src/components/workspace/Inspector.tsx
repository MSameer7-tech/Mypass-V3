import React, { useState } from "react";
import { FaviconAvatar } from "../domain/FaviconAvatar";
import { IconButton } from "../core/IconButton";
import { Badge } from "../core/Badge";
import { Card } from "../core/Card";
import { CopyButton } from "../domain/CopyButton";
import { Eye, EyeOff, ExternalLink, Edit3, Trash2, Shield, Calendar, Key, Globe, Check, FileText } from "lucide-react";
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
        <div className="h-12 w-12 rounded-xl bg-[var(--surface-card)] border border-transparent flex items-center justify-center mb-3 shadow-xs">
          <Icon icon={Shield} size="md" tone="muted" />
        </div>
        <h3 className="text-sm font-bold text-[var(--text-primary)]">No Entry Selected</h3>
        <p className="text-xs text-[var(--text-muted)] max-w-xs mt-1 leading-relaxed">
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
    <div className="h-full w-full bg-[var(--background)] px-6 py-5 overflow-y-auto flex flex-col justify-between select-text">
      {/* Compact Content Container (Constrained 640px max width & tight 24px horizontal padding) */}
      <div className="flex flex-col gap-5 max-w-[640px] w-full mx-auto">
        {/* 1. Header Section (Compact 12x12 avatar, 20px title, 32px action buttons) */}
        <div className="flex items-start justify-between pb-5 border-b border-[var(--border-subtle)]">
          <div className="flex items-center gap-3.5">
            <FaviconAvatar title={entry.title} websiteUrl={entry.websiteUrl} size="md" className="h-12 w-12 rounded-xl text-lg font-bold shrink-0 shadow-sm bg-[var(--surface-card)] border-transparent" />
            <div className="flex flex-col gap-1">
              <div className="flex items-center gap-2.5">
                <h2 className="text-xl font-bold text-[var(--text-primary)] tracking-tight">{entry.title}</h2>
                <Badge variant="outline" className="text-[11px] bg-[var(--surface-card)] border-transparent text-[var(--text-muted)] px-2 py-0.5 rounded-md font-medium">{entry.category || "Passwords"}</Badge>
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

          <div className="flex items-center gap-1.5">
            {onEdit && (
              <IconButton icon={Edit3} label="Edit Entry" size="sm" variant="secondary" onClick={onEdit} className="h-8 w-8 rounded-lg bg-[var(--surface-card)] border-transparent hover:bg-[var(--surface-card-hover)]" />
            )}
            {onDelete && (
              <IconButton icon={Trash2} label="Delete Entry" size="sm" variant="destructive" onClick={onDelete} className="h-8 w-8 rounded-lg bg-red-950/40 border-transparent hover:bg-red-900/60 text-red-400" />
            )}
          </div>
        </div>

        {/* 2. CREDENTIALS Section (Compact 32px rows) */}
        <div className="flex flex-col gap-2">
          <div className="flex items-center gap-1.5 text-[var(--text-muted)]">
            <Icon icon={Key} size="xs" />
            <h4 className="text-[11px] font-bold uppercase tracking-wider">Credentials</h4>
          </div>

          <Card variant="default" className="flex flex-col gap-2 p-3.5 bg-[var(--surface-card)] border-transparent hover:bg-[var(--surface-card-hover)] transition-colors rounded-xl shadow-xs">
            {/* Username Row */}
            <div className="flex items-center justify-between h-8">
              <div className="flex flex-col gap-0.5 min-w-0">
                <span className="text-[11px] font-medium text-[var(--text-muted)]">Username / Email</span>
                <span className="text-sm font-semibold text-[var(--text-primary)] truncate">{entry.username || "—"}</span>
              </div>
              <CopyButton valueToCopy={entry.username || ""} label="" className="h-7 w-7 p-0 min-w-0" />
            </div>

            <div className="border-t border-[var(--border-subtle)]" />

            {/* Password Row */}
            <div className="flex items-center justify-between h-8">
              <div className="flex flex-col gap-0.5 min-w-0">
                <span className="text-[11px] font-medium text-[var(--text-muted)]">Password</span>
                <span className="text-sm font-mono font-semibold text-[var(--text-primary)] tracking-wider">
                  {showPassword ? entry.password || "••••••••••••" : "••••••••••••••••"}
                </span>
              </div>

              <div className="flex items-center gap-1 shrink-0">
                <IconButton
                  icon={showPassword ? EyeOff : Eye}
                  label={showPassword ? "Hide password" : "Reveal password"}
                  size="sm"
                  variant="ghost"
                  onClick={() => setShowPassword(!showPassword)}
                  className="h-7 w-7 text-[var(--text-muted)] hover:text-[var(--text-primary)]"
                />
                <CopyButton valueToCopy={entry.password || ""} label="" className="h-7 w-7 p-0 min-w-0" />
                {entry.websiteUrl && (
                  <IconButton
                    icon={Globe}
                    label="Open website"
                    size="sm"
                    variant="ghost"
                    onClick={handleOpenUrl}
                    className="h-7 w-7 text-[var(--text-muted)] hover:text-[var(--text-primary)]"
                  />
                )}
              </div>
            </div>
          </Card>
        </div>

        {/* 3. SECURITY ANALYSIS Section */}
        <div className="flex flex-col gap-2">
          <div className="flex items-center gap-1.5 text-[var(--text-muted)]">
            <Icon icon={Shield} size="xs" />
            <h4 className="text-[11px] font-bold uppercase tracking-wider">Security Analysis</h4>
          </div>

          <Card variant="default" className="flex flex-col gap-2.5 p-3.5 bg-[var(--surface-card)] border-transparent hover:bg-[var(--surface-card-hover)] transition-colors rounded-xl shadow-xs">
            <div className="flex items-center justify-between">
              <span className="text-xs font-semibold text-[var(--text-secondary)]">Password Strength</span>
              <div className="flex items-center gap-1 px-2 py-0.5 rounded-md bg-emerald-950/60 border border-emerald-800/60 text-[10px] font-bold text-emerald-400">
                <Icon icon={Check} size="xs" className="text-emerald-400" />
                <span>Very Strong</span>
              </div>
            </div>

            <div className="flex items-center gap-1.5 h-1.5 w-full mt-0.5">
              <div className="flex-1 h-full rounded-full bg-emerald-500" />
              <div className="flex-1 h-full rounded-full bg-emerald-500" />
              <div className="flex-1 h-full rounded-full bg-emerald-500" />
              <div className="flex-1 h-full rounded-full bg-emerald-500" />
              <div className="flex-1 h-full rounded-full bg-emerald-500" />
            </div>
          </Card>
        </div>

        {/* 4. SECURE NOTES Section */}
        {entry.notes && (
          <div className="flex flex-col gap-2">
            <div className="flex items-center gap-1.5 text-[var(--text-muted)]">
              <Icon icon={FileText} size="xs" />
              <h4 className="text-[11px] font-bold uppercase tracking-wider">Secure Notes</h4>
            </div>

            <Card variant="default" className="flex items-center justify-between p-3.5 bg-[var(--surface-card)] border-transparent hover:bg-[var(--surface-card-hover)] transition-colors rounded-xl shadow-xs text-xs font-medium text-[var(--text-secondary)]">
              <span className="leading-relaxed">{entry.notes}</span>
              {onEdit && (
                <IconButton icon={Edit3} label="Edit Notes" size="sm" variant="ghost" onClick={onEdit} className="h-7 w-7 text-[var(--text-muted)] hover:text-[var(--text-primary)] shrink-0" />
              )}
            </Card>
          </div>
        )}

        {/* 5. METADATA Section - Compact Single Grouped Panel */}
        <div className="flex flex-col gap-2">
          <div className="flex items-center gap-1.5 text-[var(--text-muted)]">
            <Icon icon={Calendar} size="xs" />
            <h4 className="text-[11px] font-bold uppercase tracking-wider">Metadata</h4>
          </div>

          <Card variant="default" className="grid grid-cols-3 divide-x divide-[var(--border-subtle)] bg-[var(--surface-card)] border-transparent hover:bg-[var(--surface-card-hover)] transition-colors rounded-xl shadow-xs p-3.5 text-xs">
            <div className="flex flex-col pr-3">
              <span className="text-[10px] text-[var(--text-muted)] font-medium">Updated</span>
              <span className="font-semibold text-[var(--text-primary)] mt-0.5 truncate">{entry.updatedAt || "Just now"}</span>
            </div>
            <div className="flex flex-col px-3">
              <span className="text-[10px] text-[var(--text-muted)] font-medium">Created</span>
              <span className="font-semibold text-[var(--text-primary)] mt-0.5 truncate">Jan 12, 2024</span>
            </div>
            <div className="flex flex-col pl-3">
              <span className="text-[10px] text-[var(--text-muted)] font-medium">Record</span>
              <span className="font-semibold text-[var(--text-primary)] font-mono mt-0.5 truncate">#00{entry.id}</span>
            </div>
          </Card>
        </div>
      </div>

      {/* Footer Encryption Badge */}
      <div className="flex items-center justify-center gap-2 pt-4 text-[10px] font-medium text-[var(--text-muted)] border-t border-[var(--border-subtle)] mt-5">
        <Icon icon={Shield} size="xs" tone="muted" />
        <span>AES-256-GCM • Argon2id • Vault Updated 2 min ago</span>
      </div>
    </div>
  );
};
