import type { Meta, StoryObj } from "@storybook/react";
import { Input, PasswordInput, SearchInput } from "./Input";
import { Lock, Mail } from "lucide-react";

const meta: Meta<typeof Input> = {
  title: "Primitives/Input",
  component: Input,
  tags: ["autodocs"],
};

export default meta;
type Story = StoryObj<typeof Input>;

export const Default: Story = {
  args: {
    label: "Username or Email",
    placeholder: "user@example.com",
    leadingIcon: Mail,
  },
};

export const Password: Story = {
  render: () => <PasswordInput label="Master Password" placeholder="Enter master password..." leadingIcon={Lock} />,
};

export const Search: Story = {
  render: () => <SearchInput placeholder="Search passwords, notes, tags..." />,
};

export const WithError: Story = {
  args: {
    label: "Master Password",
    value: "wrongpass",
    error: "Invalid master password. Please try again.",
  },
};
