import React, { useState } from "react";
import { FaviconAvatar } from "../domain/FaviconAvatar";
import { IconButton } from "../core/IconButton";
import { Badge } from "../core/Badge";
import { Card } from "../core/Card";
import { CopyButton } from "../domain/CopyButton";
import { SearchInput } from "../core/Input";
import { Eye, EyeOff, ExternalLink, Edit3, Trash2, Shield, Calendar, Key, FileText, Settings, Lock, Star, Check } from "lucide-react";
import { Icon } from "../core/Icon";
import { MockVaultEntry } from "../../mocks/vault";
import { useSearchStore } from "../../stores/search/useSearchStore";

export interface InspectorProps {
  entry?: MockVaultEntry | null;
  onEdit?: () => void;
  onDelete?: () => void;
  onToggleFavorite?: () => void;
  onOpenSettings?: () => void;
  onLockVault?: () => void;
}

export const Inspector: React.FC<InspectorProps> = ({
  entry,
  onEdit,
  onDelete,
  onToggleFavorite,
  onOpenSettings,
  onLockVault,
}) => {
  const [showPassword, setShowPassword] = useState(false);
  const searchQuery = useSearchStore((s) => s.query);
  const setSearchQuery = useSearchStore((s) => s.setSearchQuery);

  const getPasswordStrength = (password?: string) => {
    if (!password) return { score: 0, label: "None", color: "var(--text-muted)", bg: "var(--surface-card-hover)" };
    const len = password.length;
    if (len < 6) return { score: 1, label: "Very Weak", color: "var(--danger)", bg: "var(--danger-surface)" };
    if (len < 10) return { score: 2, label: "Weak", color: "var(--warning)", bg: "var(--warning-surface)" };
    if (len < 14) return { score: 3, label: "Good", color: "var(--accent)", bg: "var(--surface-elevated)" };
    if (len < 18) return { score: 4, label: "Strong", color: "var(--success)", bg: "var(--success-surface)" };
    return { score: 5, label: "Very Strong", color: "var(--success)", bg: "var(--success-surface)" };
  };

  const strength = entry ? getPasswordStrength(entry.password) : getPasswordStrength("");

  return (
    <div className="h-full w-full bg-[var(--background)] flex flex-col justify-between select-text overflow-hidden">
      {/* 1. Top Search Bar Header on the Right Section for better visibility and UX */}
      <div className="h-[48px] px-6 border-b border-[var(--border-subtle)] bg-[var(--surface-panel)] flex items-center justify-between gap-3 shrink-0 select-none">
        <div className="flex-1 max-w-[560px]">
          <SearchInput
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            onClear={() => setSearchQuery("")}
            placeholder="Search vault items..."
            className="w-full h-8 text-xs"
          />
        </div>
        <div className="flex items-center gap-1.5 shrink-0">
          {onOpenSettings && (
            <IconButton
              icon={Settings}
              label="Open Settings"
              size="sm"
              variant="ghost"
              onClick={onOpenSettings}
              className="h-8 w-8 rounded-lg"
            />
          )}
          {onLockVault && (
            <IconButton
              icon={Lock}
              label="Lock Vault"
              size="sm"
              variant="ghost"
              onClick={onLockVault}
              className="h-8 w-8 rounded-lg"
            />
          )}
        </div>
      </div>

      {/* 2. Inspector Content Area */}
      {!entry ? (
        <div className="flex-1 w-full flex flex-col items-center justify-center p-8 text-center select-none">
          <div className="h-12 w-12 rounded-xl bg-[var(--surface-card)] border border-transparent flex items-center justify-center mb-3 shadow-xs">
            <Icon icon={Shield} size="md" tone="muted" />
          </div>
          <h3 className="text-sm font-bold text-[var(--text-primary)]">No Entry Selected</h3>
          <p className="text-xs text-[var(--text-muted)] max-w-xs mt-1 leading-relaxed">
            Select an item from the vault list to view credentials, security health, and metadata.
          </p>
        </div>
      ) : (
        <div className="flex-1 overflow-y-auto px-6 py-5 flex flex-col justify-between">
          {/* Compact Content Container (Constrained 640px max width) */}
          <div className="flex flex-col gap-5 max-w-[640px] w-full mx-auto">
            {/* Header Section (Compact 12x12 avatar, 20px title, 32px action buttons) */}
            <div className="flex items-start justify-between pb-5 border-b border-[var(--border-subtle)]">
              <div className="flex items-center gap-3.5">
                <FaviconAvatar title={entry.title} websiteUrl={entry.websiteUrl} size="md" className="h-12 w-12 rounded-xl text-lg font-bold shrink-0 shadow-sm" />
                <div className="flex flex-col gap-1">
                  <div className="flex items-center gap-2.5">
                    <h2 className="text-xl font-bold text-[var(--text-primary)] tracking-tight">{entry.title}</h2>
                    <Badge variant="outline" className="text-[11px] px-2 py-0.5 rounded-md font-medium">{entry.category || "Passwords"}</Badge>
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
                {onToggleFavorite && (
                  <button
                    onClick={onToggleFavorite}
                    title={entry.favorite ? "Remove from Favorites" : "Add to Favorites"}
                    className="flex items-center justify-center h-9 w-9 rounded-lg hover:bg-[var(--surface-card-hover)] transition-colors focus:outline-none focus-visible:ring-2 focus-visible:ring-[var(--border-focus)]"
                  >
                    <Icon icon={Star} size="md" className={entry.favorite ? "text-amber-400 fill-amber-400" : "text-[var(--text-muted)] hover:text-[var(--text-primary)]"} />
                  </button>
                )}
                {onEdit && (
                  <IconButton icon={Edit3} label="Edit Entry" variant="ghost" onClick={onEdit} className="rounded-lg" />
                )}
                {onDelete && (
                  <IconButton icon={Trash2} label="Delete Entry" variant="ghost" onClick={onDelete} className="rounded-lg hover:bg-[var(--danger-surface)] hover:text-[var(--danger)]" />
                )}
              </div>
            </div>

            {/* CREDENTIALS Section */}
            <div className="flex flex-col gap-2">
              <div className="flex items-center gap-1.5 text-[var(--text-muted)]">
                <Icon icon={Key} size="xs" />
                <h4 className="text-[11px] font-bold uppercase tracking-wider">Credentials</h4>
              </div>

              <Card className="flex flex-col gap-2 p-3.5 shadow-sm border border-[var(--border-subtle)] bg-[var(--surface-card)]">
                {/* Username Row */}
                <div className="flex items-center justify-between h-9">
                  <div className="flex flex-col gap-0.5 min-w-0">
                    <span className="text-[11px] font-medium text-[var(--text-muted)]">Username / Email</span>
                    <span className="text-[15px] font-semibold text-[var(--text-primary)] truncate">{entry.username || "—"}</span>
                  </div>
                  <CopyButton valueToCopy={entry.username || ""} label="" size="icon" className="p-0 min-w-0" />
                </div>

                <div className="border-t border-[var(--border-subtle)]" />

                {/* Password Row */}
                <div className="flex items-center justify-between h-9">
                  <div className="flex flex-col gap-0.5 min-w-0">
                    <span className="text-[11px] font-medium text-[var(--text-muted)]">Password</span>
                    <span id="password-value" className="text-[15px] font-mono font-semibold text-[var(--text-primary)] tracking-wider">
                      {showPassword ? entry.password || "••••••••••••" : "••••••••••••••••"}
                    </span>
                  </div>

                  <div className="flex items-center gap-1.5 shrink-0">
                    <IconButton
                      icon={showPassword ? EyeOff : Eye}
                      label={showPassword ? "Hide password" : "Reveal password"}
                      variant="ghost"
                      onClick={() => setShowPassword(!showPassword)}
                      className="text-[var(--text-muted)] hover:text-[var(--text-primary)]"
                      aria-expanded={showPassword}
                      aria-controls="password-value"
                    />
                    <CopyButton valueToCopy={entry.password || ""} label="" size="icon" className="p-0 min-w-0" />
                  </div>
                </div>
              </Card>
            </div>

            {/* SECURITY ANALYSIS Section */}
            <div className="flex flex-col gap-2">
              <div className="flex items-center gap-1.5 text-[var(--text-muted)]">
                <Icon icon={Shield} size="xs" />
                <h4 className="text-[11px] font-bold uppercase tracking-wider">Security Analysis</h4>
              </div>

              <Card className="flex flex-col gap-2.5 p-3.5 shadow-sm border border-[var(--border-subtle)] bg-[var(--surface-card)]">
                <div className="flex items-center justify-between">
                  <span className="text-xs font-semibold text-[var(--text-secondary)]">Password Strength</span>
                  <div className="flex items-center gap-1 px-2 py-0.5 rounded-md text-[10px] font-bold" style={{ backgroundColor: strength.bg, color: strength.color }}>
                    <Icon icon={Check} size="xs" style={{ color: strength.color }} />
                    <span>{strength.label}</span>
                  </div>
                </div>

                <div className="flex items-center gap-1.5 h-1.5 w-full mt-0.5">
                  {[1, 2, 3, 4, 5].map((level) => (
                    <div
                      key={level}
                      className="flex-1 h-full rounded-full transition-colors"
                      style={{ backgroundColor: level <= strength.score ? strength.color : "var(--border-subtle)" }}
                    />
                  ))}
                </div>
              </Card>
            </div>

            {/* SECURE NOTES Section */}
            {entry.notes && (
              <div className="flex flex-col gap-2">
                <div className="flex items-center gap-1.5 text-[var(--text-muted)]">
                  <Icon icon={FileText} size="xs" />
                  <h4 className="text-[11px] font-bold uppercase tracking-wider">Secure Notes</h4>
                </div>

                <Card className="flex items-center justify-between p-3.5 text-xs font-medium text-[var(--text-secondary)] shadow-sm border border-[var(--border-subtle)] bg-[var(--surface-card)]">
                  <span className="leading-relaxed">{entry.notes}</span>
                  {onEdit && (
                    <IconButton icon={Edit3} label="Edit Notes" variant="ghost" onClick={onEdit} className="text-[var(--text-muted)] hover:text-[var(--text-primary)] shrink-0" />
                  )}
                </Card>
              </div>
            )}

            {/* METADATA Section - Compact Single Grouped Panel */}
            <div className="flex flex-col gap-2">
              <div className="flex items-center gap-1.5 text-[var(--text-muted)]">
                <Icon icon={Calendar} size="xs" />
                <h4 className="text-[11px] font-bold uppercase tracking-wider">Metadata</h4>
              </div>

              <Card className="grid grid-cols-3 divide-x divide-[var(--border-subtle)] p-3.5 text-xs shadow-sm border border-[var(--border-subtle)] bg-[var(--surface-card)]">
                <div className="flex flex-col pr-3">
                  <span className="text-[10px] text-[var(--text-muted)] font-medium">Updated</span>
                  <span className="font-semibold text-[var(--text-primary)] mt-0.5 truncate">{entry.updatedAt || "Just now"}</span>
                </div>
                <div className="flex flex-col px-3">
                  <span className="text-[10px] text-[var(--text-muted)] font-medium">Created</span>
                  <span className="font-semibold text-[var(--text-primary)] mt-0.5 truncate">
                    {entry.createdAt}
                  </span>
                </div>
                <div className="flex flex-col pl-3">
                  <span className="text-[10px] text-[var(--text-muted)] font-medium">Record</span>
                  <span className="font-semibold text-[var(--text-primary)] font-mono mt-0.5 truncate">#00{entry.id}</span>
                </div>
              </Card>
            </div>

            {/* Footer Encryption Badge */}
            <div className="flex items-center justify-center gap-2 pt-4 text-[10px] font-medium text-[var(--text-muted)] border-t border-[var(--border-subtle)] mt-4">
              <Icon icon={Shield} size="xs" tone="muted" />
              <span>AES-256-GCM • Argon2id • Vault Updated 2 min ago</span>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
