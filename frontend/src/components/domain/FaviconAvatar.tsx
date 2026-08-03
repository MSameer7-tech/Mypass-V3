import React from "react";
import { Avatar, AvatarProps } from "../core/Avatar";

export interface FaviconAvatarProps extends Omit<AvatarProps, "src"> {
  websiteUrl?: string;
  title?: string;
  faviconUrl?: string;
}

export const FaviconAvatar: React.FC<FaviconAvatarProps> = ({
  websiteUrl,
  title,
  faviconUrl,
  size = "md",
  className = "",
  ...props
}) => {
  const fallbackInitials = title || websiteUrl || "?";

  return (
    <Avatar
      src={faviconUrl}
      alt={title || "Favicon"}
      initials={fallbackInitials}
      size={size}
      className={`shrink-0 ${className}`}
      {...props}
    />
  );
};
