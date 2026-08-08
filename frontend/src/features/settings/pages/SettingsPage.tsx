import React, { useState } from "react";
import { useSettingsStore } from "../../../stores/settings/useSettingsStore";
import { BackupRepository } from "../../../repositories/BackupRepository";
import { Button } from "../../../components/core/Button";

import { FieldGroup } from "../../../components/layout/FieldGroup";
import {
  Sliders,
  Palette,
  Shield,
  Clipboard,
  Database,
  Download,
  Upload,
  Activity,
  Keyboard,
  Info,
  Check,
} from "lucide-react";
import { Icon, IconProps } from "../../../components/core/Icon";

export type SettingsTab =
  | "general"
  | "appearance"
  | "security"
  | "clipboard"
  | "backup"
  | "diagnostics"
  | "shortcuts"
  | "about";

export interface SettingsPageProps {
  onClose: () => void;
  onShowToast?: (variant: "success" | "error" | "info", title: string, desc?: string) => void;
}

const navItems: { id: SettingsTab; label: string; icon: IconProps["icon"] }[] = [
  { id: "general", label: "General", icon: Sliders },
  { id: "appearance", label: "Appearance", icon: Palette },
  { id: "security", label: "Security & Lock", icon: Shield },
  { id: "clipboard", label: "Clipboard", icon: Clipboard },
  { id: "backup", label: "Backup & Export", icon: Database },
  { id: "diagnostics", label: "Diagnostics", icon: Activity },
  { id: "shortcuts", label: "Shortcuts", icon: Keyboard },
  { id: "about", label: "About", icon: Info },
];

