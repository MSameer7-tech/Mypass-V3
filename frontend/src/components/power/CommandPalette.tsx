import React, { useState, useEffect } from "react";
import { AnimatePresence, motion } from "framer-motion";
import { SearchInput } from "../core/Input";
import { Icon, IconProps } from "../core/Icon";
import { Key, Lock, Plus, Settings, Star, Shield, ArrowRight } from "lucide-react";

export interface CommandItem {
  id: string;
  title: string;
  category: "Actions" | "Navigation" | "Passwords";
  icon: IconProps["icon"];
  shortcut?: string;
  onSelect: () => void;
}

export interface CommandPaletteProps {
  open: boolean;
  onClose: () => void;
  commands?: CommandItem[];
}

const defaultCommands: CommandItem[] = [
  { id: "new-password", title: "Create New Password", category: "Actions", icon: Plus, shortcut: "⌘N", onSelect: () => {} },
  { id: "generate", title: "Generate Strong Password", category: "Actions", icon: Key, shortcut: "⌘G", onSelect: () => {} },
  { id: "lock-vault", title: "Lock Vault Immediately", category: "Actions", icon: Lock, shortcut: "⌘L", onSelect: () => {} },
  { id: "nav-favorites", title: "Go to Favorites", category: "Navigation", icon: Star, onSelect: () => {} },
  { id: "nav-all", title: "Go to All Passwords", category: "Navigation", icon: Shield, onSelect: () => {} },
  { id: "nav-settings", title: "Open Security Settings", category: "Navigation", icon: Settings, shortcut: "⌘,", onSelect: () => {} },
];

export const CommandPalette: React.FC<CommandPaletteProps> = ({
  open,
  onClose,
  commands = defaultCommands,
}) => {
  const [query, setQuery] = useState("");
  const [selectedIndex, setSelectedIndex] = useState(0);

  const filteredCommands = commands.filter((cmd) =>
    cmd.title.toLowerCase().includes(query.toLowerCase()) || cmd.category.toLowerCase().includes(query.toLowerCase())
  );

  useEffect(() => {
    setSelectedIndex(0);
  }, [query]);

  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if (!open) return;

      if (e.key === "Escape") {
        onClose();
      } else if (e.key === "ArrowDown") {
        e.preventDefault();
        setSelectedIndex((prev) => (prev + 1) % Math.max(1, filteredCommands.length));
      } else if (e.key === "ArrowUp") {
        e.preventDefault();
        setSelectedIndex((prev) => (prev - 1 + filteredCommands.length) % Math.max(1, filteredCommands.length));
      } else if (e.key === "Enter" && filteredCommands[selectedIndex]) {
        e.preventDefault();
        filteredCommands[selectedIndex].onSelect();
        onClose();
      }
    };

    window.addEventListener("keydown", handleKeyDown);
    return () => window.removeEventListener("keydown", handleKeyDown);
  }, [open, filteredCommands, selectedIndex, onClose]);

  return (
    <AnimatePresence>
      {open && (
        <div className="fixed inset-0 z-50 flex items-start justify-center pt-[12vh] p-4">
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            onClick={onClose}
            className="fixed inset-0 bg-black/60 backdrop-blur-xs"
          />

          <motion.div
            initial={{ opacity: 0, scale: 0.95, y: -10 }}
            animate={{ opacity: 1, scale: 1, y: 0 }}
            exit={{ opacity: 0, scale: 0.95, y: -10 }}
            transition={{ type: "spring", stiffness: 450, damping: 30 }}
            className="relative w-full max-w-xl bg-[var(--surface-panel)] border border-[var(--border-subtle)] rounded-2xl shadow-2xl overflow-hidden z-10 flex flex-col"
          >
            <div className="p-3 border-b border-[var(--border-subtle)]">
              <SearchInput
                value={query}
                onChange={(e) => setQuery(e.target.value)}
                onClear={() => setQuery("")}
                placeholder="Type a command or search passwords..."
                autoFocus
              />
            </div>

            <div className="max-h-[360px] overflow-y-auto p-2 flex flex-col gap-1">
              {filteredCommands.length === 0 ? (
                <div className="p-8 text-center text-xs text-[var(--text-muted)]">No matching commands found.</div>
              ) : (
                filteredCommands.map((cmd, idx) => {
                  const isSelected = idx === selectedIndex;
                  return (
                    <button
                      key={cmd.id}
                      onClick={() => {
                        cmd.onSelect();
                        onClose();
                      }}
                      onMouseEnter={() => setSelectedIndex(idx)}
                      className={`flex items-center justify-between h-10 px-3 text-xs rounded-xl transition-all duration-70 text-left ${
                        isSelected
                          ? "bg-[var(--surface-card-selected)] text-[var(--text-primary)] font-semibold shadow-xs"
                          : "text-[var(--text-secondary)] hover:bg-[var(--surface-card-hover)]"
                      }`}
                    >
                      <div className="flex items-center gap-3">
                        <Icon icon={cmd.icon} size="sm" tone={isSelected ? "accent" : "muted"} />
                        <span>{cmd.title}</span>
                      </div>
                      <div className="flex items-center gap-2">
                        {cmd.shortcut && (
                          <kbd className="px-1.5 py-0.5 text-[10px] font-mono text-[var(--text-muted)] bg-[var(--surface-sidebar)] border border-[var(--border-subtle)] rounded">
                            {cmd.shortcut}
                          </kbd>
                        )}
                        {isSelected && <Icon icon={ArrowRight} size="xs" tone="accent" />}
                      </div>
                    </button>
                  );
                })
              )}
            </div>

            <div className="px-4 py-2 bg-[var(--surface-card)] border-t border-[var(--border-subtle)] flex items-center justify-between text-[11px] text-[var(--text-muted)]">
              <div className="flex items-center gap-3">
                <span>↑↓ Navigate</span>
                <span>↵ Select</span>
                <span>ESC Close</span>
              </div>
              <span className="font-mono">Spotlight Engine</span>
            </div>
          </motion.div>
        </div>
      )}
    </AnimatePresence>
  );
};
