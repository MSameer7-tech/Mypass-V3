import React, { useState } from "react";
import type { Meta, StoryObj } from "@storybook/react";
import { Dialog } from "../src/components/overlay/Dialog";
import { ConfirmDialog } from "../src/components/overlay/ConfirmDialog";
import { Sheet } from "../src/components/overlay/Sheet";
import { NotificationCenter } from "../src/components/overlay/NotificationCenter";
import { CommandPalette } from "../src/components/power/CommandPalette";
import { Button } from "../src/components/core/Button";
import { Input } from "../src/components/core/Input";
import { FieldGroup } from "../src/components/layout/FieldGroup";

const meta: Meta = {
  title: "Overlays/Showcase",
  tags: ["autodocs"],
};

export default meta;

export const OverlaySystemShowcase: StoryObj = {
  render: () => {
    const [dialogOpen, setDialogOpen] = useState(false);
    const [confirmOpen, setConfirmOpen] = useState(false);
    const [sheetOpen, setSheetOpen] = useState(false);
    const [commandOpen, setCommandOpen] = useState(false);
    const [toasts, setToasts] = useState<any[]>([]);

    const addToast = (variant: "success" | "error" | "warning" | "info", title: string, description: string) => {
      const newToast = {
        id: Date.now().toString(),
        variant,
        title,
        description,
      };
      setToasts((prev) => [...prev, newToast]);
    };

    return (
      <div className="flex flex-col gap-6 p-8 bg-[var(--background)] text-[var(--text-primary)] rounded-xl border border-[var(--border-subtle)] min-h-[480px]">
        <h2 className="text-xl font-bold">Overlay & Feedback System Showcase</h2>

        <div className="flex flex-wrap items-center gap-3">
          <Button variant="primary" onClick={() => setDialogOpen(true)}>Open Dialog</Button>
          <Button variant="destructive" onClick={() => setConfirmOpen(true)}>Open Confirm Dialog</Button>
          <Button variant="secondary" onClick={() => setSheetOpen(true)}>Open Slide Sheet</Button>
          <Button variant="secondary" onClick={() => setCommandOpen(true)}>Open Command Palette (⌘K)</Button>
        </div>

        <div className="flex flex-wrap items-center gap-3 pt-4 border-t border-[var(--border-subtle)]">
          <Button size="sm" variant="ghost" onClick={() => addToast("success", "Password Copied", "Copied to clipboard. Will clear in 30s.")}>Trigger Success Toast</Button>
          <Button size="sm" variant="ghost" onClick={() => addToast("error", "Breach Detected", "This password appeared in a data breach.")}>Trigger Error Toast</Button>
          <Button size="sm" variant="ghost" onClick={() => addToast("warning", "Weak Master Password", "Consider using a longer master password.")}>Trigger Warning Toast</Button>
        </div>

        {/* Dialog */}
        <Dialog
          open={dialogOpen}
          onClose={() => setDialogOpen(false)}
          title="Create New Vault Entry"
          description="Enter credentials to store securely in your local vault."
          footer={
            <>
              <Button variant="ghost" size="sm" onClick={() => setDialogOpen(false)}>Cancel</Button>
              <Button variant="primary" size="sm" onClick={() => setDialogOpen(false)}>Save Entry</Button>
            </>
          }
        >
          <div className="flex flex-col gap-4">
            <FieldGroup label="Title" required>
              <Input placeholder="e.g. GitHub" />
            </FieldGroup>
            <FieldGroup label="Username / Email">
              <Input placeholder="user@example.com" />
            </FieldGroup>
          </div>
        </Dialog>

        {/* Confirm Dialog */}
        <ConfirmDialog
          open={confirmOpen}
          onClose={() => setConfirmOpen(false)}
          title="Delete Vault Entry"
          description="Are you sure you want to permanently delete 'GitHub'? This action cannot be reversed."
          confirmLabel="Delete Permanently"
          onConfirm={() => setConfirmOpen(false)}
        />

        {/* Sheet */}
        <Sheet
          open={sheetOpen}
          onClose={() => setSheetOpen(false)}
          title="Security Audit Handoff"
          description="Detailed breakdown of your vault health score."
          side="right"
        >
          <div className="flex flex-col gap-3 text-xs text-[var(--text-secondary)]">
            <p>All passwords are encrypted locally using AES-256-GCM.</p>
          </div>
        </Sheet>

        {/* Command Palette */}
        <CommandPalette open={commandOpen} onClose={() => setCommandOpen(false)} />

        {/* Toast Manager */}
        <NotificationCenter toasts={toasts} onDismiss={(id) => setToasts((prev) => prev.filter((t) => t.id !== id))} />
      </div>
    );
  },
};
