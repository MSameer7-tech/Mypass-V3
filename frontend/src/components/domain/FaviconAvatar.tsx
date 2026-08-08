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
  
  // Try to extract domain from websiteUrl to fetch favicon
  let resolvedFaviconUrl = faviconUrl;
  if (!resolvedFaviconUrl && websiteUrl) {
    try {
      // Add protocol if missing to successfully parse URL
      const urlToParse = websiteUrl.startsWith("http") ? websiteUrl : `https://${websiteUrl}`;
      const url = new URL(urlToParse);
      // Use Google's favicon service which is reliable and provides good quality
      resolvedFaviconUrl = `https://s2.googleusercontent.com/s2/favicons?domain=${url.hostname}&sz=64`;
    } catch (e) {
      // Invalid URL, fallback to initials
    }
  }

  return (
    <Avatar
      src={resolvedFaviconUrl}
      alt={title || "Favicon"}
      initials={fallbackInitials}
      size={size}
      className={`shrink-0 ${className}`}
      {...props}
    />
  );
};
