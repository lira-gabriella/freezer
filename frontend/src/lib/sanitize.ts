/** Basic input and path sanitization helpers for the frontend. */

export function stripControlChars(value: string): string {
  return value.replace(/[\x00-\x1f\x7f]/g, "");
}

export function sanitizeText(value: string, max = 256): string {
  return stripControlChars(value).trim().slice(0, max);
}

export function sanitizeProcessName(value: string): string {
  return sanitizeText(value, 128).replace(/[^\w.\- ]/g, "").trim();
}

export function sanitizePathInput(value: string): string {
  const cleaned = stripControlChars(value).trim();
  if (!cleaned) return "";
  if (cleaned.includes("..")) {
    throw new Error("Path traversal is not allowed");
  }
  return cleaned.replace(/[<>"|?*\x00]/g, "");
}

export function safeInt(value: unknown): number | null {
  const n = Number(value);
  if (!Number.isInteger(n) || n <= 0) return null;
  return n;
}

export function parsePidList(input: string): number[] {
  return Array.from(
    new Set(
      input
        .split(/[,\s]+/)
        .map((v) => safeInt(v))
        .filter((v): v is number => v !== null)
    )
  );
}

export function parseNameList(input: string): string[] {
  return Array.from(
    new Set(
      input
        .split(",")
        .map((v) => sanitizeProcessName(v))
        .filter((v) => v.length > 0)
    )
  );
}
