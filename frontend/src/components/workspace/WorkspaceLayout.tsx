import React, { useState, useMemo, useEffect } from "react";
import { PanelGroup, Panel, PanelResizeHandle } from "react-resizable-panels";
import { Sidebar } from "./Sidebar";
import { Toolbar } from "./Toolbar";
import { VaultList } from "./VaultList";
import { Inspector } from "./Inspector";
import { SectionHeader } from "../layout/SectionHeader";
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
} from "../../queries/useVaultQueries";
import { GeneratorRepository } from "../../repositories/GeneratorRepository";
import { Plus, RefreshCw } from "lucide-react";

export const WorkspaceLayout: React.FC = () => {
  // Live Server State via React Query
  const { data: liveEntries = [], isLoading, isError, error } = useVaultEntriesQuery();
  const createMutation = useCreateEntryMutation();
  const deleteMutation = useDeleteEntryMutation();

  // Store Selectors (Presentation State)
  const selectedId = useVaultStore((s) => s.selectedEntryId);
  const activeCategory = useVaultStore((s) => s.selectedCategory);
  const selectEntry = useVaultStore((s) => s.selectEntry);
  const toggleFavorite = useVaultStore((s) => s.toggleFavorite);
  const setSelectedCategory = useVaultStore((s) => s.setSelectedCategory);

  const searchQuery = useSearchStore((s) => s.query);
  const setSearchQuery = useSearchStore((s) => s.setSearchQuery);
  const commandPaletteOpen = useSearchStore((s) => s.commandPaletteOpen);
  const setCommandPaletteOpen = useSearchStore((s) => s.setCommandPaletteOpen);

  const activeDialog = useUIStore((s) => s.activeDialog);
  const openDialog = useUIStore((s) => s.openDialog);
  const closeDialog = useUIStore((s) => s.closeDialog);

  // Form State
  const [newTitle, setNewTitle] = useState("");
  const [newUsername, setNewUsername] = useState("");
  const [newPassword, setNewPassword] = useState("");
  const [newWebsite, setNewWebsite] = useState("");
  const [toasts, setToasts] = useState<any[]>([]);

  // Default selection on load
  useEffect(() => {
    if (liveEntries.length > 0 && selectedId === null) {
      selectEntry(liveEntries[0].id);
    }
  }, [liveEntries, selectedId, selectEntry]);

  // Category & Search Filtering
  const filteredEntries = useMemo(() => {
    return liveEntries.filter((entry) => {
      const matchesSearch =
        entry.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
        entry.username.toLowerCase().includes(searchQuery.toLowerCase()) ||
        entry.websiteUrl.toLowerCase().includes(searchQuery.toLowerCase());

      if (activeCategory === "All") return matchesSearch;
      if (activeCategory === "Favorites") return matchesSearch && entry.favorite;
      return matchesSearch && entry.category === activeCategory;
    });
  }, [liveEntries, activeCategory, searchQuery]);

  const selectedEntry = liveEntries.find((e) => e.id === selectedId) || filteredEntries[0];

  const itemCounts = useMemo(() => {
    return {
      all: liveEntries.length,
      favorites: liveEntries.filter((e) => e.favorite).length,
      passwords: liveEntries.filter((e) => e.category === "Passwords").length,
      notes: liveEntries.filter((e) => e.category === "Secure Notes").length,
      keys: liveEntries.filter((e) => e.category === "Developer Keys").length,
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
      });

      setNewTitle("");
      setNewUsername("");
      setNewPassword("");
      setNewWebsite("");
      closeDialog();
      addToast("success", "Entry Created", `'${newTitle}' stored in SQLite database.`);
    } catch (err: any) {
      addToast("error", "Creation Failed", err.message);
    }
  };

  const handleConfirmDelete = async () => {
    if (!selectedEntry) return;

    try {
      await deleteMutation.mutateAsync(selectedEntry.id);
      closeDialog();
      addToast("success", "Entry Deleted", `'${selectedEntry.title}' was deleted.`);
    } catch (err: any) {
      addToast("error", "Deletion Failed", err.message);
    }
  };

  return (
    <div className="h-screen w-screen bg-[var(--background)] text-[var(--text-primary)] flex flex-col overflow-hidden select-none">
      <PanelGroup direction="horizontal" className="h-full w-full">
        {/* Column 1: Resizable Sidebar */}
        <Panel defaultSize={18} minSize={14} maxSize={25} className="bg-[var(--surface-sidebar)]">
          <Sidebar
            activeCategory={activeCategory}
            onSelectCategory={setSelectedCategory}
            onOpenSettings={() => addToast("info", "Settings", "Settings active.")}
            onLockVault={() => addToast("warning", "Vault Locked", "Session cleared.")}
            itemCounts={itemCounts}
          />
        </Panel>

        <PanelResizeHandle className="w-[1px] bg-[var(--border-subtle)] hover:bg-[var(--accent)] transition-colors cursor-col-resize" />

        {/* Column 2: Resizable Vault List */}
        <Panel defaultSize={30} minSize={22} maxSize={45} className="bg-[var(--surface-panel)] border-r border-[var(--border-subtle)] flex flex-col">
          <Toolbar
            searchQuery={searchQuery}
            onSearchChange={setSearchQuery}
            onNewEntry={() => openDialog("newEntry")}
            onLockVault={() => addToast("warning", "Vault Locked", "Session cleared.")}
            onOpenSettings={() => setCommandPaletteOpen(true)}
          />

          <div className="p-3 border-b border-[var(--border-subtle)] flex items-center justify-between">
            <SectionHeader
              title={activeCategory}
              subtitle={`${filteredEntries.length} items`}
              action={
                <Button size="sm" leadingIcon={Plus} onClick={() => openDialog("newEntry")}>
                  New
                </Button>
              }
            />
          </div>

          {isError ? (
            <div className="p-4 text-xs text-[var(--danger)] text-center font-mono">
              Database Error: {(error as Error)?.message}
            </div>
          ) : (
            <VaultList
              entries={filteredEntries}
              selectedId={selectedEntry?.id}
              isLoading={isLoading}
              onSelectEntry={selectEntry}
              onToggleFavorite={(id, e) => {
                e.stopPropagation();
                toggleFavorite(id);
              }}
            />
          )}
        </Panel>

        <PanelResizeHandle className="w-[1px] bg-[var(--border-subtle)] hover:bg-[var(--accent)] transition-colors cursor-col-resize" />

        {/* Column 3: Resizable Inspector Pane */}
        <Panel defaultSize={52} minSize={35} className="bg-[var(--background)]">
          <Inspector
            entry={selectedEntry}
            onEdit={() => addToast("info", "Edit Mode", "Editor drawer active.")}
            onDelete={() => openDialog("deleteConfirm")}
          />
        </Panel>
      </PanelGroup>

      {/* Global Overlays */}
      <CommandPalette open={commandPaletteOpen} onClose={() => setCommandPaletteOpen(false)} />

      {/* New Entry Modal */}
      <Dialog
        open={activeDialog === "newEntry"}
        onClose={closeDialog}
        title="New Vault Entry"
        description="Add credentials to store locally in your AES-256 encrypted SQLite vault."
        footer={
          <>
            <Button variant="ghost" size="sm" onClick={closeDialog}>
              Cancel
            </Button>
            <Button
              variant="primary"
              size="sm"
              isLoading={createMutation.isPending}
              onClick={handleCreateSubmit}
            >
              Save Entry
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
