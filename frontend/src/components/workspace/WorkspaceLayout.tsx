import React, { useState, useMemo, useEffect } from "react";
import { PanelGroup, Panel, PanelResizeHandle } from "react-resizable-panels";
import { Sidebar } from "./Sidebar";
import { Toolbar } from "./Toolbar";
import { VaultList } from "./VaultList";
import { Inspector } from "./Inspector";
import { SecurityCenter } from "../../features/security/pages/SecurityCenter";
import { SettingsPage } from "../../features/settings/pages/SettingsPage";
import { Button } from "../core/Button";
import { Dialog } from "../overlay/Dialog";
import { ConfirmDialog } from "../overlay/ConfirmDialog";
import { CommandPalette } from "../power/CommandPalette";
import { NotificationCenter } from "../overlay/NotificationCenter";
import { Input, PasswordInput } from "../core/Input";
import { FieldGroup } from "../layout/FieldGroup";
import { useVaultStore } from "../../stores/vault/useVaultStore";
import { useSearchStore } from "../../stores/search/useSearchStore";
import { useUIStore } from "../../stores/ui/useUIStore";
import {
  useVaultEntriesQuery,
  useCreateEntryMutation,
  useDeleteEntryMutation,
  useUpdateEntryMutation,
  useToggleFavoriteMutation,
} from "../../queries/useVaultQueries";
import { GeneratorRepository } from "../../repositories/GeneratorRepository";
import { RefreshCw } from "lucide-react";

import { useAuthStore } from "../../stores/auth/useAuthStore";

