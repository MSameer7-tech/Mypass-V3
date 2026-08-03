import React from "react";
import { FaviconAvatar } from "../domain/FaviconAvatar";
import { SecurityBadge } from "../domain/SecurityBadge";
import { InspectorField } from "../domain/InspectorField";
import { PasswordStrength } from "../domain/PasswordStrength";
import { EmptyState } from "../layout/EmptyState";
import { Button } from "../core/Button";
import { MockVaultEntry } from "../../mocks/vault";
import { Edit2, Trash2 } from "lucide-react";

export interface InspectorProps {
  entry?: MockVaultEntry;
  onEdit?: (entry: MockVaultEntry) => void;
  onDelete?: (entry: MockVaultEntry) => void;
}

export const Inspector: React.FC<InspectorProps> = ({
  entry,
  onEdit,
  onDelete,
}) => {
  if (!entry) {
    return (
      <div className="flex items-center justify-center h-full p-8 bg-[var(--background)]">
        <EmptyState variant="noPasswords" />
      </div>
    );
  }

  return (
    <main className="h-full bg-[var(--background)] p-6 overflow-y-auto flex flex-col justify-between select-text">
      <div className="flex flex-col gap-6">
        {/* Header Section */}
        <div className="flex items-start justify-between pb-5 border-b border-[var(--border-subtle)]">
          <div className="flex items-center gap-4">
            <FaviconAvatar title={entry.title} websiteUrl={entry.websiteUrl} size="xl" />
            <div className="flex flex-col gap-1">
              <div className="flex items-center gap-2.5">
                <h1 className="text-2xl font-bold tracking-tight text-[var(--text-primary)]">{entry.title}</h1>
                <SecurityBadge status={entry.securityStatus} />
              </div>
              <span className="text-xs text-[var(--text-muted)] font-mono">{entry.websiteUrl}</span>
            </div>
          </div>
          <div className="flex items-center gap-2">
            {onEdit && (
              <Button variant="secondary" size="sm" leadingIcon={Edit2} onClick={() => onEdit(entry)}>
                Edit
              </Button>
            )}
            {onDelete && (
              <Button variant="destructive" size="sm" leadingIcon={Trash2} onClick={() => onDelete(entry)}>
                Delete
              </Button>
            )}
          </div>
        </div>

        {/* Credentials Cards */}
        <div className="grid grid-cols-1 gap-3">
          <InspectorField label="Username / Email" value={entry.username} />
          {entry.password && (
            <InspectorField label="Password" value={entry.password} isSensitive revealable />
          )}
          <InspectorField label="Website URL" value={entry.websiteUrl} actionUrl={entry.websiteUrl} />
          {entry.notes && <InspectorField label="Notes" value={entry.notes} copyable={false} />}
        </div>

        {/* Password Strength Card */}
        {entry.password && (
          <div className="p-4 bg-[var(--surface-card)] border border-[var(--border-subtle)] rounded-xl">
            <PasswordStrength score={entry.strengthScore} />
          </div>
        )}
      </div>

      {/* Security Metadata Footer */}
      <div className="text-xs text-[var(--text-muted)] text-center pt-4 border-t border-[var(--border-subtle)] mt-6">
        Encrypted with AES-256-GCM & Argon2id • {entry.updatedAt}
      </div>
    </main>
  );
};
