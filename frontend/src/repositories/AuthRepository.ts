import { sendIPCRequest } from "../api/client";
import { Result } from "../api/result";

export interface AuthStatus {
  sessionState: "UNLOCKED" | "LOCKED";
}

export class AuthRepository {
  static async status(): Promise<Result<AuthStatus>> {
    return sendIPCRequest<AuthStatus>("auth.status");
  }

  static async unlock(masterPassword: string): Promise<Result<{ success: boolean }>> {
    return sendIPCRequest<{ success: boolean }>("auth.unlock", { masterPassword });
  }

  static async lock(): Promise<Result<{ success: boolean }>> {
    return sendIPCRequest<{ success: boolean }>("auth.lock");
  }

  static async biometricUnlock(): Promise<Result<{ success: boolean }>> {
    return sendIPCRequest<{ success: boolean }>("auth.biometric_unlock");
  }
}
