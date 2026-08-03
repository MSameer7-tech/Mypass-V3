import { IPCError } from "./result";

const errorMessages: Record<string, string> = {
  AUTH_INVALID_PASSWORD: "Invalid master password. Please try again.",
  AUTH_VAULT_NOT_FOUND: "No vault found on this device.",
  VAULT_ENTRY_NOT_FOUND: "The requested password entry could not be found.",
  METHOD_NOT_FOUND: "Unsupported backend operation.",
  INTERNAL_ERROR: "An unexpected error occurred in the local security engine.",
};

export function mapIPCErrorToMessage(error: IPCError): string {
  return errorMessages[error.code] || error.message || "An unknown error occurred.";
}