export const WorkspaceLayout: React.FC = () => {
  // Live Server State via React Query
  const { data: liveEntries = [], isLoading, isError, error } = useVaultEntriesQuery();
  const createMutation = useCreateEntryMutation();
  const updateMutation = useUpdateEntryMutation();
  const deleteMutation = useDeleteEntryMutation();
  const toggleFavoriteMutation = useToggleFavoriteMutation();

  const lockVault = useAuthStore((s) => s.lockVault);

  // Store Selectors (Presentation State)
  const selectedId = useVaultStore((s) => s.selectedEntryId);
  const activeCategory = useVaultStore((s) => s.selectedCategory);
  const selectEntry = useVaultStore((s) => s.selectEntry);
  const setSelectedCategory = useVaultStore((s) => s.setSelectedCategory);

  const searchQuery = useSearchStore((s) => s.query);
  const commandPaletteOpen = useSearchStore((s) => s.commandPaletteOpen);
  const setCommandPaletteOpen = useSearchStore((s) => s.setCommandPaletteOpen);

  const activeDialog = useUIStore((s) => s.activeDialog);
  const openDialog = useUIStore((s) => s.openDialog);
  const closeDialog = useUIStore((s) => s.closeDialog);

  // Form & UI State
  const [newTitle, setNewTitle] = useState("");
  const [newUsername, setNewUsername] = useState("");
  const [newPassword, setNewPassword] = useState("");
  const [newWebsite, setNewWebsite] = useState("");
  const [newNotes, setNewNotes] = useState("");
  const [newCategory, setNewCategory] = useState("Passwords");
  const [newFavorite, setNewFavorite] = useState(false);
  const [toasts, setToasts] = useState<any[]>([]);
  const [sortOption, setSortOption] = useState("recent");

  // Default selection on load
  useEffect(() => {
    if (liveEntries.length > 0 && selectedId === null) {
      selectEntry(liveEntries[0].id);
    }
  }, [liveEntries, selectedId, selectEntry]);

  // Category, Search Filtering & Sorting
  const filteredEntries = useMemo(() => {
    const filtered = liveEntries.filter((entry) => {
      const matchesSearch =
        entry.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
        (entry.username || "").toLowerCase().includes(searchQuery.toLowerCase()) ||
        (entry.websiteUrl || "").toLowerCase().includes(searchQuery.toLowerCase());

      if (activeCategory === "All") return matchesSearch;
      if (activeCategory === "Favorites") return matchesSearch && entry.favorite;
      return matchesSearch && entry.category === activeCategory;
    });

    if (sortOption === "recent") {
      filtered.sort((a, b) => b.id - a.id);
    } else if (sortOption === "az") {
      filtered.sort((a, b) => a.title.localeCompare(b.title));
    } else if (sortOption === "za") {
      filtered.sort((a, b) => b.title.localeCompare(a.title));
    } else if (sortOption === "oldest") {
      filtered.sort((a, b) => a.id - b.id);
    }

    return filtered;
  }, [liveEntries, activeCategory, searchQuery, sortOption]);

  const selectedEntry = liveEntries.find((e) => e.id === selectedId) || filteredEntries[0];

  const itemCounts = useMemo(() => {
    return {
      all: liveEntries.length,
      favorites: liveEntries.filter((e) => e.favorite).length,
      passwords: liveEntries.filter((e) => e.category === "Passwords").length,
      notes: liveEntries.filter((e) => e.category === "Secure Notes").length,
      keys: liveEntries.filter((e) => e.category === "Developer Keys").length,
      work: liveEntries.filter((e) => e.category === "Work").length,
      personal: liveEntries.filter((e) => e.category === "Personal").length,
      finance: liveEntries.filter((e) => e.category === "Finance").length,
      social: liveEntries.filter((e) => e.category === "Social").length,
    };
  }, [liveEntries]);

  const addToast = (variant: "success" | "error" | "warning" | "info", title: string, description?: string) => {
    setToasts((prev) => [...prev, { id: Date.now().toString(), variant, title, description }]);
  };

  const handleGeneratePassword = async () => {
    const res = await GeneratorRepository.generate(16, true, true);
    if (res.success) {
      setNewPassword(res.data.password);
      addToast("info", "Password Generated", "Cryptographically secure password generated.");
    }
  };

  const handleCreateSubmit = async () => {
    if (!newTitle.trim()) return;

    try {
      await createMutation.mutateAsync({
        title: newTitle,
        username: newUsername,
        password: newPassword,
        websiteUrl: newWebsite,
        notes: newNotes,
        category: newCategory,
        favorite: newFavorite,
      });

      setNewTitle("");
      setNewUsername("");
      setNewPassword("");
      setNewWebsite("");
      setNewNotes("");
      setNewCategory("Passwords");
      setNewFavorite(false);
      closeDialog();
      addToast("success", "Entry Created", `'${newTitle}' stored in SQLite database.`);
    } catch (err: any) {
      addToast("error", "Creation Failed", err.message);
    }
  };

  const handleEditSubmit = async () => {
    if (!newTitle.trim() || !selectedEntry) return;

    try {
      await updateMutation.mutateAsync({
        id: selectedEntry.id,
        updates: {
          title: newTitle,
          username: newUsername,
          password: newPassword,
          websiteUrl: newWebsite,
          notes: newNotes,
          category: newCategory as any,
          favorite: newFavorite,
        }
      });
      closeDialog();
      addToast("success", "Entry Updated", `'${newTitle}' has been updated.`);
    } catch (err: any) {
      addToast("error", "Update Failed", err.message);
    }
  };

  const handleConfirmDelete = async () => {
    if (!selectedEntry) return;

    try {
      const currentIndex = filteredEntries.findIndex(e => e.id === selectedEntry.id);
      let nextId: number | null = null;
      if (filteredEntries.length > 1) {
        if (currentIndex < filteredEntries.length - 1) {
          nextId = filteredEntries[currentIndex + 1].id;
        } else {
          nextId = filteredEntries[currentIndex - 1].id;
        }
      }

      await deleteMutation.mutateAsync(selectedEntry.id);
      closeDialog();
      addToast("success", "Entry Deleted", `'${selectedEntry.title}' was deleted.`);

      if (nextId !== null) {
        selectEntry(nextId);
      } else {
        selectEntry(null);
        const searchInput = document.querySelector('input[type="search"]') as HTMLInputElement;
        if (searchInput) {
          searchInput.focus();
        }
      }
    } catch (err: any) {
      addToast("error", "Deletion Failed", err.message);
    }
  };

  const handleLockVault = () => {
    addToast("warning", "Vault Locked", "Session cleared.");
    // Small delay so toast is visible before transition
    setTimeout(() => {
      lockVault();
    }, 500);
  };

  // Global Keyboard Shortcuts
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      // ⌘ on Mac, Ctrl on Windows
      if (e.metaKey || e.ctrlKey) {
        switch (e.key.toLowerCase()) {
          case "k":
            e.preventDefault();
            setCommandPaletteOpen(true);
            break;
          case "l":
            e.preventDefault();
            handleLockVault();
            break;
          case "n":
            e.preventDefault();
            openDialog("newEntry");
            break;
          case ",":
            e.preventDefault();
            openDialog("settings");
            break;
          case "f":
            e.preventDefault();
            const searchInput = document.querySelector('input[placeholder="Search vault items..."]') as HTMLInputElement;
            if (searchInput) searchInput.focus();
            break;
        }
      }
    };

    window.addEventListener("keydown", handleKeyDown);
    return () => window.removeEventListener("keydown", handleKeyDown);
  }, [setCommandPaletteOpen, openDialog]); // eslint-disable-line react-hooks/exhaustive-deps

  return (
    <div className="h-screen w-screen bg-[var(--background)] text-[var(--text-primary)] flex flex-col overflow-hidden select-none">
      <PanelGroup direction="horizontal" className="h-full w-full">
        {/* Column 1: Sidebar (18% ≈ 212px baseline on 1180px window) */}
        <Panel defaultSize={18} minSize={15} maxSize={24} className="bg-[var(--surface-sidebar)]">
          <Sidebar
            activeCategory={activeCategory}
            onSelectCategory={setSelectedCategory}
            onOpenSettings={() => openDialog("settings")}
            onLockVault={handleLockVault}
            itemCounts={itemCounts}
          />
        </Panel>

        <PanelResizeHandle className="w-[1px] bg-[var(--border-subtle)] hover:bg-[var(--accent)] transition-colors cursor-col-resize" />

        {/* View Router: Security Center vs Vault Explorer */}
        {activeCategory === "Security Center" ? (
          <Panel defaultSize={82} minSize={70} className="bg-[var(--background)]">
            <SecurityCenter
              entries={liveEntries}
              onFixEntry={(id) => {
                selectEntry(id);
                setSelectedCategory("All");
              }}
            />
          </Panel>
        ) : (
          <>
            {/* Column 2: Vault List (30% ≈ 354px baseline on 1180px window) */}
            <Panel defaultSize={30} minSize={25} maxSize={38} className="bg-[var(--surface-panel)] border-r border-[var(--border-subtle)] flex flex-col">
              <Toolbar
                sortOption={sortOption}
                onSortChange={setSortOption}
                onNewEntry={() => openDialog("newEntry")}
              />

              {isError ? (
                <div className="p-4 text-xs text-[var(--danger)] text-center font-mono">
                  Database Error: {(error as Error)?.message}
                </div>
              ) : (
                <div className="flex-1 flex flex-col justify-between overflow-hidden">
                  <VaultList
                    entries={filteredEntries}
                    selectedId={selectedEntry?.id}
                    isLoading={isLoading}
                    onSelectEntry={selectEntry}
                    onToggleFavorite={(id, e) => {
                      e.stopPropagation();
                      toggleFavoriteMutation.mutate(id);
                    }}
                  />
                </div>
              )}
            </Panel>

            <PanelResizeHandle className="w-[1px] bg-[var(--border-subtle)] hover:bg-[var(--accent)] transition-colors cursor-col-resize" />

            {/* Column 3: Details Inspector with Top Search Header (Elastic ~52% remaining) */}
            <Panel defaultSize={52} minSize={42} className="bg-[var(--background)]">
              <Inspector
                entry={selectedEntry}
                onEdit={() => {
                  setNewTitle(selectedEntry?.title || "");
                  setNewUsername(selectedEntry?.username || "");
                  setNewPassword(selectedEntry?.password || "");
                  setNewWebsite(selectedEntry?.websiteUrl || "");
                  setNewNotes(selectedEntry?.notes || "");
                  setNewCategory(selectedEntry?.category || "Passwords");
                  setNewFavorite(selectedEntry?.favorite || false);
                  openDialog("editEntry");
                }}
                onDelete={() => openDialog("deleteConfirm")}
                onToggleFavorite={() => selectedEntry && toggleFavoriteMutation.mutate(selectedEntry.id)}
                onOpenSettings={() => openDialog("settings")}
                onLockVault={handleLockVault}
              />
            </Panel>
          </>
        )}
      </PanelGroup>

      {/* Global Overlays */}
      <CommandPalette open={commandPaletteOpen} onClose={() => setCommandPaletteOpen(false)} />

      {/* Settings Page Modal */}
      {activeDialog === "settings" && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/60 backdrop-blur-xs">
          <SettingsPage onClose={closeDialog} onShowToast={addToast} />
        </div>
      )}

      {/* Entry Modal (New & Edit) */}
      <Dialog
        open={activeDialog === "newEntry" || activeDialog === "editEntry"}
        onClose={closeDialog}
        title={activeDialog === "editEntry" ? "Edit Vault Entry" : "New Vault Entry"}
        description={activeDialog === "editEntry" ? "Update your credentials." : "Add credentials to store locally in your AES-256 encrypted SQLite vault."}
        footer={
          <>
            <Button variant="ghost" size="sm" onClick={closeDialog}>
              Cancel
            </Button>
            <Button
              variant="primary"
              size="sm"
              isLoading={activeDialog === "editEntry" ? updateMutation.isPending : createMutation.isPending}
              onClick={activeDialog === "editEntry" ? handleEditSubmit : handleCreateSubmit}
            >
              {activeDialog === "editEntry" ? "Save Changes" : "Save Entry"}
            </Button>
          </>
        }
      >
        <div className="flex flex-col gap-4">
          <FieldGroup label="Title" required>
            <Input
              value={newTitle}
              onChange={(e) => setNewTitle(e.target.value)}
              placeholder="e.g. GitHub"
              autoFocus
            />
          </FieldGroup>
          <FieldGroup label="Category">
            <select
              value={newCategory}
              onChange={(e) => setNewCategory(e.target.value)}
              className="w-full h-10 px-3.5 bg-[var(--surface-input,var(--surface-card))] text-[var(--text-primary)] text-sm rounded-lg border border-[var(--border-subtle)] shadow-[0_1px_2px_rgba(0,0,0,0.05)] focus:outline-none focus:border-[var(--border-focus)] transition-all duration-150"
            >
              <option value="Passwords">Passwords</option>
              <option value="Work">Work</option>
              <option value="Personal">Personal</option>
              <option value="Finance">Finance</option>
              <option value="Social">Social</option>
              <option value="Developer Keys">Developer Keys</option>
            </select>
          </FieldGroup>
          <FieldGroup label="Favorite">
            <label className="flex items-center gap-2 text-sm text-[var(--text-primary)] cursor-pointer">
              <input
                type="checkbox"
                checked={newFavorite}
                onChange={(e) => setNewFavorite(e.target.checked)}
                className="h-4 w-4 rounded border-[var(--border-subtle)] text-[var(--accent)] focus:ring-[var(--border-focus)] bg-[var(--surface-input,var(--surface-card))]"
              />
              Mark as Favorite
            </label>
          </FieldGroup>
          <FieldGroup label="Username / Email">
            <Input
              value={newUsername}
              onChange={(e) => setNewUsername(e.target.value)}
              placeholder="user@mypass.app"
            />
          </FieldGroup>

          <FieldGroup label="Password">
            <div className="flex gap-2">
              <div className="flex-1">
                <PasswordInput
                  value={newPassword}
                  onChange={(e) => setNewPassword(e.target.value)}
                  placeholder="Enter password..."
                />
              </div>
              <Button
                type="button"
                variant="secondary"
                size="sm"
                leadingIcon={RefreshCw}
                onClick={handleGeneratePassword}
              >
                Generate
              </Button>
            </div>
          </FieldGroup>

          <FieldGroup label="Website URL">
            <Input
              value={newWebsite}
              onChange={(e) => setNewWebsite(e.target.value)}
              placeholder="https://..."
            />
          </FieldGroup>
          <FieldGroup label="Notes">
            <textarea
              value={newNotes}
              onChange={(e) => setNewNotes(e.target.value)}
              placeholder="Add secure notes..."
              className="w-full h-20 px-3.5 py-2.5 bg-[var(--surface-input,var(--surface-card))] text-[var(--text-primary)] text-sm rounded-lg border border-[var(--border-subtle)] shadow-[0_1px_2px_rgba(0,0,0,0.05)] focus:outline-none focus:border-[var(--border-focus)] transition-all duration-150 resize-none"
            />
          </FieldGroup>
        </div>
      </Dialog>

      {/* Confirm Delete Dialog */}
      <ConfirmDialog
        open={activeDialog === "deleteConfirm"}
        onClose={closeDialog}
        title="Delete Vault Entry"
        description={`Are you sure you want to permanently delete '${selectedEntry?.title}'? This action cannot be undone.`}
        confirmLabel="Delete Permanently"
        isLoading={deleteMutation.isPending}
        onConfirm={handleConfirmDelete}
      />

      <NotificationCenter toasts={toasts} onDismiss={(id) => setToasts((prev) => prev.filter((t) => t.id !== id))} />
    </div>
  );
};
