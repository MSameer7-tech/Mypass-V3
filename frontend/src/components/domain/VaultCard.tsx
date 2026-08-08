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
        compactMode ? "h-[54px] py-1.5" : "h-[68px] py-2.5"
      } ${
        isSelected
          ? "bg-[var(--surface-card-selected)] border-[var(--border-focus)] shadow-card-selected"
          : "bg-transparent border-transparent hover:bg-[var(--surface-card-hover)]"
      }`}
    >
      <div className="flex items-center gap-4 min-w-0">
        <FaviconAvatar title={title} websiteUrl={showFavicons ? websiteUrl : undefined} size={compactMode ? "md" : "xl"} className={`${compactMode ? 'h-9 w-9 text-xs' : 'h-[44px] w-[44px] text-lg'} rounded-[10px] font-bold shrink-0 shadow-xs`} />
        <div className="flex flex-col min-w-0 gap-0.5">
          <div className="flex items-center gap-1.5">
            <span className={`font-semibold text-[var(--text-primary)] truncate tracking-tight ${compactMode ? 'text-[14px]' : 'text-[16px]'}`}>{title}</span>
            {favorite && <Icon icon={Star} size="xs" className="fill-amber-400 text-amber-400 shrink-0" />}
          </div>
          {!compactMode && <span className="text-[14px] font-normal text-[var(--text-secondary)] truncate leading-none">{username || "No username"}</span>}
          <span className="text-[11px] text-[var(--text-muted)] leading-none mt-1">{compactMode ? username || "No username" : updatedAt}</span>
        </div>
      </div>



    </motion.div>
  );
};
