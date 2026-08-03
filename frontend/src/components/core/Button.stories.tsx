import type { Meta, StoryObj } from "@storybook/react";
import { Button } from "./Button";
import { KeyRound, ArrowRight } from "lucide-react";

const meta: Meta<typeof Button> = {
  title: "Primitives/Button",
  component: Button,
  tags: ["autodocs"],
  argTypes: {
    variant: {
      control: "select",
      options: ["primary", "secondary", "ghost", "destructive", "link"],
    },
    size: {
      control: "select",
      options: ["sm", "md", "lg", "icon"],
    },
  },
};

export default meta;
type Story = StoryObj<typeof Button>;

export const Primary: Story = {
  args: {
    children: "Unlock Vault",
    variant: "primary",
    size: "md",
  },
};

export const WithIcons: Story = {
  args: {
    children: "Generate Password",
    leadingIcon: KeyRound,
    trailingIcon: ArrowRight,
    variant: "secondary",
  },
};

export const Loading: Story = {
  args: {
    children: "Unlocking...",
    isLoading: true,
    variant: "primary",
  },
};

export const Destructive: Story = {
  args: {
    children: "Delete Entry",
    variant: "destructive",
  },
};
