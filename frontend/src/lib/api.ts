import type {
  ArchiveResponse,
  AutoIdleConfig,
  FreezeRequest,
  FreezeResponse,
  IdleResult,
  ProcessInfo,
  ScanHistoryItem,
  ScanResponse,
  VaultItemResponse,
} from "@/types/cryoguard";

const API_BASE = "http://localhost:8000";

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const res = await fetch(`${API_BASE}${path}`, {
    ...init,
    headers: {
      "Content-Type": "application/json",
      ...(init?.headers || {}),
    },
    cache: "no-store",
  });
  if (!res.ok) {
    let detail = `HTTP ${res.status}`;
    try {
      const data = await res.json();
      detail = data.detail || data.message || detail;
    } catch {}
    throw new Error(detail);
  }
  return res.json() as Promise<T>;
}

export const api = {
  listProcesses: () => request<ProcessInfo[]>("/processes"),
  freeze: (body: FreezeRequest) =>
    request<FreezeResponse>("/processes/freeze", { method: "POST", body: JSON.stringify(body) }),
  thaw: (body: FreezeRequest) =>
    request<FreezeResponse>("/processes/thaw", { method: "POST", body: JSON.stringify(body) }),
  findIdle: (body: AutoIdleConfig) =>
    request<IdleResult>("/processes/idle", { method: "POST", body: JSON.stringify(body) }),

  listVault: () => request<VaultItemResponse[]>("/vault"),
  archive: (path: string) =>
    request<ArchiveResponse>("/vault/archive", { method: "POST", body: JSON.stringify({ path }) }),
  restore: (item_id: number) =>
    request<ArchiveResponse>("/vault/restore", { method: "POST", body: JSON.stringify({ item_id }) }),

  scan: (path: string) =>
    request<ScanResponse>("/security/scan", { method: "POST", body: JSON.stringify({ path }) }),
  history: (limit = 50) => request<ScanHistoryItem[]>(`/security/history?limit=${limit}`),
};

export { API_BASE };
