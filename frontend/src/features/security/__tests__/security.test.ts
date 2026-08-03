import { describe, it, expect } from "vitest";
import { analyzeVaultHealth } from "../engine/healthEngine";
import { MockVaultEntry } from "../../../mocks/vault";

describe("Security Health Analysis Engine Integration Tests", () => {
  it("correctly flags short and weak passwords", () => {
    const mockEntries: MockVaultEntry[] = [
      { id: 1, title: "Short", username: "u1", password: "123", websiteUrl: "a.com", favorite: false, category: "Passwords", securityStatus: "weak", strengthScore: 1, updatedAt: "now" },
      { id: 2, title: "Strong", username: "u2", password: "S3cur3P@ssw0rd!2026", websiteUrl: "b.com", favorite: false, category: "Passwords", securityStatus: "secure", strengthScore: 4, updatedAt: "now" },
    ];

    const report = analyzeVaultHealth(mockEntries);
    expect(report.totalPasswords).toBe(2);
    expect(report.weakCount).toBe(1);
    expect(report.strongCount).toBe(1);
    expect(report.issues).toHaveLength(1);
    expect(report.issues[0].type).toBe("SHORT_PASSWORD");
  });

  it("correctly flags reused passwords across multiple entries", () => {
    const mockEntries: MockVaultEntry[] = [
      { id: 1, title: "Site A", username: "u1", password: "SamePassword123!", websiteUrl: "a.com", favorite: false, category: "Passwords", securityStatus: "secure", strengthScore: 4, updatedAt: "now" },
      { id: 2, title: "Site B", username: "u2", password: "SamePassword123!", websiteUrl: "b.com", favorite: false, category: "Passwords", securityStatus: "secure", strengthScore: 4, updatedAt: "now" },
    ];

    const report = analyzeVaultHealth(mockEntries);
    expect(report.reusedCount).toBe(2);
    expect(report.issues.some((i) => i.type === "REUSED_PASSWORD")).toBe(true);
  });
});
