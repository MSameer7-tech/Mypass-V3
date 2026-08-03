import { sendIPCRequest } from "../api/client";
import { Result } from "../api/result";

export interface SystemStatus {
  status: string;
  version: string;
}

export class SystemRepository {
  static async ping(): Promise<Result<SystemStatus>> {
    return sendIPCRequest<SystemStatus>("system.ping");
  }
}
