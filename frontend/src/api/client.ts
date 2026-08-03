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

    if (!rawResponse || !rawResponse.trim()) {
      console.warn(`[IPC Empty Output] ${method} (${duration}ms): Empty stdout returned from bridge.`);
      return {
        success: false,
        error: { code: "EMPTY_RESPONSE", message: "Empty IPC response received from backend." },
      };
    }

    let parsed: any;
    try {
      parsed = JSON.parse(rawResponse);
    } catch (parseErr: any) {
      console.error(`[IPC JSON Parse Error] ${method} (${duration}ms): Raw payload was: "${rawResponse}"`, parseErr);
      return {
        success: false,
        error: { code: "JSON_PARSE_ERROR", message: `Invalid JSON from backend: ${parseErr.message}` },
      };
    }

    if (process.env.NODE_ENV !== "production") {
      console.log(`[IPC] ${method} (${duration}ms):`, parsed.result?.success ? "OK" : "ERROR");
    }

    if (parsed.result) {
      return parsed.result as Result<T>;
    }

    return {
      success: false,
      error: { code: "INVALID_RESPONSE", message: "Malformed JSON-RPC response format." },
    };
  } catch (err: unknown) {
    const duration = Math.round(performance.now() - startTime);
    console.error(`[IPC Transport Error] ${method} (${duration}ms):`, err);

    return {
      success: false,
      error: {
        code: "IPC_TRANSPORT_ERROR",
        message: err instanceof Error ? err.message : String(err),
      },
    };
  }
}
