import { useState } from 'react';
import { runOperation } from '../api/operations';
import { ApiError } from '../api/client';
import type { Mode, OperationName, OperationResponse } from '../api/types';
import { TraceTimeline } from '../components/TraceTimeline';
import { LatencyCompareChart } from '../components/LatencyCompareChart';
import '../components/LatencyCompareChart.css';

export function OperationsPage() {
  const [operation, setOperation] = useState<OperationName>('sum');
  const [mode, setMode] = useState<Mode>('monolith');
  const [a, setA] = useState('7');
  const [b, setB] = useState('5');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [response, setResponse] = useState<OperationResponse | null>(null);
  const [traceDone, setTraceDone] = useState(false);

  const [lastMonolithMs, setLastMonolithMs] = useState<number | null>(null);
  const [lastMicroservicesMs, setLastMicroservicesMs] = useState<number | null>(null);

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    const numA = Number(a);
    const numB = Number(b);
    if (Number.isNaN(numA) || Number.isNaN(numB)) {
      setError('Please enter valid numbers for both operands.');
      return;
    }

    setLoading(true);
    setError(null);
    setResponse(null);
    setTraceDone(false);

    try {
      const result = await runOperation(operation, { a: numA, b: numB, mode });
      setResponse(result);
      if (result.mode === 'monolith') {
        setLastMonolithMs(result.total_latency_ms);
      } else {
        setLastMicroservicesMs(result.total_latency_ms);
      }
    } catch (err) {
      if (err instanceof ApiError) {
        setError(`Request failed (${err.status || 'network'}): ${err.message}`);
      } else {
        setError('Something went wrong running the operation.');
      }
    } finally {
      setLoading(false);
    }
  }

  return (
    <div>
      <h1>Run Operation</h1>
      <p>
        Trigger a simple arithmetic call through the gateway and watch the request trace it
        follows in either architecture.
      </p>

      <form className="card" onSubmit={handleSubmit}>
        <div className="op-form-row">
          <label htmlFor="op-a">Operand A</label>
          <input
            id="op-a"
            type="number"
            value={a}
            onChange={(e) => setA(e.target.value)}
            required
          />
        </div>

        <div className="op-form-row">
          <span>Operation</span>
          <div className="toggle-group" role="group" aria-label="Operation">
            <button
              type="button"
              className={operation === 'sum' ? 'active' : ''}
              onClick={() => setOperation('sum')}
            >
              Sum
            </button>
            <button
              type="button"
              className={operation === 'mul' ? 'active' : ''}
              onClick={() => setOperation('mul')}
            >
              Multiply
            </button>
          </div>
        </div>

        <div className="op-form-row">
          <label htmlFor="op-b">Operand B</label>
          <input
            id="op-b"
            type="number"
            value={b}
            onChange={(e) => setB(e.target.value)}
            required
          />
        </div>

        <div className="op-form-row">
          <span>Mode</span>
          <div className="toggle-group" role="group" aria-label="Mode">
            <button
              type="button"
              className={mode === 'monolith' ? 'active' : ''}
              onClick={() => setMode('monolith')}
            >
              Monolith
            </button>
            <button
              type="button"
              className={mode === 'microservices' ? 'active' : ''}
              onClick={() => setMode('microservices')}
            >
              Microservices
            </button>
          </div>
        </div>

        <button type="submit" className="btn" disabled={loading}>
          {loading ? 'Running…' : 'Run'}
        </button>
      </form>

      {error && (
        <div className="error-box" role="alert">
          {error}
        </div>
      )}

      {response && (
        <div className="card">
          <h3>Request Trace</h3>
          <TraceTimeline trace={response.trace} onDone={() => setTraceDone(true)} />
          {traceDone && (
            <div className="op-result">
              <div className="op-result-value">
                Result: <strong>{response.result}</strong>
              </div>
              <div className="op-result-meta">
                Total latency: <strong>{response.total_latency_ms.toFixed(1)} ms</strong> ·
                Correlation ID: <code>{response.correlation_id}</code>
              </div>
            </div>
          )}
        </div>
      )}

      <LatencyCompareChart monolithMs={lastMonolithMs} microservicesMs={lastMicroservicesMs} />
    </div>
  );
}
