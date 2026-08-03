import type { Meta, StoryObj } from "@storybook/react";
import { WorkspaceLayout } from "../src/components/workspace/WorkspaceLayout";

const meta: Meta<typeof WorkspaceLayout> = {
  title: "Templates/Workspace Preview",
  component: WorkspaceLayout,
  tags: ["autodocs"],
  parameters: {
    layout: "fullscreen",
  },
};

export default meta;
type Story = StoryObj<typeof WorkspaceLayout>;

export const FullDesktopWorkspace: Story = {
  render: () => <WorkspaceLayout />,
};
