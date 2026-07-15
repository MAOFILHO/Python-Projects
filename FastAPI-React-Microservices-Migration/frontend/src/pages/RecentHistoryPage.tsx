import { useEffect, useState } from 'react';
import { fetchHistory } from '../api/history';
import { ApiError } from '../api/client';
import type { HistoryItem } from '../api/types';

const OP_SYMBOLS: Record<string, string> = { sum: '+', mul: '×' };

export function RecentHistoryPage() {
  const [items, setItems] = useState<HistoryItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let cancelled = false;

    async function load() {
      try {
        const data = await fetchHistory(50, 0);
        if (!cancelled) setItems(data.items ?? []);
      } catch (err) {
        if (!cancelled) {
          setError(err instanceof ApiError ? err.message : 'Failed to load history.');
        }
      } finally {
        if (!cancelled) setLoading(false);
      }
    }

    load();
    return () => {
      cancelled = true;
    };
  }, []);

  return (
    <div>
      <h1>Recent History</h1>
      <p>The last 50 operations processed by the gateway, across both modes.</p>

      {loading && <p>Loading history…</p>}

      {error && (
        <div className="error-box" role="alert">
          {error}
        </div>
      )}

      {!loading && !error && items.length === 0 && (
        <div className="empty-box">
          No history yet. Go to <a href="/operations">Run Operation</a> to generate some.
        </div>
      )}

      {!loading && !error && items.length > 0 && (
        <div className="table-scroll">
          <table>
            <thead>
              <tr>
                <th>Time</th>
                <th>Operation</th>
                <th>Operands</th>
                <th>Result</th>
                <th>Mode</th>
                <th>Handled By</th>
                <th>Latency</th>
              </tr>
            </thead>
            <tbody>
              {items.map((item) => (
                <tr key={item.id}>
                  <td>{new Date(item.created_at).toLocaleString()}</td>
                  <td>{item.operation}</td>
                  <td>
                    {item.operand_a} {OP_SYMBOLS[item.operation] ?? item.operation} {item.operand_b}
                  </td>
                  <td>{item.result}</td>
                  <td>
                    <span className={`badge badge-mode-${item.mode}`}>{item.mode}</span>
                  </td>
                  <td>{item.handled_by}</td>
                  <td>{item.latency_ms.toFixed(1)} ms</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}
