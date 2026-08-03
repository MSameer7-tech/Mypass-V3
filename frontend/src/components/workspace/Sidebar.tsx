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
    <aside className="h-full w-full bg-[var(--surface-sidebar)] p-3.5 flex flex-col justify-between select-none overflow-y-auto border-r border-[var(--border-subtle)]">
      <div className="flex flex-col gap-5">
        {/* Branding Header */}
        <div className="flex items-center gap-3 px-2 py-1">
          <div className="h-9 w-9 rounded-xl bg-[var(--accent)] flex items-center justify-center shadow-md shadow-blue-500/20 shrink-0">
            <Icon icon={Shield} size="md" tone="primary" />
          </div>
          <div className="flex flex-col">
            <span className="font-bold text-sm tracking-tight text-[var(--text-primary)]">MyPass v3</span>
            <span className="text-[11px] text-[var(--text-muted)] tracking-tight">Local-First Password Manager</span>
          </div>
        </div>

        {/* Main Navigation */}
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

          <div className="my-1.5 border-t border-[var(--border-subtle)]" />

          <SidebarItem
            icon={ShieldCheck}
            title="Security Center"
            isSelected={activeCategory === "Security Center"}
            onClick={() => onSelectCategory("Security Center")}
          />
        </div>

        {/* Categories Section */}
        <div className="flex flex-col gap-1">
          <h4 className="text-[10px] font-bold text-[var(--text-muted)] uppercase tracking-wider px-2 py-1">Categories</h4>
          <SidebarItem icon={Folder} title="Work" count={10} isSelected={activeCategory === "Work"} onClick={() => onSelectCategory("Work")} />
          <SidebarItem icon={Folder} title="Personal" count={8} isSelected={activeCategory === "Personal"} onClick={() => onSelectCategory("Personal")} />
          <SidebarItem icon={Folder} title="Finance" count={3} isSelected={activeCategory === "Finance"} onClick={() => onSelectCategory("Finance")} />
          <SidebarItem icon={Folder} title="Social" count={3} isSelected={activeCategory === "Social"} onClick={() => onSelectCategory("Social")} />
        </div>
      </div>

      {/* Footer Profile & Quick Actions */}
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
        <div className="flex items-center justify-between px-2 pt-2.5 mt-1 border-t border-[var(--border-subtle)]">
          <div className="flex items-center gap-2.5">
            <Avatar initials="Sameer" size="sm" />
            <div className="flex flex-col truncate">
              <span className="text-xs font-semibold text-[var(--text-primary)] truncate">Sameer</span>
              <div className="flex items-center gap-1.5 mt-0.5">
                <span className="h-1.5 w-1.5 rounded-full bg-emerald-400 shadow-xs shadow-emerald-400" />
                <span className="text-[10px] font-medium text-[var(--success)] truncate">Vault Unlocked</span>
              </div>
            </div>
          </div>
          <button className="p-1 text-[var(--text-muted)] hover:text-[var(--text-primary)] rounded">
            <Icon icon={MoreHorizontal} size="xs" />
          </button>
        </div>
      </div>
    </aside>
  );
};
