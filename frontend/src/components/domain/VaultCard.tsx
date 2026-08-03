import React from "react";
import { FaviconAvatar } from "./FaviconAvatar";
import { Star } from "lucide-react";

export interface VaultCardProps extends Omit<React.HTMLAttributes<HTMLDivElement>, "id"> {
  id: number;
  title: string;
  username: string;
  websiteUrl?: string;
  faviconUrl?: string;
  isFavorite?: boolean;
  timestamp?: string;
  isSelected?: boolean;
  onItemSelect?: (id: number) => void;
  onToggleFavorite?: (id: number, e: React.MouseEvent) => void;
}

export const VaultCard: React.FC<VaultCardProps> = ({
  id,
  title,
  username,
  websiteUrl,
  faviconUrl,
  isFavorite = false,
  timestamp = "Last used 2 days ago",
  isSelected = false,
  onItemSelect,
  onToggleFavorite,
  className = "",
  ...props
}) => {
  const handleClick = () => {
    if (onItemSelect) onItemSelect(id);
  };

  const activeStyle = isSelected
    ? "bg-[var(--surface-card-selected)] border-[var(--border-focus)] ring-1 ring-[var(--border-focus)]"
    : "bg-[var(--surface-card)] hover:bg-[var(--surface-card-hover)] active:bg-[var(--surface-card-selected)] border-[var(--border-subtle)]";

  return (
    <div
      onClick={handleClick}
      className={`relative flex items-center justify-between h-[74px] px-4 py-3 border rounded-xl cursor-pointer transition-all duration-100 select-none ${activeStyle} ${className}`}
      {...props}
    >
      <div className="flex items-center gap-3 min-w-0 flex-1">
        <FaviconAvatar title={title} websiteUrl={websiteUrl} faviconUrl={faviconUrl} size="lg" />
        <div className="flex flex-col gap-0.5 min-w-0 flex-1">
          <span className="text-sm font-semibold text-[var(--text-primary)] truncate tracking-tight">
            {title}
          </span>
          <span className="text-xs text-[var(--text-secondary)] truncate">
            {username || "No username"}
          </span>
          <span className="text-[11px] text-[var(--text-muted)] truncate">
            {timestamp}
          </span>
        </div>
      </div>
      {onToggleFavorite && (
        <button
          type="button"
          onClick={(e) => onToggleFavorite(id, e)}
          className="p-1 rounded text-[var(--text-muted)] hover:text-amber-400 focus:outline-none shrink-0 ml-2"
          aria-label={isFavorite ? "Remove favorite" : "Add favorite"}
        >
          <Star className={`h-4 w-4 ${isFavorite ? "fill-amber-400 text-amber-400" : ""}`} />
        </button>
      )}
    </div>
  );
};
