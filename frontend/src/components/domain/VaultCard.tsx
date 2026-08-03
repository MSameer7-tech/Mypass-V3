import React from "react";
import { motion } from "framer-motion";
import { FaviconAvatar } from "./FaviconAvatar";
import { SecurityBadge } from "./SecurityBadge";
import { Star } from "lucide-react";
import { Icon } from "../core/Icon";

export interface VaultCardProps {
  id: number;
  title: string;
  username: string;
  websiteUrl?: string;
  category?: string;
  favorite?: boolean;
  securityStatus?: "secure" | "weak" | "breached";
  updatedAt?: string;
  isSelected?: boolean;
  onClick?: () => void;
  onToggleFavorite?: (e: React.MouseEvent) => void;
}

export const VaultCard: React.FC<VaultCardProps> = ({
  title,
  username,
  websiteUrl,
  favorite = false,
  securityStatus = "secure",
  updatedAt = "Recently",
  isSelected = false,
  onClick,
  onToggleFavorite,
}) => {
  return (
    <motion.div
      whileHover={{ y: -1 }}
      whileTap={{ scale: 0.99 }}
      transition={{ duration: 0.15 }}
      onClick={onClick}
      className={`group relative flex items-center justify-between h-[84px] p-4 rounded-xl cursor-pointer transition-all border ${
        isSelected
          ? "bg-[var(--surface-card-selected)] border-[var(--border-focus)] shadow-md shadow-blue-500/10"
          : "bg-[var(--surface-card)] border-[var(--border-subtle)] hover:bg-[var(--surface-card-hover)] hover:border-slate-700"
      }`}
    >
      <div className="flex items-center gap-3.5 min-w-0">
        <FaviconAvatar title={title} websiteUrl={websiteUrl} size="md" className="h-11 w-11 rounded-xl text-base font-bold shrink-0" />
        <div className="flex flex-col min-w-0">
          <div className="flex items-center gap-2">
            <span className="text-base font-semibold text-[var(--text-primary)] truncate tracking-tight">{title}</span>
            {favorite && <Icon icon={Star} size="xs" className="fill-amber-400 text-amber-400 shrink-0" />}
          </div>
          <span className="text-sm font-normal text-[var(--text-secondary)] truncate">{username || "No username"}</span>
          <span className="text-xs text-[var(--text-muted)] mt-0.5">{updatedAt}</span>
        </div>
      </div>

      <div className="flex flex-col items-end gap-1.5 shrink-0 ml-2">
        <SecurityBadge status={securityStatus} />
        {onToggleFavorite && (
          <button
            onClick={onToggleFavorite}
            className="opacity-0 group-hover:opacity-100 p-1 text-[var(--text-muted)] hover:text-amber-400 transition-all rounded"
          >
            <Icon icon={Star} size="xs" className={favorite ? "fill-amber-400 text-amber-400" : ""} />
          </button>
        )}
      </div>
    </motion.div>
  );
};
