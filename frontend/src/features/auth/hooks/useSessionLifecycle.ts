import { useEffect } from "react";
import { useAuthStore } from "../../../stores/auth/useAuthStore";
import { useSettingsStore } from "../../../stores/settings/useSettingsStore";

export function useSessionLifecycle() {
  const sessionState = useAuthStore((s) => s.sessionState);
  const autoLockMinutes = useSettingsStore((s) => s.autoLockMinutes);
  const lastActivityTimestamp = useAuthStore((s) => s.lastActivityTimestamp);
  const resetActivityTimer = useAuthStore((s) => s.resetActivityTimer);
  const lockVault = useAuthStore((s) => s.lockVault);

  // Interaction Event Listeners
  useEffect(() => {
    if (sessionState !== "UNLOCKED") return;

    const handleUserActivity = () => {
      resetActivityTimer();
    };

    window.addEventListener("mousemove", handleUserActivity);
    window.addEventListener("keydown", handleUserActivity);
    window.addEventListener("mousedown", handleUserActivity);
    window.addEventListener("focus", handleUserActivity);
    document.addEventListener("visibilitychange", handleUserActivity);

    return () => {
      window.removeEventListener("mousemove", handleUserActivity);
      window.removeEventListener("keydown", handleUserActivity);
      window.removeEventListener("mousedown", handleUserActivity);
      window.removeEventListener("focus", handleUserActivity);
      document.removeEventListener("visibilitychange", handleUserActivity);
    };
  }, [sessionState, resetActivityTimer]);

  // Auto-Lock Timer Interval
  useEffect(() => {
    if (sessionState !== "UNLOCKED" || autoLockMinutes <= 0) return;

    const interval = setInterval(() => {
      const idleTimeMs = Date.now() - lastActivityTimestamp;
      const maxIdleMs = autoLockMinutes * 60 * 1000;

      if (idleTimeMs >= maxIdleMs) {
        console.log("[AutoLock] Vault idle timeout reached. Locking vault...");
        lockVault();
      }
    }, 5000);

    return () => clearInterval(interval);
  }, [sessionState, autoLockMinutes, lastActivityTimestamp, lockVault]);
}
