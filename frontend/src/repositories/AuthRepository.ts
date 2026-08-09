import { sendIPCRequest } from "../api/client";
import { Result } from "../api/result";

export interface AuthStatus {
  sessionState: "UNLOCKED" | "LOCKED" | "NO_VAULT";
}

export interface BiometricStatus {
  available: boolean;
  enabled: boolean;
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

  static async biometricStatus(): Promise<Result<BiometricStatus>> {
    return sendIPCRequest<BiometricStatus>("auth.biometric_status");
  }

  static async enableBiometrics(): Promise<Result<{ success: boolean }>> {
    return sendIPCRequest<{ success: boolean }>("auth.enable_biometrics");
  }

  static async disableBiometrics(): Promise<Result<{ success: boolean }>> {
    return sendIPCRequest<{ success: boolean }>("auth.disable_biometrics");
  }
}
