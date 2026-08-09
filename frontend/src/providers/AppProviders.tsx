import React, { useEffect } from "react";
import { QueryClientProvider } from "@tanstack/react-query";
import { queryClient } from "../queries/queryClient";
import { useSettingsStore } from "../stores/settings/useSettingsStore";
import { getCurrentWindow } from "@tauri-apps/api/window";
import { useClipboardStore } from "../stores/clipboard/useClipboardStore";

export interface AppProvidersProps {
  children: React.ReactNode;
}

export const AppProviders: React.FC<AppProvidersProps> = ({ children }) => {
  const theme = useSettingsStore((s) => s.theme);

  useEffect(() => {
    const isDark =
      theme === "dark" ||
      (theme === "system" && window.matchMedia("(prefers-color-scheme: dark)").matches);

    if (isDark) {
      document.documentElement.classList.remove("light");
    } else {
      document.documentElement.classList.add("light");
    }
  }, [theme]);

  useEffect(() => {
    let unlisten: (() => void) | undefined;
    const setupCloseListener = async () => {
      try {
        const appWindow = getCurrentWindow();
        unlisten = await appWindow.onCloseRequested(async (event) => {
          // Prevent immediate close to allow clipboard clearing
          event.preventDefault();
          try {
            await useClipboardStore.getState().clearIfOwned();
          } catch (e) {
            // Ignore errors, ensure we still close
          }
          // Now officially close
          appWindow.destroy();
        });
      } catch (e) {
        // Not running in Tauri context (e.g. browser)
        window.addEventListener("beforeunload", () => {
          useClipboardStore.getState().clearIfOwned();
        });
      }
    };
    setupCloseListener();

    return () => {
      if (unlisten) unlisten();
    };
  }, []);

  return (
    <QueryClientProvider client={queryClient}>
      {children}
    </QueryClientProvider>
  );
};
