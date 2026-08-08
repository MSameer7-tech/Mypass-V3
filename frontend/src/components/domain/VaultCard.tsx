import React from "react";
import { motion } from "framer-motion";
import { FaviconAvatar } from "./FaviconAvatar";
import { Star, MoreHorizontal, Check } from "lucide-react";
import { Icon } from "../core/Icon";
import { useSettingsStore } from "../../stores/settings/useSettingsStore";

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
  const compactMode = useSettingsStore((s) => s.compactMode);
  const showFavicons = useSettingsStore((s) => s.showFavicons);

  return (
    <motion.div
      whileHover={{ y: -1 }}
      whileTap={{ scale: 0.99 }}
      transition={{ duration: 0.12 }}
      onClick={onClick}
      className={`group relative flex items-center justify-between px-3.5 rounded-xl cursor-pointer transition-all border ${
        compactMode ? "h-[50px] py-1.5" : "h-[62px] py-2.5"
      } ${
        isSelected
          ? "bg-[var(--surface-card-selected)] border-[var(--border-focus)] shadow-card-selected -translate-y-[1px]"
          : "bg-[var(--surface-card)] border-transparent hover:bg-[var(--surface-card-hover)] shadow-xs"
      }`}
    >
      <div className="flex items-center gap-3 min-w-0">
        <FaviconAvatar title={title} websiteUrl={showFavicons ? websiteUrl : undefined} size={compactMode ? "sm" : "md"} className={`${compactMode ? 'h-7 w-7' : 'h-9 w-9'} rounded-lg text-xs font-bold shrink-0 shadow-xs`} />
        <div className="flex flex-col min-w-0 gap-0.5">
          <div className="flex items-center gap-1.5">
            <span className={`font-semibold text-[var(--text-primary)] truncate tracking-tight ${compactMode ? 'text-[12px]' : 'text-[13px]'}`}>{title}</span>
            {favorite && <Icon icon={Star} size="xs" className="fill-amber-400 text-amber-400 shrink-0" />}
          </div>
          {!compactMode && <span className="text-[12px] font-normal text-[var(--text-secondary)] truncate leading-none">{username || "No username"}</span>}
          <span className="text-[10px] text-[var(--text-muted)] leading-none mt-0.5">{compactMode ? username || "No username" : updatedAt}</span>
        </div>
      </div>


      <div className="flex items-center gap-1.5 shrink-0 ml-2">
        <div className="flex items-center gap-1 px-2 py-0.5 rounded-md bg-[var(--success-surface)] border border-[var(--success)]/20 text-[9px] font-bold text-[var(--success)] uppercase tracking-wider">
          <span>Secure</span>
          <Icon icon={Check} size="xs" className="text-[var(--success)]" />
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
