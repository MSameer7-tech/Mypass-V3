import React from "react";

export interface SkeletonProps extends React.HTMLAttributes<HTMLDivElement> {
  variant?: "text" | "circular" | "rectangular" | "card" | "listRow";
  width?: string | number;
  height?: string | number;
}

export const Skeleton: React.FC<SkeletonProps> = ({
  variant = "text",
  width,
  height,
  className = "",
  style,
  ...props
}) => {
  if (variant === "card") {
    return (
      <div className={`p-4 bg-[var(--surface-card)] border border-[var(--border-subtle)] rounded-xl animate-pulse flex flex-col gap-3 ${className}`}>
        <div className="flex items-center gap-3">
          <div className="h-10 w-10 bg-[var(--surface-card-selected)] rounded-lg shrink-0" />
          <div className="flex flex-col gap-1.5 flex-1">
            <div className="h-4 w-3/4 bg-[var(--surface-card-selected)] rounded" />
            <div className="h-3 w-1/2 bg-[var(--surface-card-selected)] rounded opacity-60" />
          </div>
        </div>
      </div>
    );
  }

  if (variant === "listRow") {
    return (
      <div className={`h-[74px] p-3 bg-[var(--surface-card)] border border-[var(--border-subtle)] rounded-xl animate-pulse flex items-center gap-3 ${className}`}>
        <div className="h-11 w-11 bg-[var(--surface-card-selected)] rounded-xl shrink-0" />
        <div className="flex flex-col gap-2 flex-1">
          <div className="h-4 w-2/3 bg-[var(--surface-card-selected)] rounded" />
          <div className="h-3 w-1/3 bg-[var(--surface-card-selected)] rounded opacity-60" />
        </div>
      </div>
    );
  }

  const variantStyle =
    variant === "circular"
      ? "rounded-full"
      : variant === "rectangular"
      ? "rounded-lg"
      : "rounded";

  return (
    <div
      className={`animate-pulse bg-[var(--surface-card-selected)] ${variantStyle} ${className}`}
      style={{
        width: width ?? (variant === "text" ? "100%" : undefined),
        height: height ?? (variant === "text" ? "1em" : undefined),
        ...style,
      }}
      {...props}
    />
  );
};
