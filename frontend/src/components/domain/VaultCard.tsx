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
      className={`group relative flex items-center justify-between h-[62px] px-3.5 py-2.5 rounded-xl cursor-pointer transition-all border ${
        isSelected
          ? "bg-[var(--surface-card-selected)] border-[var(--border-focus)] shadow-card-selected -translate-y-[1px]"
          : "bg-[var(--surface-card)] border-transparent hover:bg-[var(--surface-card-hover)] shadow-xs"
      }`}
    >
      <div className="flex items-center gap-3 min-w-0">
        <FaviconAvatar title={title} websiteUrl={websiteUrl} size="md" className="h-9 w-9 rounded-lg text-xs font-bold shrink-0 shadow-xs" />
        <div className="flex flex-col min-w-0 gap-0.5">
          <div className="flex items-center gap-1.5">
            <span className="text-[13px] font-semibold text-[var(--text-primary)] truncate tracking-tight">{title}</span>
            {favorite && <Icon icon={Star} size="xs" className="fill-amber-400 text-amber-400 shrink-0" />}
          </div>
          <span className="text-[12px] font-normal text-[var(--text-secondary)] truncate leading-none">{username || "No username"}</span>
          <span className="text-[10px] text-[var(--text-muted)] leading-none mt-0.5">{updatedAt}</span>
        </div>
      </div>

      <div className="flex items-center gap-1.5 shrink-0 ml-2">
        <div className="flex items-center gap-1 px-2 py-0.5 rounded-md bg-emerald-950/50 border border-emerald-800/40 text-[9px] font-bold text-emerald-400 uppercase tracking-wider">
          <span>Secure</span>
          <Icon icon={Check} size="xs" className="text-emerald-400" />
        </div>
        <button
          onClick={(e) => {
            e.stopPropagation();
            if (onToggleFavorite) onToggleFavorite(e);
          }}
          className="p-1 text-[var(--text-muted)] hover:text-[var(--text-primary)] rounded-md hover:bg-white/5 transition-all"
        >
          <Icon icon={MoreHorizontal} size="sm" />
        </button>
      </div>
    </motion.div>
  );
};
