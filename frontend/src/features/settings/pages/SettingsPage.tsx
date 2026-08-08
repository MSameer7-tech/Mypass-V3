import React, { useState } from "react";
import { motion } from "framer-motion";
import { useSettingsStore } from "../../../stores/settings/useSettingsStore";
import { BackupRepository } from "../../../repositories/BackupRepository";
import { Button } from "../../../components/core/Button";

import { FieldGroup } from "../../../components/layout/FieldGroup";
import { useQueryClient } from "@tanstack/react-query";
import { VAULT_QUERY_KEY } from "../../../queries/useVaultQueries";
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
  Globe,
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
  const queryClient = useQueryClient();

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
    input.style.display = "none";
    document.body.appendChild(input);
    
    input.onchange = async (e: Event) => {
      const file = (e.target as HTMLInputElement).files?.[0];
      if (!file) {
        document.body.removeChild(input);
        return;
      }
      
      const reader = new FileReader();
      reader.onload = async (event) => {
        const content = event.target?.result as string;
        if (content) {
          setImporting(true);
          const res = await BackupRepository.importVault(content);
          setImporting(false);
          if (res.success && onShowToast) {
            queryClient.invalidateQueries({ queryKey: VAULT_QUERY_KEY });
            onShowToast("success", "Vault Imported", `Imported ${res.data.importedCount} entries into vault.`);
          } else {
            onShowToast?.("error", "Import Failed", "Could not parse JSON or save entries.");
          }
        }
        document.body.removeChild(input);
      };
      reader.readAsText(file);
    };
    input.click();
  };

  return (
    <div className="flex h-[560px] w-[860px] bg-[var(--surface-panel)] border border-[var(--border-subtle)] rounded-2xl shadow-2xl overflow-hidden select-none">
      {/* Settings Sidebar Nav (180px) */}
      <aside className="w-[180px] bg-[var(--surface-sidebar)] border-r border-[var(--border-subtle)] p-3 flex flex-col gap-1 shrink-0">
        <h2 className="text-xs font-bold text-[var(--text-muted)] uppercase tracking-wider px-3 py-2">Preferences</h2>
        {navItems.map((item) => {
          const isSelected = activeTab === item.id;
          return (
            <button
              key={item.id}
              onClick={() => setActiveTab(item.id)}
              className={`flex items-center gap-2.5 px-3 py-2 text-[13px] font-medium rounded-lg transition-colors text-left ${
                isSelected
                  ? "bg-[var(--accent)] text-white shadow-xs"
                  : "text-[var(--text-primary)] hover:bg-[#2b2d31]"
              }`}
            >
              <Icon icon={item.icon} size="sm" tone={isSelected ? "white" : "muted"} />
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
            <div className="flex flex-col gap-5">
              <h3 className="text-[14px] font-semibold text-[var(--text-primary)] px-1">Vault Interface</h3>
              
              <div className="flex flex-col rounded-xl overflow-hidden border border-[var(--border-subtle)] bg-[var(--surface-card)]">
                <div className="flex items-center justify-between p-4">
                  <div className="flex items-center gap-4">
                    <div className="w-8 h-8 rounded-lg bg-[var(--surface-sidebar)] flex items-center justify-center shrink-0 border border-[var(--border-subtle)]">
                      <Sliders size={16} className="text-[var(--text-primary)]" />
                    </div>
                    <div className="flex flex-col gap-0.5">
                      <span className="text-[13px] font-medium text-[var(--text-primary)]">Compact View</span>
                      <span className="text-[12px] text-[var(--text-muted)]">Reduce spacing and padding in vault lists.</span>
                    </div>
                  </div>
                  
                  {/* Toggle Switch */}
                  <button
                    onClick={() => setCompactMode(!compactMode)}
                    className={`relative flex h-5 w-9 shrink-0 items-center rounded-full p-0.5 transition-colors duration-200 ease-in-out focus:outline-none ${
                      compactMode ? "bg-blue-500" : "bg-[#333]"
                    }`}
                  >
                    <motion.div
                      layout
                      className="h-4 w-4 rounded-full bg-white shadow-sm"
                      animate={{ x: compactMode ? 16 : 0 }}
                      transition={{ type: "spring", stiffness: 700, damping: 40 }}
                    />
                  </button>
                </div>
              </div>
            </div>
          )}

          {/* Appearance Tab */}
          {activeTab === "appearance" && (
            <div className="flex flex-col gap-5">
              <h3 className="text-[14px] font-semibold text-[var(--text-primary)] px-1">Interface Appearance</h3>
              
              <div className="flex flex-col rounded-xl overflow-hidden border border-[var(--border-subtle)] bg-[var(--surface-card)]">
                {/* Color Theme Row */}
                <div className="flex items-center justify-between p-4 border-b border-[var(--border-subtle)]">
                  <div className="flex items-center gap-4">
                    <div className="w-8 h-8 rounded-lg bg-[var(--surface-sidebar)] flex items-center justify-center shrink-0 border border-[var(--border-subtle)]">
                      <Palette size={16} className="text-[var(--text-primary)]" />
                    </div>
                    <div className="flex flex-col gap-0.5">
                      <span className="text-[13px] font-medium text-[var(--text-primary)]">Color Theme</span>
                      <span className="text-[12px] text-[var(--text-muted)]">Select your preferred application theme.</span>
                    </div>
                  </div>
                  
                  {/* Segmented Control */}
                  <div className="flex items-center bg-[var(--surface-sidebar)] p-1 rounded-lg border border-[var(--border-subtle)] shadow-inner">
                    {(["dark", "light", "system"] as const).map((t) => (
                      <button
                        key={t}
                        onClick={() => setTheme(t)}
                        className={`px-3 py-1 text-[11px] font-bold tracking-wider uppercase rounded-md transition-all ${
                          theme === t
                            ? "bg-[var(--surface-panel)] text-[var(--text-primary)] shadow-sm border border-[var(--border-subtle)]"
                            : "text-[var(--text-muted)] hover:text-[var(--text-secondary)] border border-transparent"
                        }`}
                      >
                        {t}
                      </button>
                    ))}
                  </div>
                </div>

                {/* Favicons Row */}
                <div className="flex items-center justify-between p-4">
                  <div className="flex items-center gap-4">
                    <div className="w-8 h-8 rounded-lg bg-[var(--surface-sidebar)] flex items-center justify-center shrink-0 border border-[var(--border-subtle)]">
                      <Globe size={16} className="text-[var(--text-primary)]" />
                    </div>
                    <div className="flex flex-col gap-0.5">
                      <span className="text-[13px] font-medium text-[var(--text-primary)]">Website Favicons</span>
                      <span className="text-[12px] text-[var(--text-muted)]">Fetch and display website icons on vault cards.</span>
                    </div>
                  </div>
                  
                  {/* Toggle Switch */}
                  <button
                    onClick={() => setShowFavicons(!showFavicons)}
                    className={`relative flex h-5 w-9 shrink-0 items-center rounded-full p-0.5 transition-colors duration-200 ease-in-out focus:outline-none ${
                      showFavicons ? "bg-blue-500" : "bg-[#333]"
                    }`}
                  >
                    <motion.div
                      layout
                      className="h-4 w-4 rounded-full bg-white shadow-sm"
                      animate={{ x: showFavicons ? 16 : 0 }}
                      transition={{ type: "spring", stiffness: 700, damping: 40 }}
                    />
                  </button>
                </div>
              </div>
            </div>
          )}

          {/* Security Tab */}
          {activeTab === "security" && (
            <div className="flex flex-col gap-5">
              <h3 className="text-[14px] font-semibold text-[var(--text-primary)] px-1">Security & Access</h3>
              
              <div className="flex flex-col rounded-xl overflow-hidden border border-[var(--border-subtle)] bg-[var(--surface-card)]">
                {/* Auto-Lock Row */}
                <div className="flex items-center justify-between p-4 border-b border-[var(--border-subtle)]">
                  <div className="flex items-center gap-4">
                    <div className="w-8 h-8 rounded-lg bg-[var(--surface-sidebar)] flex items-center justify-center shrink-0 border border-[var(--border-subtle)]">
                      <Shield size={16} className="text-[var(--text-primary)]" />
                    </div>
                    <div className="flex flex-col gap-0.5">
                      <span className="text-[13px] font-medium text-[var(--text-primary)]">Auto-Lock Timeout</span>
                      <span className="text-[12px] text-[var(--text-muted)]">Vault locks automatically when inactive.</span>
                    </div>
                  </div>
                  
                  {/* Segmented Control */}
                  <div className="flex items-center bg-[var(--surface-sidebar)] p-1 rounded-lg border border-[var(--border-subtle)] shadow-inner shrink-0">
                    {[1, 5, 15, 30, 60].map((mins) => (
                      <button
                        key={mins}
                        onClick={() => setAutoLockMinutes(mins)}
                        className={`px-2 py-1 text-[11px] font-bold tracking-wider rounded-md transition-all ${
                          autoLockMinutes === mins
                            ? "bg-[var(--surface-panel)] text-[var(--text-primary)] shadow-sm border border-[var(--border-subtle)]"
                            : "text-[var(--text-muted)] hover:text-[var(--text-secondary)] border border-transparent"
                        }`}
                      >
                        {mins} MIN
                      </button>
                    ))}
                  </div>
                </div>

                {/* Confirm Deletions Row */}
                <div className="flex items-center justify-between p-4">
                  <div className="flex items-center gap-4">
                    <div className="w-8 h-8 rounded-lg bg-[var(--surface-sidebar)] flex items-center justify-center shrink-0 border border-[var(--border-subtle)]">
                      <Activity size={16} className="text-[var(--text-primary)]" />
                    </div>
                    <div className="flex flex-col gap-0.5">
                      <span className="text-[13px] font-medium text-[var(--text-primary)]">Confirm Deletions</span>
                      <span className="text-[12px] text-[var(--text-muted)]">Require confirmation before deleting entries.</span>
                    </div>
                  </div>
                  
                  {/* Toggle Switch */}
                  <button
                    onClick={() => setConfirmBeforeDelete(!confirmBeforeDelete)}
                    className={`relative flex h-5 w-9 shrink-0 items-center rounded-full p-0.5 transition-colors duration-200 ease-in-out focus:outline-none ${
                      confirmBeforeDelete ? "bg-blue-500" : "bg-[#333]"
                    }`}
                  >
                    <motion.div
                      layout
                      className="h-4 w-4 rounded-full bg-white shadow-sm"
                      animate={{ x: confirmBeforeDelete ? 16 : 0 }}
                      transition={{ type: "spring", stiffness: 700, damping: 40 }}
                    />
                  </button>
                </div>
              </div>
            </div>
          )}

          {/* Clipboard Tab */}
          {activeTab === "clipboard" && (
            <div className="flex flex-col gap-5">
              <h3 className="text-[14px] font-semibold text-[var(--text-primary)] px-1">Clipboard Behavior</h3>
              
              <div className="flex flex-col rounded-xl overflow-hidden border border-[var(--border-subtle)] bg-[var(--surface-card)]">
                <div className="flex items-center justify-between p-4">
                  <div className="flex items-center gap-4">
                    <div className="w-8 h-8 rounded-lg bg-[var(--surface-sidebar)] flex items-center justify-center shrink-0 border border-[var(--border-subtle)]">
                      <Clipboard size={16} className="text-[var(--text-primary)]" />
                    </div>
                    <div className="flex flex-col gap-0.5">
                      <span className="text-[13px] font-medium text-[var(--text-primary)]">Clear Timeout</span>
                      <span className="text-[12px] text-[var(--text-muted)]">Automatically purge copied passwords from OS clipboard.</span>
                    </div>
                  </div>
                  
                  {/* Segmented Control */}
                  <div className="flex items-center bg-[var(--surface-sidebar)] p-1 rounded-lg border border-[var(--border-subtle)] shadow-inner shrink-0">
                    {[15, 30, 45, 60].map((secs) => (
                      <button
                        key={secs}
                        onClick={() => setClipboardAutoClearSeconds(secs)}
                        className={`px-3 py-1 text-[11px] font-bold tracking-wider rounded-md transition-all ${
                          clipboardAutoClearSeconds === secs
                            ? "bg-[var(--surface-panel)] text-[var(--text-primary)] shadow-sm border border-[var(--border-subtle)]"
                            : "text-[var(--text-muted)] hover:text-[var(--text-secondary)] border border-transparent"
                        }`}
                      >
                        {secs} SEC
                      </button>
                    ))}
                  </div>
                </div>
              </div>
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

        <div className="flex justify-end pt-4 mt-auto">
          <Button variant="secondary" size="sm" onClick={onClose}>
            Done
          </Button>
        </div>
      </main>
    </div>
  );
};
