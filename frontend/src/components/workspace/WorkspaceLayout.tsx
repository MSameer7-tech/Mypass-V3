import React, { useState, useMemo } from "react";
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
import { Input } from "../core/Input";
import { PasswordInput } from "../core/Input";
import { FieldGroup } from "../layout/FieldGroup";
import { mockVaultEntries, MockVaultEntry } from "../../mocks/vault";
import { Plus } from "lucide-react";

export const WorkspaceLayout: React.FC = () => {
  const [entries, setEntries] = useState<MockVaultEntry[]>(mockVaultEntries);
  const [activeCategory, setActiveCategory] = useState<string>("All");
  const [selectedId, setSelectedId] = useState<number>(1);
  const [searchQuery, setSearchQuery] = useState<string>("");

  // Dialog & Overlay States
  const [commandPaletteOpen, setCommandPaletteOpen] = useState(false);
  const [newEntryDialogOpen, setNewEntryDialogOpen] = useState(false);
  const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
  const [toasts, setToasts] = useState<any[]>([]);

  // Category & Search Filtering
  const filteredEntries = useMemo(() => {
    return entries.filter((entry) => {
      const matchesSearch =
        entry.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
        entry.username.toLowerCase().includes(searchQuery.toLowerCase()) ||
        entry.websiteUrl.toLowerCase().includes(searchQuery.toLowerCase());

      if (activeCategory === "All") return matchesSearch;
      if (activeCategory === "Favorites") return matchesSearch && entry.favorite;
      return matchesSearch && entry.category === activeCategory;
    });
  }, [entries, activeCategory, searchQuery]);

  const selectedEntry = entries.find((e) => e.id === selectedId) || filteredEntries[0];

  const itemCounts = useMemo(() => {
    return {
      all: entries.length,
      favorites: entries.filter((e) => e.favorite).length,
      passwords: entries.filter((e) => e.category === "Passwords").length,
      notes: entries.filter((e) => e.category === "Secure Notes").length,
      keys: entries.filter((e) => e.category === "Developer Keys").length,
    };
  }, [entries]);

  const handleToggleFavorite = (id: number, e: React.MouseEvent) => {
    e.stopPropagation();
    setEntries((prev) =>
      prev.map((entry) => (entry.id === id ? { ...entry, favorite: !entry.favorite } : entry))
    );
  };

  const addToast = (variant: "success" | "error" | "warning" | "info", title: string, description?: string) => {
    setToasts((prev) => [...prev, { id: Date.now().toString(), variant, title, description }]);
  };

  const handleDeleteEntry = () => {
    if (!selectedEntry) return;
    setEntries((prev) => prev.filter((e) => e.id !== selectedEntry.id));
    setDeleteDialogOpen(false);
    addToast("success", "Entry Deleted", `'${selectedEntry.title}' was removed from your vault.`);
  };

  return (
    <div className="h-screen w-screen bg-[var(--background)] text-[var(--text-primary)] flex flex-col overflow-hidden select-none">
      <PanelGroup direction="horizontal" className="h-full w-full">
        {/* Column 1: Resizable Sidebar (240px min) */}
        <Panel defaultSize={18} minSize={14} maxSize={25} className="bg-[var(--surface-sidebar)]">
          <Sidebar
            activeCategory={activeCategory}
            onSelectCategory={setActiveCategory}
            onOpenSettings={() => addToast("info", "Settings", "Settings sheet active.")}
            onLockVault={() => addToast("warning", "Vault Locked", "Vault session cleared.")}
            itemCounts={itemCounts}
          />
        </Panel>

        <PanelResizeHandle className="w-[1px] bg-[var(--border-subtle)] hover:bg-[var(--accent)] transition-colors cursor-col-resize" />

        {/* Column 2: Resizable Vault List (340px min) */}
        <Panel defaultSize={30} minSize={22} maxSize={45} className="bg-[var(--surface-panel)] border-r border-[var(--border-subtle)] flex flex-col">
          <Toolbar
            searchQuery={searchQuery}
            onSearchChange={setSearchQuery}
            onNewEntry={() => setNewEntryDialogOpen(true)}
            onLockVault={() => addToast("warning", "Vault Locked", "Session cleared.")}
            onOpenSettings={() => setCommandPaletteOpen(true)}
          />

          <div className="p-3 border-b border-[var(--border-subtle)] flex items-center justify-between">
            <SectionHeader
              title={activeCategory}
              subtitle={`${filteredEntries.length} items`}
              action={
                <Button size="sm" leadingIcon={Plus} onClick={() => setNewEntryDialogOpen(true)}>
                  New
                </Button>
              }
            />
          </div>

          <VaultList
            entries={filteredEntries}
            selectedId={selectedEntry?.id}
            onSelectEntry={setSelectedId}
            onToggleFavorite={handleToggleFavorite}
          />
        </Panel>

        <PanelResizeHandle className="w-[1px] bg-[var(--border-subtle)] hover:bg-[var(--accent)] transition-colors cursor-col-resize" />

        {/* Column 3: Resizable Inspector Pane (~620px min) */}
        <Panel defaultSize={52} minSize={35} className="bg-[var(--background)]">
          <Inspector
            entry={selectedEntry}
            onEdit={() => addToast("info", "Edit Mode", "Editor drawer active.")}
            onDelete={() => setDeleteDialogOpen(true)}
          />
        </Panel>
      </PanelGroup>

      {/* Global Overlays */}
      <CommandPalette open={commandPaletteOpen} onClose={() => setCommandPaletteOpen(false)} />

      {/* New Entry Modal */}
      <Dialog
        open={newEntryDialogOpen}
        onClose={() => setNewEntryDialogOpen(false)}
        title="New Vault Entry"
        description="Add credentials to store locally in your AES-256 encrypted vault."
        footer={
          <>
            <Button variant="ghost" size="sm" onClick={() => setNewEntryDialogOpen(false)}>
              Cancel
            </Button>
            <Button
              variant="primary"
              size="sm"
              onClick={() => {
                setNewEntryDialogOpen(false);
                addToast("success", "Entry Created", "Stored securely in vault.");
              }}
            >
              Save Entry
            </Button>
          </>
        }
      >
        <div className="flex flex-col gap-4">
          <FieldGroup label="Title" required>
            <Input placeholder="e.g. GitHub" />
          </FieldGroup>
          <FieldGroup label="Username / Email">
            <Input placeholder="user@mypass.app" />
          </FieldGroup>
          <FieldGroup label="Password">
            <PasswordInput placeholder="Enter or generate password..." />
          </FieldGroup>
          <FieldGroup label="Website URL">
            <Input placeholder="https://..." />
          </FieldGroup>
        </div>
      </Dialog>

      {/* Confirm Delete Dialog */}
      <ConfirmDialog
        open={deleteDialogOpen}
        onClose={() => setDeleteDialogOpen(false)}
        title="Delete Vault Entry"
        description={`Are you sure you want to permanently delete '${selectedEntry?.title}'? This action cannot be undone.`}
        confirmLabel="Delete Permanently"
        onConfirm={handleDeleteEntry}
      />

      {/* Toast Notification Manager */}
      <NotificationCenter toasts={toasts} onDismiss={(id) => setToasts((prev) => prev.filter((t) => t.id !== id))} />
    </div>
  );
};
