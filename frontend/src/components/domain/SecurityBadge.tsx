import React from "react";
import { Badge, BadgeVariant } from "../core/Badge";

export type SecurityStatus = "secure" | "weak" | "breached";

export interface SecurityBadgeProps {
  status?: SecurityStatus;
  className?: string;
}

const statusConfig: Record<SecurityStatus, { variant: BadgeVariant; label: string }> = {
  secure: { variant: "success", label: "SECURE ✓" },
  weak: { variant: "warning", label: "Weak" },
  breached: { variant: "danger", label: "Breached" },
};

export const SecurityBadge: React.FC<SecurityBadgeProps> = ({
  status = "secure",
  className = "",
}) => {
  const config = statusConfig[status];

  return (
    <Badge variant={config.variant} className={className}>
      {config.label}
    </Badge>
  );
};
