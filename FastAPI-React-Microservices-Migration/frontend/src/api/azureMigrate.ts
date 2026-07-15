import { get, post } from './client';

export interface AzureCheckResponse {
  available: boolean;
  message: string;
}

export interface AzureDeployStartResponse {
  started: boolean;
  message: string;
}

export interface AzureStatusResponse {
  status: 'idle' | 'running' | 'success' | 'failed';
  lines: string[];
  total_lines: number;
  gateway_url: string | null;
  error: string | null;
}

// Every call below requires the localhost-only + token-gated endpoints on
// the gateway (see services/gateway/app/migration_control.py) - fetchAzureToken
// is the one exception, gated only by the localhost check, since it's how
// the token itself is bootstrapped.

export function fetchAzureToken(): Promise<{ token: string }> {
  return get('/api/migrate/azure/token');
}

export function checkAzureCli(token: string): Promise<AzureCheckResponse> {
  return get('/api/migrate/azure/check', { 'X-Migrate-Token': token });
}

export function startAzureDeploy(token: string): Promise<AzureDeployStartResponse> {
  return post('/api/migrate/azure/deploy', {}, { 'X-Migrate-Token': token });
}

export function fetchAzureStatus(token: string, since: number): Promise<AzureStatusResponse> {
  return get(`/api/migrate/azure/status?since=${since}`, { 'X-Migrate-Token': token });
}
