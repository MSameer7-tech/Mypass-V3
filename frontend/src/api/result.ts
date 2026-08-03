export interface IPCError {
  code: string;
  message: string;
}

export type Result<T> =
  | {
      success: true;
      data: T;
    }
  | {
      success: false;
      error: IPCError;
    };
