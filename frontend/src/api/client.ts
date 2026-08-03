import { invoke } from "@tauri-apps/api/core";
import { Result } from "./result";

let requestId = 0;

export async function sendIPCRequest<T>(
  method: string,
  params: Record<string, unknown> = {}
): Promise<Result<T>> {
  const id = ++requestId;
  const payload = JSON.stringify({
    version: 1,
    jsonrpc: "2.0",
    id,
    method,
    params,
  });

  const startTime = performance.now();

  try {
    const rawResponse = await invoke<string>("python_ipc", { payload });
    const duration = Math.round(performance.now() - startTime);

    const parsed = JSON.parse(rawResponse);

    if (process.env.NODE_ENV !== "production") {
      console.log(`[IPC] ${method} (${duration}ms):`, parsed.result?.success ? "OK" : "ERROR");
    }

    if (parsed.result) {
      return parsed.result as Result<T>;
    }

    return {
      success: false,
      error: { code: "INVALID_RESPONSE", message: "Malformed JSON-RPC response." },
    };
  } catch (err: unknown) {
    const duration = Math.round(performance.now() - startTime);
    console.error(`[IPC Error] ${method} (${duration}ms):`, err);

    return {
      success: false,
      error: {
        code: "IPC_TRANSPORT_ERROR",
        message: err instanceof Error ? err.message : String(err),
      },
    };
  }
}
