import { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { fetchHistoryStats } from '../api/history';
import { runOperation } from '../api/operations';
import { ApiError } from '../api/client';
import type { HistoryStatsResponse, Mode } from '../api/types';
import { ModeBarChart } from '../components/ModeBarChart';
import { Sparkline } from '../components/Sparkline';

// SVG doesn't resolve CSS custom properties from inline style attrs reliably in all
// contexts, so use literal hex values that match the theme instead.
const MODE_HEX: Record<Mode, string> = {
  monolith: '#0a1a3c',
  microservices: '#ff8c00',
};

export function PerformanceComparePage() {
  const [stats, setStats] = useState<HistoryStatsResponse | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);
  const [trialsRunning, setTrialsRunning] = useState<Mode | null>(null);

  async function load() {
    try {
      const data = await fetchHistoryStats();
      setStats(data);
      setError(null);
    } catch (err) {
      setError(err instanceof ApiError ? err.message : 'Failed to load performance stats.');
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    load();
  }, []);

  async function runTrials(mode: Mode) {
    setTrialsRunning(mode);
    try {
      for (let i = 0; i < 5; i += 1) {
        await runOperation('sum', { a: 7, b: 5, mode });
      }
      await load();
    } catch (err) {
      setError(err instanceof ApiError ? err.message : 'Failed to run trials.');
    } finally {
      setTrialsRunning(null);
    }
  }

  const byMode = stats?.by_mode ?? {};
  const hasData = Boolean(byMode.monolith || byMode.microservices);

  return (
    <div>
      <h1>Compare Performance</h1>
      <p>Aggregate latency statistics captured across every run recorded in history.</p>

      {loading && <p>Loading stats…</p>}

      {error && (
        <div className="error-box" role="alert">
          {error}
        </div>
      )}

      {!loading && !error && !hasData && (
        <div className="empty-box">
          No data yet — run some operations first to see a comparison.{' '}
          <Link to="/operations">Go to Run Operation</Link>.
        </div>
      )}

      {!loading && hasData && (
        <div className="card">
          <h3>Average Latency by Mode</h3>
          <ModeBarChart
            bars={(['monolith', 'microservices'] as Mode[])
              .filter((m) => byMode[m])
              .map((m) => ({ label: m, value: byMode[m]!.avg_ms, color: MODE_HEX[m] }))}
          />
        </div>
      )}

      {!loading && hasData && (
        <div className="card">
          <h3>Recent Latency Trend</h3>
          <div className="sparkline-grid">
            {(['monolith', 'microservices'] as Mode[]).map((m) => (
              <div key={m}>
                <div className="sparkline-mode-label">
                  <span
                    className="status-dot"
                    style={{ background: MODE_HEX[m] }}
                    aria-hidden="true"
                  />
                  {m} {byMode[m] ? `(avg ${byMode[m]!.avg_ms.toFixed(1)} ms)` : '(no data)'}
                </div>
                <Sparkline values={byMode[m]?.recent_ms ?? []} color={MODE_HEX[m]} label={m} />
              </div>
            ))}
          </div>
        </div>
      )}

      <div className="card">
        <h3>Generate More Data</h3>
        <p>Run 5 sum trials (7 + 5) for a mode and refresh the charts above.</p>
        <div className="trial-buttons">
          <button
            type="button"
            className="btn btn-secondary"
            disabled={trialsRunning !== null}
            onClick={() => runTrials('monolith')}
          >
            {trialsRunning === 'monolith' ? 'Running…' : 'Run 5 trials — Monolith'}
          </button>
          <button
            type="button"
            className="btn btn-secondary"
            disabled={trialsRunning !== null}
            onClick={() => runTrials('microservices')}
          >
            {trialsRunning === 'microservices' ? 'Running…' : 'Run 5 trials — Microservices'}
          </button>
        </div>
      </div>

      <aside className="callout">
        <p>
          The latency gap between modes reflects real network-hop overhead: each service-to-service
          HTTP call in the microservices path adds its own round trip. This is the{' '}
          <strong>Independent Scaling</strong> tradeoff — services on the microservices path pay
          per-hop latency, but in exchange gain independent deployability and independent
          scalability. Read more in{' '}
          <Link to="/learn">What Are Microservices?</Link> and see the
          per-hop trace live on <Link to="/learn#observability">Observability &amp; Resilience</Link>.
        </p>
      </aside>
    </div>
  );
}
