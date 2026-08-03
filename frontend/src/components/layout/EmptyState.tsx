import React from "react";
import { Icon, IconProps } from "../core/Icon";
import { Lock, Search, Star, FolderX, WifiOff, ShieldAlert } from "lucide-react";

export type EmptyStateVariant = "noPasswords" | "noSearchResults" | "noFavorites" | "noCategory" | "noInternet" | "noVault";

export interface EmptyStateProps {
  variant?: EmptyStateVariant;
  title?: string;
  description?: string;
  icon?: IconProps["icon"];
  action?: React.ReactNode;
  className?: string;
}

const variantConfig: Record<EmptyStateVariant, { icon: IconProps["icon"]; title: string; description: string }> = {
  noPasswords: {
    icon: Lock,
    title: "No Password Selected",
    description: "Select a password from the vault list to inspect its security details.",
  },
  noSearchResults: {
    icon: Search,
    title: "No Matching Passwords",
    description: "No passwords or items matched your search query. Try adjusting your filter.",
  },
  noFavorites: {
    icon: Star,
    title: "No Favorites Added",
    description: "Star important items to quickly access them in your favorites list.",
  },
  noCategory: {
    icon: FolderX,
    title: "Category is Empty",
    description: "No passwords have been assigned to this category yet.",
  },
  noInternet: {
    icon: WifiOff,
    title: "Offline Mode Active",
    description: "MyPass runs 100% locally on your device. Remote icon updates paused.",
  },
  noVault: {
    icon: ShieldAlert,
    title: "No Vault Created",
    description: "Create a new local encrypted vault to store your passwords securely.",
  },
};

export const EmptyState: React.FC<EmptyStateProps> = ({
  variant = "noPasswords",
  title,
  description,
  icon,
  action,
  className = "",
}) => {
  const config = variantConfig[variant];
  const DisplayIcon = icon || config.icon;
  const displayTitle = title || config.title;
  const displayDescription = description || config.description;

  return (
    <div className={`flex flex-col items-center justify-center p-8 text-center max-w-sm mx-auto ${className}`}>
      <div className="flex items-center justify-center h-14 w-14 rounded-2xl bg-[var(--surface-card)] border border-[var(--border-subtle)] mb-4 shadow-sm">
        <Icon icon={DisplayIcon} size="lg" tone="accent" />
      </div>
      <h3 className="text-base font-bold text-[var(--text-primary)] mb-1 tracking-tight">{displayTitle}</h3>
      <p className="text-xs text-[var(--text-muted)] leading-relaxed mb-5">{displayDescription}</p>
      {action && <div className="flex items-center gap-2">{action}</div>}
    </div>
  );
};
