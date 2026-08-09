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
      const { sessionState, lastActivityTimestamp, lockVault } = useAuthStore.getState();
      const maxIdleMs = useSettingsStore.getState().autoLockMinutes * 60 * 1000;
      
      if (sessionState === "UNLOCKED" && maxIdleMs > 0) {
        if (Date.now() - lastActivityTimestamp >= maxIdleMs) {
          lockVault();
          return;
        }
      }
      resetActivityTimer();
    };

    const handleVisibilityChange = () => {
      if (document.visibilityState === 'visible') {
        handleUserActivity();
      }
    };

    window.addEventListener("mousemove", handleUserActivity);
    window.addEventListener("keydown", handleUserActivity);
    window.addEventListener("mousedown", handleUserActivity);
    window.addEventListener("focus", handleUserActivity);
    document.addEventListener("visibilitychange", handleVisibilityChange);

    return () => {
      window.removeEventListener("mousemove", handleUserActivity);
      window.removeEventListener("keydown", handleUserActivity);
      window.removeEventListener("mousedown", handleUserActivity);
      window.removeEventListener("focus", handleUserActivity);
      document.removeEventListener("visibilitychange", handleVisibilityChange);
    };
  }, [sessionState, resetActivityTimer]);

  // Auto-Lock Timer Interval
  useEffect(() => {
    if (sessionState !== "UNLOCKED" || autoLockMinutes <= 0) return;

    const checkLock = () => {
      const idleTimeMs = Date.now() - lastActivityTimestamp;
      const maxIdleMs = autoLockMinutes * 60 * 1000;

      if (idleTimeMs >= maxIdleMs) {
        lockVault();
      }
    };

    const interval = setInterval(checkLock, 5000);
    
    // We removed the duplicate focus/visibilitychange listeners here because
    // they are properly handled with preemptive locking in handleUserActivity.
    
    return () => {
      clearInterval(interval);
    };
  }, [sessionState, autoLockMinutes, lastActivityTimestamp, lockVault]);
}
