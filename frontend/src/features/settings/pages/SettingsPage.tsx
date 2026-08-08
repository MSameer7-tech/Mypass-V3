import React, { useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { useSettingsStore } from "../../../stores/settings/useSettingsStore";
import { BackupRepository } from "../../../repositories/BackupRepository";
import { Button } from "../../../components/core/Button";
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
  Globe,
  AlertTriangle,
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
  const confirmBeforeDelete = useSettingsStore((s) => s.confirmBeforeDelete);
  const setConfirmBeforeDelete = useSettingsStore((s) => s.setConfirmBeforeDelete);

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
              className={`relative flex items-center gap-2.5 px-3 py-2 text-[13px] font-medium rounded-lg transition-colors text-left group ${
                isSelected
                  ? "text-white"
                  : "text-[var(--text-primary)] hover:bg-[var(--surface-card-hover)]"
              }`}
            >
              {isSelected && (
                <motion.div
                  layoutId="settings-active-tab"
                  className="absolute inset-0 bg-[var(--accent)] rounded-lg shadow-sm border border-[var(--accent)]"
                  transition={{ type: "spring", stiffness: 400, damping: 30 }}
                />
              )}
              <div className="relative z-10 flex items-center gap-2.5">
                <motion.div
                  animate={{ scale: isSelected ? 1.04 : 1 }}
                  whileHover={{ scale: isSelected ? 1.04 : 1.02 }}
                  transition={{ type: "spring", stiffness: 450, damping: 25 }}
                >
                  <Icon icon={item.icon} size="sm" tone={isSelected ? "inherit" : "muted"} />
                </motion.div>
                <span>{item.label}</span>
              </div>
            </button>
          );
        })}
      </aside>

      {/* Main Settings Content Pane */}
      <main className="flex-1 p-6 overflow-y-auto flex flex-col justify-between select-text relative">
        <AnimatePresence mode="wait">
          <motion.div
            key={activeTab}
            initial={{ opacity: 0, y: 6 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -6 }}
            transition={{ duration: 0.25, ease: "easeOut" }}
            className="flex flex-col gap-6"
          >
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
                      compactMode ? "bg-[var(--accent)]" : "bg-[var(--surface-input)] border border-[var(--border-subtle)]"
                    }`}
                  >
                    <motion.div
                      layout
                      className="h-4 w-4 rounded-full bg-white shadow-sm"
                      animate={{ x: compactMode ? 16 : 0, scaleX: compactMode ? 1.05 : 1 }}
                      transition={{ type: "spring", stiffness: 500, damping: 30 }}
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
                  <div className="relative flex items-center bg-[var(--surface-sidebar)] p-1 rounded-lg border border-[var(--border-subtle)] shadow-inner">
                    {(["dark", "light", "system"] as const).map((t) => {
                      const isSel = theme === t;
                      return (
                        <button
                          key={t}
                          onClick={() => setTheme(t)}
                          className={`relative px-3 py-1 text-[11px] tracking-wider uppercase rounded-md transition-colors duration-200 z-10 ${
                            isSel ? "text-white font-bold" : "text-[var(--text-muted)] font-medium hover:text-[var(--text-secondary)]"
                          }`}
                        >
                          {isSel && (
                            <motion.div
                              layoutId="theme-active"
                              className="absolute inset-0 bg-[var(--accent)] rounded-md shadow-sm"
                              transition={{ type: "spring", stiffness: 400, damping: 30 }}
                              style={{ zIndex: -1 }}
                            />
                          )}
                          {t}
                        </button>
                      );
                    })}
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
                      showFavicons ? "bg-[var(--accent)]" : "bg-[var(--surface-input)] border border-[var(--border-subtle)]"
                    }`}
                  >
                    <motion.div
                      layout
                      className="h-4 w-4 rounded-full bg-white shadow-sm"
                      animate={{ x: showFavicons ? 16 : 0, scaleX: showFavicons ? 1.05 : 1 }}
                      transition={{ type: "spring", stiffness: 500, damping: 30 }}
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
                  <div className="relative flex items-center bg-[var(--surface-sidebar)] p-1 rounded-lg border border-[var(--border-subtle)] shadow-inner shrink-0">
                    {[1, 5, 15, 30, 60].map((mins) => {
                      const isSel = autoLockMinutes === mins;
                      return (
                        <button
                          key={mins}
                          onClick={() => setAutoLockMinutes(mins)}
                          className={`relative px-2 py-1 text-[11px] tracking-wider rounded-md transition-colors duration-200 z-10 ${
                            isSel ? "text-white font-bold" : "text-[var(--text-muted)] font-medium hover:text-[var(--text-secondary)]"
                          }`}
                        >
                          {isSel && (
                            <motion.div
                              layoutId="autolock-active"
                              className="absolute inset-0 bg-[var(--accent)] rounded-md shadow-sm"
                              transition={{ type: "spring", stiffness: 400, damping: 30 }}
                              style={{ zIndex: -1 }}
                            />
                          )}
                          {mins} MIN
                        </button>
                      );
                    })}
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
                      confirmBeforeDelete ? "bg-[var(--accent)]" : "bg-[var(--surface-input)] border border-[var(--border-subtle)]"
                    }`}
                  >
                    <motion.div
                      layout
                      className="h-4 w-4 rounded-full bg-white shadow-sm"
                      animate={{ x: confirmBeforeDelete ? 16 : 0, scaleX: confirmBeforeDelete ? 1.05 : 1 }}
                      transition={{ type: "spring", stiffness: 500, damping: 30 }}
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
                  <div className="relative flex items-center bg-[var(--surface-sidebar)] p-1 rounded-lg border border-[var(--border-subtle)] shadow-inner shrink-0">
                    {[15, 30, 45, 60].map((secs) => {
                      const isSel = clipboardAutoClearSeconds === secs;
                      return (
                        <button
                          key={secs}
                          onClick={() => setClipboardAutoClearSeconds(secs)}
                          className={`relative px-3 py-1 text-[11px] tracking-wider rounded-md transition-colors duration-200 z-10 ${
                            isSel ? "text-white font-bold" : "text-[var(--text-muted)] font-medium hover:text-[var(--text-secondary)]"
                          }`}
                        >
                          {isSel && (
                            <motion.div
                              layoutId="clipboard-active"
                              className="absolute inset-0 bg-[var(--accent)] rounded-md shadow-sm"
                              transition={{ type: "spring", stiffness: 400, damping: 30 }}
                              style={{ zIndex: -1 }}
                            />
                          )}
                          {secs} SEC
                        </button>
                      );
                    })}
                  </div>
                </div>
              </div>
            </div>
          )}

          {/* Backup Tab */}
          {activeTab === "backup" && (
            <div className="flex flex-col gap-6 max-w-[540px]">
              <div className="flex flex-col gap-2">
                <h3 className="text-[14px] font-semibold text-[var(--text-primary)] px-1">Backup & Export</h3>
                
                {/* Security Warning */}
                <div className="flex items-start gap-3 p-3 mb-2 rounded-xl bg-[var(--warning-surface)] border border-[var(--warning)]/20">
                  <AlertTriangle size={16} className="text-[var(--warning)] shrink-0 mt-0.5" />
                  <p className="text-[12px] leading-relaxed text-[var(--text-primary)]">
                    <strong className="font-semibold text-[var(--warning)]">Security Notice:</strong> Exported JSON files contain your vault data in <span className="font-semibold">plaintext</span>. Store them securely and delete temporary copies when no longer needed.
                  </p>
                </div>
                
                <div className="flex flex-col rounded-xl overflow-hidden border border-[var(--border-subtle)] bg-[var(--surface-card)]">
                  {/* Export Row */}
                  <div className="flex items-center justify-between p-4 border-b border-[var(--border-subtle)]">
                    <div className="flex items-center gap-4">
                      <div className="w-8 h-8 rounded-lg bg-[var(--surface-sidebar)] flex items-center justify-center shrink-0 border border-[var(--border-subtle)]">
                        <Download size={16} className="text-[var(--text-primary)]" />
                      </div>
                      <div className="flex flex-col gap-0.5">
                        <span className="text-[13px] font-medium text-[var(--text-primary)]">Export Vault</span>
                        <span className="text-[12px] text-[var(--text-muted)]">Create a portable plaintext backup of your vault.</span>
                      </div>
                    </div>
                    <Button variant="primary" size="sm" isLoading={exporting} onClick={handleExport} className="shrink-0">
                      Export JSON
                    </Button>
                  </div>

                  {/* Import Row */}
                  <div className="flex items-center justify-between p-4">
                    <div className="flex items-center gap-4">
                      <div className="w-8 h-8 rounded-lg bg-[var(--surface-sidebar)] flex items-center justify-center shrink-0 border border-[var(--border-subtle)]">
                        <Upload size={16} className="text-[var(--text-primary)]" />
                      </div>
                      <div className="flex flex-col gap-0.5">
                        <span className="text-[13px] font-medium text-[var(--text-primary)]">Import Vault</span>
                        <span className="text-[12px] text-[var(--text-muted)]">Add entries to your existing vault from a JSON file.</span>
                      </div>
                    </div>
                    <Button variant="secondary" size="sm" isLoading={importing} onClick={handleImport} className="shrink-0">
                      Import JSON
                    </Button>
                  </div>
                </div>
              </div>
            </div>
          )}

          {/* Diagnostics Tab */}
          {activeTab === "diagnostics" && (
            <div className="flex flex-col gap-6 max-w-[540px]">
              <div className="flex flex-col gap-2">
                <h3 className="text-[14px] font-semibold text-[var(--text-primary)] px-1">System Diagnostics</h3>
                
                <div className="flex flex-col rounded-xl overflow-hidden border border-[var(--border-subtle)] bg-[var(--surface-card)]">
                  {/* Database Status Row */}
                  <div className="flex items-center justify-between p-4 border-b border-[var(--border-subtle)]">
                    <div className="flex items-center gap-4">
                      <div className="w-8 h-8 rounded-lg bg-[var(--surface-sidebar)] flex items-center justify-center shrink-0 border border-[var(--border-subtle)]">
                        <Database size={16} className="text-[var(--text-primary)]" />
                      </div>
                      <div className="flex flex-col gap-0.5">
                        <span className="text-[13px] font-medium text-[var(--text-primary)]">Database</span>
                        <span className="text-[12px] text-[var(--text-muted)]">SQLite • Healthy</span>
                      </div>
                    </div>
                    <div className="flex items-center">
                      <motion.span 
                        initial={{ opacity: 0, scale: 0.9 }}
                        animate={{ opacity: 1, scale: 1 }}
                        transition={{ duration: 0.2 }}
                        className="relative text-[11px] font-bold tracking-wider text-green-400 bg-green-500/10 px-2 py-0.5 rounded-md border border-green-500/20"
                      >
                        <motion.div
                          className="absolute inset-0 bg-green-400 rounded-md"
                          initial={{ opacity: 0.3, scale: 1 }}
                          animate={{ opacity: 0, scale: 1.3 }}
                          transition={{ duration: 0.5, ease: "easeOut", delay: 0.1 }}
                        />
                        <span className="relative z-10">OK</span>
                      </motion.span>
                    </div>
                  </div>

                  {/* Path Row */}
                  <div className="flex items-center justify-between p-4 border-b border-[var(--border-subtle)]">
                    <div className="flex items-center gap-4">
                      <div className="flex flex-col gap-1 w-full">
                        <span className="text-[12px] font-medium text-[var(--text-primary)]">Location</span>
                        <div className="flex items-center gap-2">
                          <code className="text-[11px] text-[var(--text-muted)] font-mono truncate max-w-[320px]">~/.mypass_data/mypass.db</code>
                        </div>
                      </div>
                    </div>
                    <button 
                      className="text-[var(--text-muted)] hover:text-[var(--text-primary)] transition-colors p-1.5 rounded-md hover:bg-[var(--surface-sidebar)] border border-transparent hover:border-[var(--border-subtle)] shrink-0"
                      onClick={() => navigator.clipboard.writeText("~/.mypass_data/mypass.db")}
                      title="Copy Path"
                    >
                      <Clipboard size={14} />
                    </button>
                  </div>
                  
                  {/* Engine versions Row */}
                  <div className="flex flex-col p-4 gap-3 bg-[var(--surface-sidebar)]">
                     <div className="flex items-center justify-between">
                        <span className="text-[12px] text-[var(--text-muted)]">Encryption</span>
                        <span className="text-[12px] font-medium text-[var(--text-primary)]">AES-256-GCM + Argon2id</span>
                     </div>
                     <div className="flex items-center justify-between">
                        <span className="text-[12px] text-[var(--text-muted)]">Python Engine</span>
                        <span className="text-[12px] font-medium text-[var(--text-primary)]">v3.11</span>
                     </div>
                     <div className="flex items-center justify-between">
                        <span className="text-[12px] text-[var(--text-muted)]">Tauri Desktop</span>
                        <span className="text-[12px] font-medium text-[var(--text-primary)]">v2.2</span>
                     </div>
                  </div>
                </div>
              </div>
            </div>
          )}

          {/* Shortcuts Tab */}
          {activeTab === "shortcuts" && (
            <div className="flex flex-col gap-6 max-w-[540px]">
              <div className="flex flex-col gap-2">
                <h3 className="text-[14px] font-semibold text-[var(--text-primary)] px-1">Keyboard Shortcuts</h3>
                
                <div className="flex flex-col rounded-xl overflow-hidden border border-[var(--border-subtle)] bg-[var(--surface-card)]">
                  {[
                    { shortcut: "⌘K", desc: "Open Command Palette" },
                    { shortcut: "⌘L", desc: "Lock Vault Immediately" },
                    { shortcut: "⌘N", desc: "Create New Entry" },
                    { shortcut: "⌘F", desc: "Focus Search Input" },
                    { shortcut: "⌘,", desc: "Open Preferences" },
                  ].map((s, index, arr) => (
                    <div key={s.shortcut} className={`flex items-center justify-between p-4 ${index !== arr.length - 1 ? 'border-b border-[var(--border-subtle)]' : ''}`}>
                      <span className="text-[13px] text-[var(--text-primary)] font-medium">{s.desc}</span>
                      <kbd className="px-2 py-1 font-mono text-[11px] font-semibold tracking-widest text-[var(--text-secondary)] bg-[var(--surface-sidebar)] border border-[var(--border-subtle)] rounded shadow-sm">{s.shortcut}</kbd>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          )}

          {/* About Tab */}
          {activeTab === "about" && (
            <motion.div 
              variants={{
                hidden: { opacity: 0 },
                show: { opacity: 1, transition: { staggerChildren: 0.05 } }
              }}
              initial="hidden"
              animate="show"
              className="flex flex-col flex-1 gap-6 max-w-[540px]"
            >
              {/* Header / Identity */}
              <div className="flex items-start gap-5">
                <motion.div variants={{ hidden: { opacity: 0, y: 8 }, show: { opacity: 1, y: 0, transition: { duration: 0.3 } } }} className="w-[72px] h-[72px] rounded-[16px] bg-[#1a1b1e] border border-[var(--border-subtle)] shadow-[0_0_15px_rgba(255,255,255,0.05)] overflow-hidden flex items-center justify-center shrink-0">
                  <img src="/icon-128.png" alt="MyPass" className="w-[72px] h-[72px] object-cover" onError={(e) => (e.currentTarget.style.display = 'none')} />
                </motion.div>
                <div className="flex flex-col pt-0.5">
                  <motion.h2 variants={{ hidden: { opacity: 0, y: 8 }, show: { opacity: 1, y: 0, transition: { duration: 0.3 } } }} className="text-[22px] font-bold text-[var(--text-primary)] tracking-tight leading-none mb-1.5">MyPass</motion.h2>
                  <motion.span variants={{ hidden: { opacity: 0, y: 8 }, show: { opacity: 1, y: 0, transition: { duration: 0.3 } } }} className="text-[13px] font-semibold text-[var(--text-secondary)] mb-2">Private by design. Simple by default.</motion.span>
                  <motion.p variants={{ hidden: { opacity: 0, y: 8 }, show: { opacity: 1, y: 0, transition: { duration: 0.3 } } }} className="text-[13px] text-[var(--text-muted)] max-w-[360px] leading-[1.5]">
                    A local-first password manager built to keep your credentials secure, organized, and entirely under your control.
                  </motion.p>
                </div>
              </div>

              <motion.div variants={{ hidden: { opacity: 0, y: 8 }, show: { opacity: 1, y: 0, transition: { duration: 0.3 } } }} className="border-t border-[var(--border-subtle)]" />

              {/* Details Grid */}
              <div className="grid grid-cols-2 gap-3 mt-1">
                {/* Version Card */}
                <motion.div variants={{ hidden: { opacity: 0, y: 8 }, show: { opacity: 1, y: 0, transition: { duration: 0.3 } } }} className="flex flex-col gap-1 p-3 rounded-xl bg-[var(--surface-card)] border border-[var(--border-subtle)]">
                  <span className="text-[11px] font-medium text-[var(--text-muted)] uppercase tracking-wider">Version</span>
                  <div className="text-[15px] font-semibold text-[var(--text-primary)]">MyPass v3.0.0</div>
                  <div className="text-[13px] text-[var(--text-secondary)]">Stable Release</div>
                </motion.div>

                {/* Security Card */}
                <motion.div variants={{ hidden: { opacity: 0, y: 8 }, show: { opacity: 1, y: 0, transition: { duration: 0.3 } } }} className="flex flex-col gap-1 p-3 rounded-xl bg-[var(--surface-card)] border border-[var(--border-subtle)]">
                  <span className="text-[11px] font-medium text-[var(--text-muted)] uppercase tracking-wider">Security</span>
                  <div className="text-[15px] font-semibold text-[var(--text-primary)]">AES-256-GCM</div>
                  <div className="text-[13px] text-[var(--text-secondary)]">Argon2id + Local-first</div>
                </motion.div>

                {/* Technology Card */}
                <motion.div variants={{ hidden: { opacity: 0, y: 8 }, show: { opacity: 1, y: 0, transition: { duration: 0.3 } } }} className="flex flex-col gap-1 p-3 rounded-xl bg-[var(--surface-card)] border border-[var(--border-subtle)]">
                  <span className="text-[11px] font-medium text-[var(--text-muted)] uppercase tracking-wider">Technology</span>
                  <div className="text-[15px] font-semibold text-[var(--text-primary)]">React + Tauri</div>
                  <div className="text-[13px] text-[var(--text-secondary)]">Tailwind + Framer Motion</div>
                </motion.div>

                {/* Open Source Card */}
                <motion.div variants={{ hidden: { opacity: 0, y: 8 }, show: { opacity: 1, y: 0, transition: { duration: 0.3 } } }} className="flex flex-col gap-1 p-3 rounded-xl bg-[var(--surface-card)] border border-[var(--border-subtle)]">
                  <span className="text-[11px] font-medium text-[var(--text-muted)] uppercase tracking-wider">Open Source</span>
                  <div className="text-[15px] font-semibold text-[var(--text-primary)]">MIT License</div>
                  <div className="text-[13px] text-[var(--text-secondary)]">Free forever</div>
                </motion.div>
              </div>
            </motion.div>
          )}
          </motion.div>
        </AnimatePresence>

        {/* Footer Area with Copyright and Done Button */}
        <div className="flex items-center justify-between pt-4 mt-auto">
          <span className="text-[11px] font-medium text-[var(--text-muted)] ml-1">
            © 2026 MyPass · Built with privacy in mind
          </span>
          <Button variant="secondary" onClick={onClose} className="h-[38px] px-6 text-[13px]">
            Done
          </Button>
        </div>
      </main>
    </div>
  );
};
