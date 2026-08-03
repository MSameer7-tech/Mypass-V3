import React from "react";
import { QueryClientProvider } from "@tanstack/react-query";
import { queryClient } from "../queries/queryClient";

export interface AppProvidersProps {
  children: React.ReactNode;
}

export const AppProviders: React.FC<AppProvidersProps> = ({ children }) => {
  return (
    <QueryClientProvider client={queryClient}>
      {children}
    </QueryClientProvider>
  );
};
