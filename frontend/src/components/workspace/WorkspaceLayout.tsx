import React, { useMemo } from "react";
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
import { Plus } from "lucide-react";

export const WorkspaceLayout: React.FC = () => {
  // Store Selectors (Prevents re-renders)
  const entries = useVaultStore((s) => s.entries);
  const selectedId = useVaultStore((s) => s.selectedEntryId);
  const activeCategory = useVaultStore((s) => s.selectedCategory);
  const selectEntry = useVaultStore((s) => s.selectEntry);
  const toggleFavorite = useVaultStore((s) => s.toggleFavorite);
  const deleteEntry = useVaultStore((s) => s.deleteEntry);
  const setSelectedCategory = useVaultStore((s) => s.setSelectedCategory);

  const searchQuery = useSearchStore((s) => s.query);
  const setSearchQuery = useSearchStore((s) => s.setSearchQuery);
  const commandPaletteOpen = useSearchStore((s) => s.commandPaletteOpen);
  const setCommandPaletteOpen = useSearchStore((s) => s.setCommandPaletteOpen);

  const activeDialog = useUIStore((s) => s.activeDialog);
  const openDialog = useUIStore((s) => s.openDialog);
  const closeDialog = useUIStore((s) => s.closeDialog);

  const [toasts, setToasts] = React.useState<any[]>([]);

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

  const addToast = (variant: "success" | "error" | "warning" | "info", title: string, description?: string) => {
    setToasts((prev) => [...prev, { id: Date.now().toString(), variant, title, description }]);
  };

  const handleConfirmDelete = () => {
    if (!selectedEntry) return;
    deleteEntry(selectedEntry.id);
    closeDialog();
    addToast("success", "Entry Deleted", `'${selectedEntry.title}' was removed.`);
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

          <VaultList
            entries={filteredEntries}
            selectedId={selectedEntry?.id}
            onSelectEntry={selectEntry}
            onToggleFavorite={(id, e) => {
              e.stopPropagation();
              toggleFavorite(id);
            }}
          />
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
        description="Add credentials to store locally in your vault."
        footer={
          <>
            <Button variant="ghost" size="sm" onClick={closeDialog}>
              Cancel
            </Button>
            <Button
              variant="primary"
              size="sm"
              onClick={() => {
                closeDialog();
                addToast("success", "Entry Created", "Stored in vault.");
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
        </div>
      </Dialog>

      {/* Confirm Delete Dialog */}
      <ConfirmDialog
        open={activeDialog === "deleteConfirm"}
        onClose={closeDialog}
        title="Delete Vault Entry"
        description={`Are you sure you want to permanently delete '${selectedEntry?.title}'? This action cannot be undone.`}
        confirmLabel="Delete Permanently"
        onConfirm={handleConfirmDelete}
      />

      <NotificationCenter toasts={toasts} onDismiss={(id) => setToasts((prev) => prev.filter((t) => t.id !== id))} />
    </div>
  );
};
