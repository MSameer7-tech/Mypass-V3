import React from "react";

export interface PasswordStrengthProps {
  score?: number; // 0 to 4
  label?: string;
  className?: string;
}

const scoreConfig: Record<number, { label: string; color: string }> = {
  0: { label: "Very Weak", color: "bg-red-500" },
  1: { label: "Weak", color: "bg-red-400" },
  2: { label: "Moderate", color: "bg-amber-400" },
  3: { label: "Strong", color: "bg-emerald-400" },
  4: { label: "Very Strong", color: "bg-emerald-500" },
};

export const PasswordStrength: React.FC<PasswordStrengthProps> = ({
  score = 0,
  label,
  className = "",
}) => {
  const boundedScore = Math.max(0, Math.min(4, score));
  const config = scoreConfig[boundedScore];
  const displayLabel = label || config.label;

  return (
    <div className={`flex flex-col gap-1.5 w-full ${className}`}>
      <div className="flex items-center justify-between text-xs">
        <span className="text-[var(--text-muted)] font-medium">Password Strength</span>
        <span className="font-semibold text-[var(--text-secondary)]">{displayLabel}</span>
      </div>
      <div className="flex items-center gap-1.5 h-1.5 w-full">
        {[0, 1, 2, 3].map((index) => (
          <div
            key={index}
            className={`h-full flex-1 rounded-full transition-all duration-200 ${
              index <= boundedScore - 1 ? config.color : "bg-[var(--surface-card-selected)]"
            }`}
          />
        ))}
      </div>
    </div>
  );
};
