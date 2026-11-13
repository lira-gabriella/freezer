export interface ProcessInfo {
  pid: number;
  name: string;
  username?: string | null;
  cpu_percent: number;
  memory_mb: number;
  status: string;
  exe?: string | null;
}

export interface FreezeRequest {
  pids: number[];
  process_names?: string[];
}

export interface FreezeResponse {
  success: boolean;
  message: string;
  affected_pids: number[];
  failed_pids: number[];
}

export interface AutoIdleConfig {
  enabled: boolean;
  idle_timeout_minutes: number;
  protected_processes: string[];
}

export interface IdleResult {
  idle_pids: number[];
  count: number;
}

export interface VaultItemResponse {
  id: number;
  name: string;
  original_path: string;
  archive_path: string;
  original_size_bytes: number;
  archive_size_bytes: number;
  sha256: string;
  is_archived: boolean;
  saved_bytes: number;
  created_at?: string | null;
  restored_at?: string | null;
}

export interface ArchiveResponse {
  success: boolean;
  message: string;
  item?: VaultItemResponse | null;
}

export interface Finding {
  path: string;
  reason: string;
  severity: "low" | "medium" | "high";
  sha256?: string | null;
  file_size: number;
}

export interface ScanResponse {
  success: boolean;
  target_path: string;
  safety_score: number;
  files_scanned: number;
  suspicious_count: number;
  findings: Finding[];
  message: string;
}

export interface ScanHistoryItem {
  id: number;
  target_path: string;
  safety_score: number;
  files_scanned: number;
  suspicious_count: number;
  created_at?: string | null;
}
