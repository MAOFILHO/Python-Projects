import { get } from './client';
import type { HistoryResponse, HistoryStatsResponse } from './types';

export function fetchHistory(limit = 50, offset = 0): Promise<HistoryResponse> {
  return get<HistoryResponse>(`/api/history?limit=${limit}&offset=${offset}`);
}

export function fetchHistoryStats(): Promise<HistoryStatsResponse> {
  return get<HistoryStatsResponse>('/api/history/stats');
}
