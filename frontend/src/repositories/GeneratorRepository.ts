import { sendIPCRequest } from "../api/client";
import { Result } from "../api/result";

export interface GeneratedPassword {
  password: string;
}

export class GeneratorRepository {
  static async generate(length = 16, symbols = true, numbers = true): Promise<Result<GeneratedPassword>> {
    return sendIPCRequest<GeneratedPassword>("generator.generate", { length, symbols, numbers });
  }
}
