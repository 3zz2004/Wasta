export type Result<T, E extends string> =
  | { readonly ok: true; readonly value: T }
  | { readonly ok: false; readonly error: E };

export const ok = <T>(value: T) => ({ ok: true, value }) as const;
export const err = <E extends string>(error: E) => ({ ok: false, error }) as const;
