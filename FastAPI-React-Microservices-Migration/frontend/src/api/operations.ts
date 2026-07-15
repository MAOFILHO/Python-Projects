import { post } from './client';
import type { OperationName, OperationRequest, OperationResponse } from './types';

export function runOperation(
  operation: OperationName,
  body: OperationRequest,
): Promise<OperationResponse> {
  return post<OperationResponse>(`/api/operations/${operation}`, body);
}
