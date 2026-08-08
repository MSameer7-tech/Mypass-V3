import React from "react";
import { SidebarItem } from "../layout/SidebarItem";
import { Avatar } from "../core/Avatar";
import { Shield, Star, KeyRound, FileText, Code, Lock, Settings, ShieldCheck, Folder, MoreHorizontal } from "lucide-react";
import { Icon } from "../core/Icon";

export interface SidebarProps {
  activeCategory: string;
  onSelectCategory: (category: string) => void;
  onOpenSettings?: () => void;
  onLockVault?: () => void;
  itemCounts: {
    all: number;
    favorites: number;
    passwords: number;
    notes: number;
    keys: number;
  };
}

export const Sidebar: React.FC<SidebarProps> = ({
  activeCategory,
  onSelectCategory,
  onOpenSettings,
  onLockVault,
  itemCounts,
}) => {
  return (
    <aside className="h-full w-full bg-[var(--surface-sidebar)] p-3 flex flex-col justify-between select-none overflow-y-auto border-r border-[var(--border-subtle)]">
      <div className="flex flex-col gap-5">
        {/* Sleek Minimal Branding Header */}
        <div className="flex items-center gap-2.5 px-2 py-1.5 mb-1">
          <img src="/favicon.png" alt="MyPass Icon" className="h-8 w-8 rounded-lg shadow-md shadow-blue-500/20 shrink-0 object-cover" />
          <span className="font-bold text-[15px] tracking-tight text-[var(--text-primary)]">MyPass</span>
        </div>

        {/* Main Navigation - Larger 13px words for better readability */}
        <div className="flex flex-col gap-1">
          <SidebarItem
            icon={Shield}
            title="All Items"
            count={itemCounts.all}
            isSelected={activeCategory === "All"}
            onClick={() => onSelectCategory("All")}
          />
          <SidebarItem
            icon={Star}
            title="Favorites"
            count={itemCounts.favorites}
            isSelected={activeCategory === "Favorites"}
            onClick={() => onSelectCategory("Favorites")}
          />
          <SidebarItem
            icon={KeyRound}
            title="Passwords"
            count={itemCounts.passwords}
            isSelected={activeCategory === "Passwords"}
            onClick={() => onSelectCategory("Passwords")}
          />

          <SidebarItem
            icon={Code}
            title="Developer Keys"
            count={itemCounts.keys}
            isSelected={activeCategory === "Developer Keys"}
            onClick={() => onSelectCategory("Developer Keys")}
          />

          <div className="my-2 border-t border-[var(--border-subtle)]" />

          <SidebarItem
            icon={ShieldCheck}
            title="Security Center"
            isSelected={activeCategory === "Security Center"}
            onClick={() => onSelectCategory("Security Center")}
          />
        </div>


      </div>


    </aside>
  );
};
