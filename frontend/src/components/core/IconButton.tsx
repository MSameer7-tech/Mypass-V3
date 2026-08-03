import React from "react";
import { Button, ButtonProps } from "./Button";
import { Icon, IconProps } from "./Icon";

export interface IconButtonProps extends Omit<ButtonProps, "children"> {
  icon: IconProps["icon"];
  label: string;
  tone?: IconProps["tone"];
}

export const IconButton = React.forwardRef<HTMLButtonElement, IconButtonProps>(
  ({ icon, label, tone = "primary", size = "md", ...props }, ref) => {
    return (
      <Button ref={ref} size="icon" aria-label={label} title={label} {...props}>
        <Icon icon={icon} size={size === "sm" ? "sm" : "md"} tone={tone} />
      </Button>
    );
  }
);

IconButton.displayName = "IconButton";
