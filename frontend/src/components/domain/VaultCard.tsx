import React from "react";
import { motion } from "framer-motion";
import { FaviconAvatar } from "./FaviconAvatar";
import { Star, MoreHorizontal, Check } from "lucide-react";
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
  updatedAt = "Recently",
  isSelected = false,
  onClick,
  onToggleFavorite,
}) => {
  return (
    <motion.div
      whileHover={{ y: -1 }}
      whileTap={{ scale: 0.99 }}
      transition={{ duration: 0.12 }}
      onClick={onClick}
      className={`group relative flex items-center justify-between h-[84px] p-3.5 rounded-xl cursor-pointer transition-all border ${
        isSelected
          ? "bg-[var(--surface-card-selected)] border-[var(--border-focus)] shadow-md shadow-blue-500/10"
          : "bg-[var(--surface-card)] border-[var(--border-subtle)] hover:bg-[var(--surface-card-hover)] hover:border-slate-700"
      }`}
    >
      <div className="flex items-center gap-3.5 min-w-0">
        <FaviconAvatar title={title} websiteUrl={websiteUrl} size="md" className="h-11 w-11 rounded-xl text-base font-bold shrink-0 shadow-xs" />
        <div className="flex flex-col min-w-0">
          <div className="flex items-center gap-1.5">
            <span className="text-base font-semibold text-[var(--text-primary)] truncate tracking-tight">{title}</span>
            {favorite && <Icon icon={Star} size="xs" className="fill-amber-400 text-amber-400 shrink-0" />}
          </div>
          <span className="text-sm font-normal text-[var(--text-secondary)] truncate">{username || "No username"}</span>
          <span className="text-xs text-[var(--text-muted)] mt-0.5">{updatedAt}</span>
        </div>
      </div>

      <div className="flex items-center gap-2 shrink-0 ml-2">
        <div className="flex items-center gap-1 px-2 py-0.5 rounded-md bg-emerald-950/40 border border-emerald-800/40 text-[10px] font-bold text-emerald-400 uppercase tracking-wider">
          <span>SECURE</span>
          <Icon icon={Check} size="xs" className="text-emerald-400" />
        </div>
        <button
          onClick={(e) => {
            e.stopPropagation();
            if (onToggleFavorite) onToggleFavorite(e);
          }}
          className="p-1.5 text-[var(--text-muted)] hover:text-[var(--text-primary)] rounded-lg hover:bg-[var(--surface-card-hover)] transition-all"
        >
          <Icon icon={MoreHorizontal} size="sm" />
        </button>
      </div>
    </motion.div>
  );
};
