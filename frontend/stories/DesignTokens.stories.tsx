import React from "react";
import type { Meta, StoryObj } from "@storybook/react";

const meta: Meta = {
  title: "Design Tokens/Colors",
  tags: ["autodocs"],
};

export default meta;

export const Palette: StoryObj = {
  render: () => (
    <div className="flex flex-col gap-6 p-6 bg-[var(--background)] text-[var(--text-primary)] rounded-xl border border-[var(--border-subtle)]">
      <h2 className="text-xl font-bold">MyPass Color Design Tokens</h2>
      <div className="grid grid-cols-2 sm:grid-cols-4 gap-4">
        {[
          { name: "--background", color: "#0F1015" },
          { name: "--surface-sidebar", color: "#14151B" },
          { name: "--surface-panel", color: "#181920" },
          { name: "--surface-card", color: "#1E202A" },
          { name: "--surface-card-hover", color: "#262834" },
          { name: "--surface-card-selected", color: "#2D303E" },
          { name: "--accent", color: "#3B82F6" },
          { name: "--danger", color: "#EF4444" },
          { name: "--success", color: "#10B981" },
          { name: "--warning", color: "#F59E0B" },
        ].map((token) => (
          <div key={token.name} className="flex flex-col gap-2 p-3 rounded-lg border border-[var(--border-subtle)] bg-[var(--surface-panel)]">
            <div className="h-12 w-full rounded-md border border-white/10" style={{ backgroundColor: token.color }} />
            <span className="text-xs font-mono text-[var(--text-secondary)]">{token.name}</span>
            <span className="text-xs font-mono text-[var(--text-muted)]">{token.color}</span>
          </div>
        ))}
      </div>
    </div>
  ),
};
