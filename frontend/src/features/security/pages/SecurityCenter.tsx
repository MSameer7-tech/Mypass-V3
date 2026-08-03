import React, { useMemo } from "react";
import { analyzeVaultHealth } from "../engine/healthEngine";
import { Card } from "../../../components/core/Card";
import { Badge } from "../../../components/core/Badge";
import { Button } from "../../../components/core/Button";
import { Shield, ShieldAlert, AlertTriangle, Key, RefreshCw } from "lucide-react";
import { Icon } from "../../../components/core/Icon";
import { MockVaultEntry } from "../../../mocks/vault";

export interface SecurityCenterProps {
  entries: MockVaultEntry[];
  onFixEntry?: (id: number) => void;
}

export const SecurityCenter: React.FC<SecurityCenterProps> = ({ entries, onFixEntry }) => {
  const report = useMemo(() => analyzeVaultHealth(entries), [entries]);

  const scoreColor =
    report.overallScore >= 80
      ? "text-[var(--success)] border-emerald-900/40"
      : report.overallScore >= 50
      ? "text-[var(--warning)] border-amber-900/40"
      : "text-[var(--danger)] border-red-900/40";

  return (
    <div className="h-full w-full bg-[var(--background)] p-8 overflow-y-auto flex flex-col gap-8 select-text">
      {/* Header Branding */}
      <div className="flex items-center justify-between border-b border-[var(--border-subtle)] pb-4">
        <div className="flex items-center gap-3">
          <div className="h-10 w-10 rounded-xl bg-[var(--accent)] flex items-center justify-center shadow-md">
            <Icon icon={Shield} size="md" tone="primary" />
          </div>
          <div className="flex flex-col">
            <h1 className="text-xl font-bold text-[var(--text-primary)]">Security Center</h1>
            <span className="text-xs text-[var(--text-muted)]">Offline Password Health & Breach Auditor</span>
          </div>
        </div>
        <Badge variant="outline" className="text-xs font-mono">100% Offline Engine</Badge>
      </div>

      {/* Top Metrics Cards Grid */}
      <div className="grid grid-cols-1 md:grid-cols-5 gap-4">
        {/* Score Card */}
        <Card variant="elevated" className={`flex flex-col items-center justify-center p-6 text-center border-l-4 ${scoreColor}`}>
          <span className="text-3xl font-black font-mono tracking-tight text-[var(--text-primary)]">{report.overallScore}/100</span>
          <span className="text-xs font-semibold text-[var(--text-muted)] mt-1">Vault Health Score</span>
        </Card>

        {/* Metric 2: Total */}
        <Card variant="default" className="flex flex-col p-4">
          <span className="text-xs text-[var(--text-muted)] font-medium">Total Passwords</span>
          <span className="text-2xl font-bold text-[var(--text-primary)] mt-1">{report.totalPasswords}</span>
          <span className="text-[11px] text-[var(--success)] mt-1">{report.strongCount} Strong</span>
        </Card>

        {/* Metric 3: Weak */}
        <Card variant="default" className="flex flex-col p-4">
          <span className="text-xs text-[var(--text-muted)] font-medium">Weak Passwords</span>
          <span className="text-2xl font-bold text-[var(--warning)] mt-1">{report.weakCount}</span>
          <span className="text-[11px] text-[var(--text-muted)] mt-1">Low Complexity</span>
        </Card>

        {/* Metric 4: Reused */}
        <Card variant="default" className="flex flex-col p-4">
          <span className="text-xs text-[var(--text-muted)] font-medium">Reused Passwords</span>
          <span className="text-2xl font-bold text-amber-500 mt-1">{report.reusedCount}</span>
          <span className="text-[11px] text-[var(--text-muted)] mt-1">Duplicate Hashes</span>
        </Card>

        {/* Metric 5: Breached */}
        <Card variant="default" className="flex flex-col p-4">
          <span className="text-xs text-[var(--text-muted)] font-medium">Breached</span>
          <span className="text-2xl font-bold text-[var(--danger)] mt-1">{report.breachedCount}</span>
          <span className="text-[11px] text-[var(--danger)] mt-1">HIBP Matched</span>
        </Card>
      </div>

      {/* Recommendations Banner */}
      <div className="p-4 bg-[var(--surface-panel)] border border-[var(--border-subtle)] rounded-xl flex flex-col gap-2">
        <div className="flex items-center gap-2 text-xs font-bold text-[var(--text-secondary)]">
          <Icon icon={RefreshCw} size="xs" tone="accent" />
          <span>Security Recommendations</span>
        </div>
        <ul className="flex flex-col gap-1.5 list-disc list-inside text-xs text-[var(--text-muted)]">
          {report.recommendations.map((rec, i) => (
            <li key={i}>{rec}</li>
          ))}
        </ul>
      </div>

      {/* Security Issues List */}
      <div className="flex flex-col gap-4">
        <h2 className="text-sm font-bold text-[var(--text-primary)]">Security Audit Findings ({report.issues.length})</h2>

        {report.issues.length === 0 ? (
          <div className="p-8 text-center bg-[var(--surface-card)] rounded-xl border border-[var(--border-subtle)] text-xs text-[var(--text-muted)]">
            No security issues detected. Your vault meets optimal security standards.
          </div>
        ) : (
          <div className="grid grid-cols-1 gap-3">
            {report.issues.map((issue, idx) => (
              <div
                key={idx}
                className="flex items-center justify-between p-4 bg-[var(--surface-card)] border border-[var(--border-subtle)] rounded-xl hover:bg-[var(--surface-card-hover)] transition-all"
              >
                <div className="flex items-center gap-3">
                  <div className={`p-2.5 rounded-lg shrink-0 ${issue.severity === "critical" ? "bg-[var(--danger-surface)]" : "bg-[var(--warning-surface)]"}`}>
                    <Icon icon={issue.severity === "critical" ? ShieldAlert : AlertTriangle} size="sm" tone={issue.severity === "critical" ? "danger" : "warning"} />
                  </div>
                  <div className="flex flex-col gap-0.5">
                    <div className="flex items-center gap-2">
                      <span className="text-sm font-bold text-[var(--text-primary)]">{issue.entryTitle}</span>
                      <Badge variant={issue.severity === "critical" ? "danger" : "warning"}>{issue.type}</Badge>
                    </div>
                    <span className="text-xs text-[var(--text-muted)]">{issue.description}</span>
                  </div>
                </div>

                {onFixEntry && (
                  <Button
                    variant="secondary"
                    size="sm"
                    leadingIcon={Key}
                    onClick={() => onFixEntry(issue.entryId)}
                  >
                    Fix Password
                  </Button>
                )}
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
};
