import React from "react";
import { Spinner } from "../core/Spinner";

export interface LoadingOverlayProps {
  message?: string;
  isFullWindow?: boolean;
}

export const LoadingOverlay: React.FC<LoadingOverlayProps> = ({
  message = "Loading...",
  isFullWindow = false,
}) => {
  const containerStyle = isFullWindow
    ? "fixed inset-0 z-50 bg-[var(--background)]/80 backdrop-blur-sm"
    : "absolute inset-0 z-40 bg-[var(--surface-panel)]/70 backdrop-blur-xs rounded-xl";

  return (
    <div className={`flex flex-col items-center justify-center gap-3 p-6 ${containerStyle}`}>
      <Spinner size="lg" />
      <span className="text-xs font-semibold text-[var(--text-secondary)] tracking-wide">{message}</span>
    </div>
  );
};
