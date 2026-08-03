import React from "react";
import type { Meta, StoryObj } from "@storybook/react";
import { Badge } from "../src/components/core/Badge";
import { Card } from "../src/components/core/Card";
import { Avatar } from "../src/components/core/Avatar";
import { Spinner } from "../src/components/core/Spinner";
import { Skeleton } from "../src/components/core/Skeleton";

const meta: Meta = {
  title: "Primitives/Overview",
  tags: ["autodocs"],
};

export default meta;

export const Showcase: StoryObj = {
  render: () => (
    <div className="flex flex-col gap-6 p-6 bg-[var(--background)] text-[var(--text-primary)] rounded-xl border border-[var(--border-subtle)]">
      <h2 className="text-xl font-bold">Core Primitives Overview</h2>
      
      <div className="flex flex-col gap-3">
        <h3 className="text-sm font-semibold text-[var(--text-secondary)]">Badges</h3>
        <div className="flex items-center gap-2">
          <Badge variant="default">Default</Badge>
          <Badge variant="success">SECURE ✓</Badge>
          <Badge variant="warning">Weak</Badge>
          <Badge variant="danger">Breached</Badge>
          <Badge variant="outline">Work</Badge>
        </div>
      </div>

      <div className="flex flex-col gap-3">
        <h3 className="text-sm font-semibold text-[var(--text-secondary)]">Avatars</h3>
        <div className="flex items-center gap-3">
          <Avatar initials="GitHub" size="sm" />
          <Avatar initials="Amazon" size="md" />
          <Avatar initials="Discord" size="lg" />
          <Avatar initials="MyPass" size="xl" />
        </div>
      </div>

      <div className="flex flex-col gap-3">
        <h3 className="text-sm font-semibold text-[var(--text-secondary)]">Cards</h3>
        <div className="grid grid-cols-2 gap-4">
          <Card variant="default">Default Card</Card>
          <Card variant="interactive">Interactive Hover Card</Card>
        </div>
      </div>

      <div className="flex flex-col gap-3">
        <h3 className="text-sm font-semibold text-[var(--text-secondary)]">Skeletons & Spinners</h3>
        <div className="flex items-center gap-4">
          <Spinner size="md" />
          <div className="flex-1">
            <Skeleton variant="listRow" />
          </div>
        </div>
      </div>
    </div>
  ),
};
