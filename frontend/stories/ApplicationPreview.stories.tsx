import React, { useState } from "react";
import type { Meta, StoryObj } from "@storybook/react";
import { SidebarItem } from "../src/components/layout/SidebarItem";
import { SearchBar } from "../src/components/layout/SearchBar";
import { SectionHeader } from "../src/components/layout/SectionHeader";
import { VaultCard } from "../src/components/domain/VaultCard";
import { InspectorField } from "../src/components/domain/InspectorField";
import { SecurityBadge } from "../src/components/domain/SecurityBadge";
import { PasswordStrength } from "../src/components/domain/PasswordStrength";
import { FaviconAvatar } from "../src/components/domain/FaviconAvatar";
import { Button } from "../src/components/core/Button";
import { Badge } from "../src/components/core/Badge";
import { Shield, KeyRound, Star, Lock, Plus, Edit2, Trash2 } from "lucide-react";

const meta: Meta = {
  title: "Templates/Application Preview",
  tags: ["autodocs"],
};

export default meta;

export const MockPasswordManager: StoryObj = {
  render: () => {
    const [selectedId, setSelectedId] = useState(1);
    const [searchQuery, setSearchQuery] = useState("");

    const mockVaultItems = [
      { id: 1, title: "GitHub", username: "developer@mypass.app", websiteUrl: "https://github.com", favorite: true, timestamp: "Last used 2 hours ago" },
      { id: 2, title: "Amazon", username: "sameer@amazon.com", websiteUrl: "https://amazon.com", favorite: false, timestamp: "Last used yesterday" },
      { id: 3, title: "Discord", username: "sameer_dev", websiteUrl: "https://discord.com", favorite: true, timestamp: "Last used 3 days ago" },
    ];

    const currentEntry = mockVaultItems.find((i) => i.id === selectedId) || mockVaultItems[0];

    return (
      <div className="flex h-[720px] w-[1280px] bg-[var(--background)] text-[var(--text-primary)] rounded-xl border border-[var(--border-subtle)] overflow-hidden shadow-2xl">
        {/* Left Sidebar (240px) */}
        <aside className="w-[240px] bg-[var(--surface-sidebar)] border-r border-[var(--border-subtle)] p-3 flex flex-col justify-between shrink-0">
          <div className="flex flex-col gap-4">
            <div className="flex items-center gap-2.5 px-2 py-1.5">
              <div className="h-7 w-7 rounded-lg bg-[var(--accent)] flex items-center justify-center font-bold text-white text-xs">
                M
              </div>
              <span className="font-bold text-sm tracking-tight">MyPass v3</span>
              <Badge variant="outline" className="ml-auto text-[10px]">Local</Badge>
            </div>

            <div className="flex flex-col gap-1">
              <SidebarItem icon={Shield} title="All Items" count={12} isSelected={true} />
              <SidebarItem icon={Star} title="Favorites" count={3} />
              <SidebarItem icon={KeyRound} title="Passwords" count={9} />
            </div>
          </div>

          <div className="pt-3 border-t border-[var(--border-subtle)]">
            <SidebarItem icon={Lock} title="Lock Vault" shortcut="⌘L" />
          </div>
        </aside>

        {/* Middle Vault List Column (320px) */}
        <section className="w-[340px] bg-[var(--surface-panel)] border-r border-[var(--border-subtle)] flex flex-col shrink-0">
          <div className="p-3 border-b border-[var(--border-subtle)] flex flex-col gap-3">
            <SearchBar value={searchQuery} onChange={(e) => setSearchQuery(e.target.value)} onClear={() => setSearchQuery("")} />
            <SectionHeader title="Saved Passwords" action={<Button size="sm" leadingIcon={Plus}>New</Button>} />
          </div>

          <div className="flex-1 overflow-y-auto p-3 flex flex-col gap-2">
            {mockVaultItems.map((item) => (
              <VaultCard
                key={item.id}
                id={item.id}
                title={item.title}
                username={item.username}
                websiteUrl={item.websiteUrl}
                isFavorite={item.favorite}
                timestamp={item.timestamp}
                isSelected={selectedId === item.id}
                onItemSelect={(id) => setSelectedId(id)}
              />
            ))}
          </div>
        </section>

        {/* Right Details Inspector (Elastic ~620px) */}
        <main className="flex-1 bg-[var(--background)] p-6 overflow-y-auto flex flex-col justify-between">
          <div className="flex flex-col gap-6">
            {/* Inspector Header */}
            <div className="flex items-start justify-between pb-4 border-b border-[var(--border-subtle)]">
              <div className="flex items-center gap-4">
                <FaviconAvatar title={currentEntry.title} websiteUrl={currentEntry.websiteUrl} size="xl" />
                <div className="flex flex-col gap-1">
                  <div className="flex items-center gap-2">
                    <h1 className="text-2xl font-bold tracking-tight">{currentEntry.title}</h1>
                    <SecurityBadge status="secure" />
                  </div>
                  <span className="text-xs text-[var(--text-muted)]">{currentEntry.websiteUrl}</span>
                </div>
              </div>
              <div className="flex items-center gap-2">
                <Button variant="secondary" size="sm" leadingIcon={Edit2}>Edit</Button>
                <Button variant="destructive" size="sm" leadingIcon={Trash2}>Delete</Button>
              </div>
            </div>

            {/* Inspector Field Cards */}
            <div className="grid grid-cols-1 gap-3">
              <InspectorField label="Username / Email" value={currentEntry.username} />
              <InspectorField label="Password" value="s3cur3P@ssw0rd!2026" isSensitive revealable />
              <InspectorField label="Website URL" value={currentEntry.websiteUrl} actionUrl={currentEntry.websiteUrl} />
            </div>

            {/* Password Strength Section */}
            <div className="p-4 bg-[var(--surface-card)] border border-[var(--border-subtle)] rounded-xl">
              <PasswordStrength score={4} />
            </div>
          </div>

          <div className="text-xs text-[var(--text-muted)] text-center pt-4 border-t border-[var(--border-subtle)]">
            Encrypted with AES-256-GCM & Argon2id • Last modified 2 hours ago
          </div>
        </main>
      </div>
    );
  },
};
