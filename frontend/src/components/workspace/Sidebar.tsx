import React from "react";
import { SidebarItem } from "../layout/SidebarItem";
import { Badge } from "../core/Badge";
import { Avatar } from "../core/Avatar";
import { Shield, Star, KeyRound, FileText, Code, Lock, Settings, ShieldCheck } from "lucide-react";

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
    <aside className="h-full w-full bg-[var(--surface-sidebar)] p-3 flex flex-col justify-between select-none overflow-y-auto">
      <div className="flex flex-col gap-4">
        {/* Header Branding */}
        <div className="flex items-center gap-2.5 px-2 py-1">
          <div className="h-7 w-7 rounded-lg bg-[var(--accent)] flex items-center justify-center font-bold text-white text-xs shadow-sm">
            M
          </div>
          <span className="font-bold text-sm tracking-tight text-[var(--text-primary)]">MyPass v3</span>
          <Badge variant="outline" className="ml-auto text-[10px]">Local</Badge>
        </div>

        {/* Categories Section */}
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
            icon={FileText}
            title="Secure Notes"
            count={itemCounts.notes}
            isSelected={activeCategory === "Secure Notes"}
            onClick={() => onSelectCategory("Secure Notes")}
          />
          <SidebarItem
            icon={Code}
            title="Developer Keys"
            count={itemCounts.keys}
            isSelected={activeCategory === "Developer Keys"}
            onClick={() => onSelectCategory("Developer Keys")}
          />

          <div className="my-2 border-t border-[var(--border-subtle)]" />

          {/* Security Center Destination */}
          <SidebarItem
            icon={ShieldCheck}
            title="Security Center"
            isSelected={activeCategory === "Security Center"}
            onClick={() => onSelectCategory("Security Center")}
          />
        </div>
      </div>

      {/* Footer User & Actions */}
      <div className="flex flex-col gap-1 pt-3 border-t border-[var(--border-subtle)]">
        {onOpenSettings && (
          <SidebarItem
            icon={Settings}
            title="Settings"
            shortcut="⌘,"
            onClick={onOpenSettings}
          />
        )}
        {onLockVault && (
          <SidebarItem
            icon={Lock}
            title="Lock Vault"
            shortcut="⌘L"
            onClick={onLockVault}
          />
        )}
        <div className="flex items-center gap-2.5 px-2 pt-2 mt-1 border-t border-[var(--border-subtle)]">
          <Avatar initials="Sameer" size="sm" />
          <div className="flex flex-col truncate">
            <span className="text-xs font-semibold text-[var(--text-primary)] truncate">Sameer</span>
            <span className="text-[10px] text-[var(--text-muted)] truncate">Vault Encrypted</span>
          </div>
        </div>
      </div>
    </aside>
  );
};