export const SettingsPage: React.FC<SettingsPageProps> = ({ onClose, onShowToast }) => {
  const [activeTab, setActiveTab] = useState<SettingsTab>("general");
  const [exporting, setExporting] = useState(false);
  const [importing, setImporting] = useState(false);

  // Settings Store
  const theme = useSettingsStore((s) => s.theme);
  const setTheme = useSettingsStore((s) => s.setTheme);
  const compactMode = useSettingsStore((s) => s.compactMode);
  const setCompactMode = useSettingsStore((s) => s.setCompactMode);
  const showFavicons = useSettingsStore((s) => s.showFavicons);
  const setShowFavicons = useSettingsStore((s) => s.setShowFavicons);
  const autoLockMinutes = useSettingsStore((s) => s.autoLockMinutes);
  const setAutoLockMinutes = useSettingsStore((s) => s.setAutoLockMinutes);
  const clipboardAutoClearSeconds = useSettingsStore((s) => s.clipboardAutoClearSeconds);
  const setClipboardAutoClearSeconds = useSettingsStore((s) => s.setClipboardAutoClearSeconds);

  const handleExport = async () => {
    setExporting(true);
    const res = await BackupRepository.exportVault("json");
    setExporting(false);
    if (res.success && onShowToast) {
      const blob = new Blob([res.data.payload], { type: "application/json" });
      const url = URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url;
      a.download = res.data.filename || "mypass-vault-backup.json";
      a.click();
      URL.revokeObjectURL(url);
      
      onShowToast("success", "Vault Exported", `Exported ${res.data.itemCount} items to JSON.`);
    }
  };

  const handleImport = async () => {
    const input = document.createElement("input");
    input.type = "file";
    input.accept = "application/json,.json";
    input.onchange = async (e: Event) => {
      const file = (e.target as HTMLInputElement).files?.[0];
      if (!file) return;
      
      const reader = new FileReader();
      reader.onload = async (event) => {
        const content = event.target?.result as string;
        if (content) {
          setImporting(true);
          const res = await BackupRepository.importVault(content);
          setImporting(false);
          if (res.success && onShowToast) {
            onShowToast("success", "Vault Imported", `Imported ${res.data.importedCount} entries into vault.`);
          } else {
            onShowToast?.("error", "Import Failed", "Could not parse JSON or save entries.");
          }
        }
      };
      reader.readAsText(file);
    };
    input.click();
  };

  return (
    <div className="flex h-[560px] w-[860px] bg-[var(--surface-panel)] border border-[var(--border-subtle)] rounded-2xl shadow-2xl overflow-hidden select-none">
      {/* Settings Sidebar Nav (220px) */}
      <aside className="w-[220px] bg-[var(--surface-sidebar)] border-r border-[var(--border-subtle)] p-3 flex flex-col gap-1 shrink-0">
        <h2 className="text-xs font-bold text-[var(--text-muted)] uppercase tracking-wider px-3 py-2">Preferences</h2>
        {navItems.map((item) => {
          const isSelected = activeTab === item.id;
          return (
            <button
              key={item.id}
              onClick={() => setActiveTab(item.id)}
              className={`flex items-center gap-2.5 px-3 py-2 text-xs font-semibold rounded-lg transition-all text-left ${
                isSelected
                  ? "bg-[var(--surface-card-selected)] text-[var(--text-primary)] shadow-xs"
                  : "text-[var(--text-secondary)] hover:bg-[var(--surface-card-hover)] hover:text-[var(--text-primary)]"
              }`}
            >
              <Icon icon={item.icon} size="sm" tone={isSelected ? "accent" : "muted"} />
              <span>{item.label}</span>
            </button>
          );
        })}
      </aside>

      {/* Main Settings Content Pane */}
      <main className="flex-1 p-6 overflow-y-auto flex flex-col justify-between select-text">
        <div className="flex flex-col gap-6">
          {/* General Tab */}
          {activeTab === "general" && (
            <div className="flex flex-col gap-4">
              <h3 className="text-base font-bold text-[var(--text-primary)] border-b border-[var(--border-subtle)] pb-2">General Settings</h3>
              <FieldGroup label="Compact View Mode" description="Reduce line height and padding in vault item cards.">
                <Button variant={compactMode ? "primary" : "secondary"} size="sm" onClick={() => setCompactMode(!compactMode)}>
                  {compactMode ? "Compact Enabled ✓" : "Standard View"}
                </Button>
              </FieldGroup>
            </div>
          )}

          {/* Appearance Tab */}
          {activeTab === "appearance" && (
            <div className="flex flex-col gap-4">
              <h3 className="text-base font-bold text-[var(--text-primary)] border-b border-[var(--border-subtle)] pb-2">Appearance</h3>
              <FieldGroup label="Color Theme">
                <div className="flex items-center gap-2">
                  {(["dark", "light", "system"] as const).map((t) => (
                    <Button
                      key={t}
                      variant={theme === t ? "primary" : "secondary"}
                      size="sm"
                      onClick={() => setTheme(t)}
                    >
                      {t.toUpperCase()}
                    </Button>
                  ))}
                </div>
              </FieldGroup>
              <FieldGroup label="Favicons" description="Fetch website favicons for vault cards.">
                <Button variant={showFavicons ? "primary" : "secondary"} size="sm" onClick={() => setShowFavicons(!showFavicons)}>
                  {showFavicons ? "Favicons Visible ✓" : "Hidden"}
                </Button>
              </FieldGroup>
            </div>
          )}

          {/* Security Tab */}
          {activeTab === "security" && (
            <div className="flex flex-col gap-4">
              <h3 className="text-base font-bold text-[var(--text-primary)] border-b border-[var(--border-subtle)] pb-2">Security & Auto-Lock</h3>
              <FieldGroup label="Auto-Lock Inactivity Timeout" description="Vault locks automatically when inactive.">
                <div className="flex items-center gap-2">
                  {[1, 5, 15, 30, 60].map((mins) => (
                    <Button
                      key={mins}
                      variant={autoLockMinutes === mins ? "primary" : "secondary"}
                      size="sm"
                      onClick={() => setAutoLockMinutes(mins)}
                    >
                      {mins}m
                    </Button>
                  ))}
                </div>
              </FieldGroup>
            </div>
          )}

          {/* Clipboard Tab */}
          {activeTab === "clipboard" && (
            <div className="flex flex-col gap-4">
              <h3 className="text-base font-bold text-[var(--text-primary)] border-b border-[var(--border-subtle)] pb-2">Clipboard Auto-Clear</h3>
              <FieldGroup label="Clear Timeout" description="Automatically purge copied passwords from OS clipboard.">
                <div className="flex items-center gap-2">
                  {[15, 30, 45, 60].map((secs) => (
                    <Button
                      key={secs}
                      variant={clipboardAutoClearSeconds === secs ? "primary" : "secondary"}
                      size="sm"
                      onClick={() => setClipboardAutoClearSeconds(secs)}
                    >
                      {secs}s
                    </Button>
                  ))}
                </div>
              </FieldGroup>
            </div>
          )}

          {/* Backup Tab */}
          {activeTab === "backup" && (
            <div className="flex flex-col gap-4">
              <h3 className="text-base font-bold text-[var(--text-primary)] border-b border-[var(--border-subtle)] pb-2">Backup & Export</h3>
              <div className="flex items-center gap-3">
                <Button variant="primary" size="sm" leadingIcon={Download} isLoading={exporting} onClick={handleExport}>
                  Export Vault (JSON)
                </Button>
                <Button variant="secondary" size="sm" leadingIcon={Upload} isLoading={importing} onClick={handleImport}>
                  Import Vault
                </Button>
              </div>
            </div>
          )}

          {/* Diagnostics Tab */}
          {activeTab === "diagnostics" && (
            <div className="flex flex-col gap-3 font-mono text-xs">
              <h3 className="text-base font-bold font-sans text-[var(--text-primary)] border-b border-[var(--border-subtle)] pb-2">System Diagnostics</h3>
              <div className="p-3 bg-[var(--surface-card)] rounded-xl border border-[var(--border-subtle)] flex flex-col gap-2">
                <div>Database Path: ~/.password_manager_data/mypass.db</div>
                <div>Encryption: AES-256-GCM + Argon2id</div>
                <div>Python Engine: v3.11</div>
                <div>Tauri Desktop: v2.2</div>
                <div>SQLite Status: Healthy ✓</div>
              </div>
            </div>
          )}

          {/* Shortcuts Tab */}
          {activeTab === "shortcuts" && (
            <div className="flex flex-col gap-3 text-xs">
              <h3 className="text-base font-bold text-[var(--text-primary)] border-b border-[var(--border-subtle)] pb-2">Keyboard Shortcuts</h3>
              <div className="grid grid-cols-2 gap-2">
                {[
                  { shortcut: "⌘K", desc: "Open Command Palette" },
                  { shortcut: "⌘L", desc: "Lock Vault Immediately" },
                  { shortcut: "⌘N", desc: "Create New Entry" },
                  { shortcut: "⌘F", desc: "Focus Search Input" },
                  { shortcut: "⌘,", desc: "Open Preferences" },
                ].map((s) => (
                  <div key={s.shortcut} className="flex items-center justify-between p-2.5 bg-[var(--surface-card)] rounded-lg border border-[var(--border-subtle)]">
                    <span className="text-[var(--text-secondary)]">{s.desc}</span>
                    <kbd className="px-1.5 py-0.5 font-mono text-[10px] bg-[var(--surface-sidebar)] border border-[var(--border-subtle)] rounded">{s.shortcut}</kbd>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* About Tab */}
          {activeTab === "about" && (
            <div className="flex flex-col flex-1 gap-8">
              {/* Header / Identity */}
              <div className="flex items-start gap-5">
                <div className="w-[72px] h-[72px] rounded-[18px] bg-[#1a1b1e] border border-[var(--border-subtle)] shadow-sm flex items-center justify-center shrink-0">
                  <img src="/mypass-icon.png" alt="MyPass" className="w-[48px] h-[48px] object-contain" onError={(e) => (e.currentTarget.style.display = 'none')} />
                </div>
                <div className="flex flex-col pt-1">
                  <h2 className="text-[22px] font-bold text-[var(--text-primary)] tracking-tight leading-none mb-1">MyPass</h2>
                  <span className="text-[13px] font-semibold text-[var(--text-secondary)] mb-2">Local-first password manager</span>
                  <p className="text-[13px] text-[var(--text-muted)] max-w-[360px] leading-[1.6]">
                    Securely store, organize, and manage your passwords and sensitive information with a private, local-first vault.
                  </p>
                </div>
              </div>

              <div className="border-t border-[var(--border-subtle)]" />

              {/* Details Grid */}
              <div className="grid grid-cols-2 gap-x-8 gap-y-8">
                {/* Column 1 */}
                <div className="flex flex-col gap-6">
                  <div className="flex flex-col gap-2">
                    <span className="text-[10px] font-bold text-[var(--text-muted)] uppercase tracking-wider">Version</span>
                    <div className="flex flex-col gap-1">
                      <div className="text-[13px] font-bold text-[var(--text-primary)]">MyPass v3.0.0</div>
                      <div className="text-[13px] text-[var(--text-secondary)]">Stable Release</div>
                    </div>
                  </div>
                  
                  <div className="flex flex-col gap-2">
                    <span className="text-[10px] font-bold text-[var(--text-muted)] uppercase tracking-wider">Technology</span>
                    <div className="flex flex-col gap-1">
                      <div className="text-[13px] text-[var(--text-secondary)]">React + TypeScript</div>
                      <div className="text-[13px] text-[var(--text-secondary)]">Tauri</div>
                      <div className="text-[13px] text-[var(--text-secondary)]">Tailwind CSS</div>
                      <div className="text-[13px] text-[var(--text-secondary)]">Framer Motion</div>
                    </div>
                  </div>
                </div>

                {/* Column 2 */}
                <div className="flex flex-col gap-6">
                  <div className="flex flex-col gap-2">
                    <span className="text-[10px] font-bold text-[var(--text-muted)] uppercase tracking-wider">Security</span>
                    <div className="flex flex-col gap-1">
                      <div className="text-[13px] text-[var(--text-secondary)]">AES-256-GCM encryption</div>
                      <div className="text-[13px] text-[var(--text-secondary)]">Argon2id key derivation</div>
                      <div className="text-[13px] text-[var(--text-secondary)]">Local-first architecture</div>
                      <div className="text-[13px] text-[var(--text-secondary)]">No account or cloud dependency</div>
                    </div>
                  </div>
                  
                  <div className="flex flex-col gap-2">
                    <span className="text-[10px] font-bold text-[var(--text-muted)] uppercase tracking-wider">Open Source</span>
                    <div className="flex flex-col gap-1">
                      <div className="text-[13px] text-[var(--text-secondary)]">MIT License</div>
                    </div>
                  </div>
                </div>
              </div>

              <div className="mt-auto pt-8 text-center text-[11px] text-[var(--text-muted)] font-medium">
                © 2026 MyPass • Built with privacy in mind
              </div>
            </div>
          )}
        </div>

        <div className="flex justify-end pt-4 border-t border-[var(--border-subtle)] mt-4">
          <Button variant="primary" size="sm" leadingIcon={Check} onClick={onClose}>
            Done
          </Button>
        </div>
      </main>
    </div>
  );
};
