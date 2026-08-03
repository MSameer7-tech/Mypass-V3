import React, { useState } from "react";

export interface AvatarProps extends React.HTMLAttributes<HTMLDivElement> {
  src?: string;
  alt?: string;
  initials?: string;
  size?: "sm" | "md" | "lg" | "xl";
}

const sizeStyles: Record<string, string> = {
  sm: "h-6 w-6 text-xs rounded-md",
  md: "h-8 w-8 text-sm rounded-lg",
  lg: "h-11 w-11 text-base rounded-xl",
  xl: "h-14 w-14 text-xl rounded-xl font-bold",
};

export const Avatar: React.FC<AvatarProps> = ({
  src,
  alt = "",
  initials,
  size = "md",
  className = "",
  ...props
}) => {
  const [imageError, setImageError] = useState(false);

  const renderFallback = () => {
    const char = initials ? initials.charAt(0).toUpperCase() : "?";
    return (
      <span className="font-semibold text-[var(--text-secondary)] select-none">
        {char}
      </span>
    );
  };

  return (
    <div
      className={`relative inline-flex items-center justify-center bg-[var(--surface-card-selected)] border border-[var(--border-subtle)] overflow-hidden shrink-0 ${sizeStyles[size]} ${className}`}
      {...props}
    >
      {src && !imageError ? (
        <img
          src={src}
          alt={alt}
          onError={() => setImageError(true)}
          className="h-full w-full object-cover"
        />
      ) : (
        renderFallback()
      )}
    </div>
  );
};
