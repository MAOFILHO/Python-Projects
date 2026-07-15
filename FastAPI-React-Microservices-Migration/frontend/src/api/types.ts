export type Mode = 'monolith' | 'microservices';
export type OperationName = 'sum' | 'mul';

export interface TraceHop {
  service: string;
  action: string;
  started_at: string;
  duration_ms: number;
  status: 'ok' | 'error';
}

export interface OperationRequest {
  a: number;
  b: number;
  mode: Mode;
}

export interface OperationResponse {
  result: number;
  mode: Mode;
  operation: OperationName;
  correlation_id: string;
  total_latency_ms: number;
  trace: TraceHop[];
}

export interface ServiceHealthEntry {
  service: string;
  status: 'ok' | 'down';
  latency_ms: number;
}

export interface HealthResponse {
  services: ServiceHealthEntry[];
  overall: 'ok' | 'degraded';
}

export interface HistoryItem {
  id: number;
  operation: string;
  operand_a: number;
  operand_b: number;
  result: number;
  mode: string;
  handled_by: string;
  correlation_id: string;
  latency_ms: number;
  created_at: string;
}

export interface HistoryResponse {
  items: HistoryItem[];
  total: number;
}

export interface ModeStats {
  count: number;
  avg_ms: number;
  min_ms: number;
  max_ms: number;
  recent_ms: number[];
}

export interface HistoryStatsResponse {
  by_mode: Partial<Record<Mode, ModeStats>>;
}
