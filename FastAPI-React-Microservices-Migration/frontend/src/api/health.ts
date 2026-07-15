import { get } from './client';
import type { HealthResponse } from './types';

export function fetchHealth(): Promise<HealthResponse> {
  return get<HealthResponse>('/api/health');
}
