import { MockVaultEntry } from "../../../mocks/vault";

export type SecurityIssueType =
  | "WEAK_PASSWORD"
  | "REUSED_PASSWORD"
  | "BREACHED_PASSWORD"
  | "SHORT_PASSWORD"
  | "LOW_ENTROPY";

export interface SecurityIssue {
  entryId: number;
  entryTitle: string;
  type: SecurityIssueType;
  description: string;
  severity: "critical" | "warning" | "info";
}

export interface SecurityAuditReport {
  overallScore: number;
  totalPasswords: number;
  strongCount: number;
  weakCount: number;
  reusedCount: number;
  breachedCount: number;
  issues: SecurityIssue[];
  recommendations: string[];
}

export function analyzeVaultHealth(entries: MockVaultEntry[]): SecurityAuditReport {
  const issues: SecurityIssue[] = [];
  const passwordCounts: Record<string, number> = {};

  let strongCount = 0;
  let weakCount = 0;
  let reusedCount = 0;
  let breachedCount = 0;

  // Track password frequencies for reuse detection
  entries.forEach((e) => {
    if (e.password) {
      passwordCounts[e.password] = (passwordCounts[e.password] || 0) + 1;
    }
  });

  entries.forEach((e) => {
    const pwd = e.password || "";

    // 1. Weak / Short Check
    if (pwd.length < 8) {
      weakCount++;
      issues.push({
        entryId: e.id,
        entryTitle: e.title,
        type: "SHORT_PASSWORD",
        description: "Password is fewer than 8 characters long.",
        severity: "critical",
      });
    } else if (e.strengthScore <= 2) {
      weakCount++;
      issues.push({
        entryId: e.id,
        entryTitle: e.title,
        type: "WEAK_PASSWORD",
        description: "Password lacks complexity or entropy.",
        severity: "warning",
      });
    } else {
      strongCount++;
    }

    // 2. Reuse Check
    if (pwd && passwordCounts[pwd] > 1) {
      reusedCount++;
      issues.push({
        entryId: e.id,
        entryTitle: e.title,
        type: "REUSED_PASSWORD",
        description: `Password is reused across ${passwordCounts[pwd]} entries.`,
        severity: "critical",
      });
    }

    // 3. Breached Check
    if (e.securityStatus === "breached") {
      breachedCount++;
      issues.push({
        entryId: e.id,
        entryTitle: e.title,
        type: "BREACHED_PASSWORD",
        description: "Password has appeared in a known data breach.",
        severity: "critical",
      });
    }
  });

  // Calculate Overall Score (0 - 100)
  const total = Math.max(1, entries.length);
  const deductions = weakCount * 10 + reusedCount * 15 + breachedCount * 25;
  const overallScore = Math.max(0, Math.min(100, 100 - Math.round(deductions / total)));

  const recommendations: string[] = [];
  if (breachedCount > 0) recommendations.push(`Immediately update ${breachedCount} breached passwords.`);
  if (reusedCount > 0) recommendations.push(`Generate unique passwords for ${reusedCount} reused accounts.`);
  if (weakCount > 0) recommendations.push(`Strengthen ${weakCount} weak passwords.`);
  if (recommendations.length === 0) recommendations.push("Your vault health score is optimal! Keep up the good security habits.");

  return {
    overallScore,
    totalPasswords: entries.length,
    strongCount,
    weakCount,
    reusedCount,
    breachedCount,
    issues,
    recommendations,
  };
}
