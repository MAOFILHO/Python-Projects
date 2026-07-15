import { useEffect, useRef, useState } from 'react';
import { Link } from 'react-router-dom';
import { runOperation } from '../api/operations';
import { fetchHistoryStats } from '../api/history';
import { ApiError } from '../api/client';
import {
  checkAzureCli,
  fetchAzureStatus,
  fetchAzureToken,
  startAzureDeploy,
} from '../api/azureMigrate';
import type { HistoryStatsResponse, Mode, OperationName, TraceHop } from '../api/types';
import { TraceTimeline } from '../components/TraceTimeline';
import { ModeBarChart } from '../components/ModeBarChart';
import { Sparkline } from '../components/Sparkline';
import './MigrationPage.css';

const MODE_HEX: Record<Mode, string> = {
  monolith: '#0a1a3c',
  microservices: '#ff8c00',
};

// The Strangler Fig cutover, staged as traffic-split percentages routed to
// the microservices path (the remainder stays on the monolith) - mirrors the
// "Traffic Redirection" step described in Learn > The Strangler Fig
// Migration Pattern, made interactive instead of just diagrammed.
const STAGES = [
  {
    percent: 0,
    label: 'Now running: Monolithic architecture',
    status: 'monolith' as const,
    narration: 'Baseline: 100% of traffic is served in-process by the monolith. No extraction yet.',
  },
  {
    percent: 25,
    label: 'Migrating to Microservices — first service extracted',
    status: 'migrating' as const,
    narration: 'Extracted sum-service and mul-service. Gateway starts routing ~25% of traffic to them; the rest still hits the monolith.',
  },
  {
    percent: 50,
    label: 'Migrating to Microservices — traffic split evenly',
    status: 'migrating' as const,
    narration: 'Confidence is up. Traffic split is now even — half the requests still fail over to the monolith as a safety net.',
  },
  {
    percent: 75,
    label: 'Migrating to Microservices — monolith mostly strangled',
    status: 'migrating' as const,
    narration: 'Monolith is down to a thin skeleton. Most traffic now flows through the independent services.',
  },
  {
    percent: 100,
    label: 'Now running: Microservices architecture',
    status: 'microservices' as const,
    narration: 'Cutover complete. 100% of traffic now flows through the microservices path. Monolith can be decommissioned.',
  },
];

const BATCH_SIZE = 6;
const STEP_DELAY_MS = 550;
const STAGE_TRANSITION_DELAY_MS = 900;

interface LogEntry {
  id: number;
  operation: OperationName;
  mode: Mode;
  result: number;
  latency_ms: number;
  hops: number;
}

interface ConsoleLine {
  id: number;
  text: string;
  kind: 'stage' | 'request' | 'done';
}

function sleep(ms: number) {
  return new Promise((resolve) => setTimeout(resolve, ms));
}

export function MigrationPage() {
  const [stageIndex, setStageIndex] = useState(0);
  const [running, setRunning] = useState(false);
  const [autoRunning, setAutoRunning] = useState(false);
  const [log, setLog] = useState<LogEntry[]>([]);
  const [consoleLines, setConsoleLines] = useState<ConsoleLine[]>([]);
  const [liveTrace, setLiveTrace] = useState<TraceHop[]>([]);
  const [stats, setStats] = useState<HistoryStatsResponse | null>(null);
  const [error, setError] = useState<string | null>(null);
  const nextId = useRef(1);
  const nextConsoleId = useRef(1);
  const consoleEndRef = useRef<HTMLDivElement | null>(null);

  // --- Real Azure deployment (see api/azureMigrate.ts) ---
  const [azureToken, setAzureToken] = useState<string | null>(null);
  const [azureAvailable, setAzureAvailable] = useState<boolean | null>(null);
  const [azureMessage, setAzureMessage] = useState<string>('');
  const [azureStatus, setAzureStatus] = useState<'idle' | 'running' | 'success' | 'failed'>('idle');
  const [azureLines, setAzureLines] = useState<string[]>([]);
  const [azureUrl, setAzureUrl] = useState<string | null>(null);
  const [azureError, setAzureError] = useState<string | null>(null);
  const azureSinceRef = useRef(0);
  const azurePollRef = useRef<ReturnType<typeof setInterval> | null>(null);
  const azureOpenedRef = useRef(false);

  const stage = STAGES[stageIndex];
  const isComplete = stage.percent === 100;
  const isBusy = running || autoRunning;

  function appendConsole(text: string, kind: ConsoleLine['kind'] = 'request') {
    setConsoleLines((prev) => [...prev, { id: nextConsoleId.current++, text, kind }].slice(-100));
  }

  useEffect(() => {
    consoleEndRef.current?.scrollIntoView({ block: 'nearest' });
  }, [consoleLines]);

  async function refreshStats() {
    try {
      const data = await fetchHistoryStats();
      setStats(data);
    } catch {
      // Non-fatal - the migration can still run without the comparison charts loading.
    }
  }

  useEffect(() => {
    refreshStats();
  }, []);

  // Bootstrap the Azure control token once on mount. This only succeeds
  // when the gateway sees this as a local request (see
  // services/gateway/app/migration_control.py) - on any other deployment
  // (including an already-migrated Azure copy of this very app), it 403s
  // and the "Deploy to Azure" section simply stays hidden.
  useEffect(() => {
    let cancelled = false;
    (async () => {
      try {
        const { token } = await fetchAzureToken();
        if (cancelled) return;
        setAzureToken(token);
        const check = await checkAzureCli(token);
        if (cancelled) return;
        setAzureAvailable(check.available);
        setAzureMessage(check.message);
      } catch {
        if (!cancelled) setAzureAvailable(null);
      }
    })();
    return () => {
      cancelled = true;
    };
  }, []);

  useEffect(() => {
    return () => {
      if (azurePollRef.current) clearInterval(azurePollRef.current);
    };
  }, []);

  function pollAzureStatus(token: string) {
    if (azurePollRef.current) clearInterval(azurePollRef.current);
    azurePollRef.current = setInterval(async () => {
      try {
        const snapshot = await fetchAzureStatus(token, azureSinceRef.current);
        if (snapshot.lines.length > 0) {
          setAzureLines((prev) => [...prev, ...snapshot.lines]);
          azureSinceRef.current = snapshot.total_lines;
        }
        setAzureStatus(snapshot.status);
        if (snapshot.gateway_url) setAzureUrl(snapshot.gateway_url);

        if (snapshot.status === 'success' || snapshot.status === 'failed') {
          if (azurePollRef.current) clearInterval(azurePollRef.current);
          if (snapshot.status === 'failed') {
            setAzureError(snapshot.error ?? 'Deployment failed. See the console output above.');
          } else if (snapshot.gateway_url && !azureOpenedRef.current) {
            azureOpenedRef.current = true;
            window.open(snapshot.gateway_url, '_blank', 'noopener,noreferrer');
          }
        }
      } catch {
        // Transient poll failure - just try again on the next tick.
      }
    }, 700);
  }

  async function handleDeployToAzure() {
    if (!azureToken) return;
    const confirmed = window.confirm(
      'This provisions real, billable Azure resources (Container Apps, Container Registry, ' +
        'Log Analytics) under your currently logged-in `az` CLI account, using the same stack ' +
        'this app already deploys via `make azure-deploy`. Continue?',
    );
    if (!confirmed) return;

    setAzureError(null);
    setAzureLines([]);
    azureSinceRef.current = 0;
    azureOpenedRef.current = false;
    setAzureUrl(null);
    setAzureStatus('running');

    try {
      const result = await startAzureDeploy(azureToken);
      if (!result.started) {
        setAzureStatus('idle');
        setAzureError(result.message);
        return;
      }
      pollAzureStatus(azureToken);
    } catch (err) {
      setAzureStatus('idle');
      setAzureError(err instanceof ApiError ? err.message : 'Failed to start deployment.');
    }
  }

  async function runBatchAtStage(percent: number) {
    for (let i = 0; i < BATCH_SIZE; i += 1) {
      const operation: OperationName = Math.random() < 0.5 ? 'sum' : 'mul';
      const mode: Mode = Math.random() * 100 < percent ? 'microservices' : 'monolith';
      const a = Math.floor(Math.random() * 20) + 1;
      const b = Math.floor(Math.random() * 20) + 1;

      const resp = await runOperation(operation, { a, b, mode });
      setLiveTrace(resp.trace);

      const entry: LogEntry = {
        id: nextId.current++,
        operation,
        mode,
        result: resp.result,
        latency_ms: resp.total_latency_ms,
        hops: resp.trace.length,
      };
      setLog((prev) => [entry, ...prev].slice(0, 20));
      appendConsole(
        `→ ${operation}(${a}, ${b}) routed to ${mode.toUpperCase()} — ${resp.trace.length} hop(s), ` +
          `${resp.total_latency_ms.toFixed(1)}ms, result=${resp.result}`,
      );

      await sleep(STEP_DELAY_MS);
    }
  }

  async function runBatch() {
    setRunning(true);
    setError(null);
    try {
      appendConsole(`Running ${BATCH_SIZE} requests at ${stage.percent}% microservices traffic...`, 'stage');
      await runBatchAtStage(stage.percent);
      await refreshStats();
    } catch (err) {
      setError(err instanceof ApiError ? err.message : 'A request failed mid-batch.');
    } finally {
      setRunning(false);
    }
  }

  async function startMigration() {
    setAutoRunning(true);
    setError(null);
    setStageIndex(0);
    appendConsole('Starting migration from the monolith...', 'stage');
    try {
      for (let i = 0; i < STAGES.length; i += 1) {
        setStageIndex(i);
        const s = STAGES[i];
        appendConsole(`[${s.label}] ${s.narration}`, 'stage');
        await sleep(STAGE_TRANSITION_DELAY_MS);
        await runBatchAtStage(s.percent);
      }
      await refreshStats();
      appendConsole('Migration complete. The app is now running on Microservices.', 'done');
    } catch (err) {
      setError(err instanceof ApiError ? err.message : 'The migration stopped early because a request failed.');
    } finally {
      setAutoRunning(false);
    }
  }

  function advanceStage() {
    setStageIndex((i) => Math.min(i + 1, STAGES.length - 1));
    setLiveTrace([]);
  }

  function retreatStage() {
    setStageIndex((i) => Math.max(i - 1, 0));
    setLiveTrace([]);
  }

  function resetMigration() {
    setStageIndex(0);
    setLog([]);
    setLiveTrace([]);
    setError(null);
    setConsoleLines([]);
  }

  const byMode = stats?.by_mode ?? {};
  const hasComparisonData = Boolean(byMode.monolith || byMode.microservices);

  return (
    <div>
      <h1>Start Migration</h1>
      <p>
        Watch the migration itself, not just the before/after snapshots. Each stage below shifts a
        percentage of live traffic from the <strong>monolith</strong> to the{' '}
        <strong>microservices</strong> path — exactly the "Traffic Redirection" step from{' '}
        <Link to="/learn#strangler-fig">The Strangler Fig Migration Pattern</Link>.
      </p>

      <div className="card migration-progress-card">
        <div className={`migration-status-banner migration-status-${stage.status}`}>
          <span className="status-dot" aria-hidden="true" />
          {stage.label}
        </div>
        <div className="migration-stage-label">
          <span>
            {stage.percent}% microservices / {100 - stage.percent}% monolith
          </span>
        </div>
        <div className="migration-progress-bar" role="img" aria-label={`${stage.percent}% of traffic routed to microservices`}>
          <div
            className="migration-progress-fill-mono"
            style={{ width: `${100 - stage.percent}%`, background: MODE_HEX.monolith }}
          />
          <div
            className="migration-progress-fill-micro"
            style={{ width: `${stage.percent}%`, background: MODE_HEX.microservices }}
          />
        </div>
        <div className="migration-stage-dots">
          {STAGES.map((s, i) => (
            <div
              key={s.percent}
              className={`migration-stage-dot ${i === stageIndex ? 'active' : ''} ${i < stageIndex ? 'done' : ''}`}
              title={s.label}
            />
          ))}
        </div>

        <div className="migration-controls migration-controls-primary">
          <button type="button" className="btn migration-start-btn" onClick={startMigration} disabled={isBusy}>
            {autoRunning ? 'Migrating…' : '▶ Start Migration to Microservices'}
          </button>
        </div>

        <p className="migration-note">Or step through it manually:</p>
        <div className="migration-controls">
          <button type="button" className="btn btn-secondary" onClick={retreatStage} disabled={stageIndex === 0 || isBusy}>
            ← Back a stage
          </button>
          <button type="button" className="btn btn-secondary" onClick={runBatch} disabled={isBusy}>
            {running ? 'Running batch…' : `Run ${BATCH_SIZE} requests at this stage`}
          </button>
          <button
            type="button"
            className="btn btn-secondary"
            onClick={advanceStage}
            disabled={stageIndex === STAGES.length - 1 || isBusy}
          >
            Advance stage →
          </button>
          <button type="button" className="btn btn-secondary" onClick={resetMigration} disabled={isBusy}>
            Reset to Stage 0
          </button>
        </div>
        <p className="migration-note">
          "Reset" only rewinds this simulation locally — it doesn't erase recorded history or the
          comparison metrics below, which accumulate across everything you've run in this session.
        </p>
      </div>

      {isComplete && (
        <div className="callout migration-complete-banner">
          <div>
            <strong>Migration complete — the App is now running on Microservices.</strong> All
            simulated traffic flows through the microservices path; the monolith has been fully
            strangled.
          </div>
          <Link to="/compare" className="btn migration-compare-cta">
            Click Compare to see the performance difference →
          </Link>
        </div>
      )}

      {error && (
        <div className="error-box" role="alert">
          {error}
        </div>
      )}

      {azureAvailable !== null && (
        <div className="card">
          <h3>Deploy to Azure (real)</h3>
          <p>
            Everything above is a free, local simulation. This deploys the <strong>full stack</strong>{' '}
            (monolith + all microservices) as real Azure Container Apps — the exact same
            infrastructure documented in <Link to="/learn#observability">Observability &amp; Resilience</Link>{' '}
            — so you can re-run this same migration against real cross-container network latency
            instead of localhost. See <code>azure/README.md</code> for the full cost breakdown and
            manual CLI equivalent.
          </p>

          {!azureAvailable && (
            <div className="empty-box">{azureMessage || 'Azure CLI not available.'}</div>
          )}

          {azureAvailable && (
            <>
              <div className="migration-controls">
                <button
                  type="button"
                  className="btn migration-azure-btn"
                  onClick={handleDeployToAzure}
                  disabled={azureStatus === 'running'}
                >
                  {azureStatus === 'running' ? 'Deploying to Azure…' : '🚀 Deploy to Azure'}
                </button>
                {azureStatus === 'success' && azureUrl && (
                  <a href={azureUrl} target="_blank" rel="noopener noreferrer" className="btn btn-secondary">
                    Open live Azure app ↗
                  </a>
                )}
              </div>
              <p className="migration-note">{azureMessage}</p>

              {azureError && (
                <div className="error-box" role="alert">
                  {azureError}
                </div>
              )}

              {azureStatus === 'success' && azureUrl && (
                <div className="callout">
                  <strong>Deployed.</strong> Your live Azure app opened in a new tab:{' '}
                  <a href={azureUrl} target="_blank" rel="noopener noreferrer">
                    {azureUrl}
                  </a>
                  . Remember to run <code>make azure-teardown</code> when you're done to avoid
                  ongoing cost.
                </div>
              )}

              {azureLines.length > 0 && (
                <div className="migration-console">
                  {azureLines.map((line, i) => (
                    <div key={i} className="migration-console-line migration-console-request">
                      {line}
                    </div>
                  ))}
                </div>
              )}
            </>
          )}
        </div>
      )}

      <div className="card">
        <h3>Migration console</h3>
        {consoleLines.length === 0 ? (
          <p className="sparkline-empty">Click "Start Migration" or run a manual batch to see verbose output here.</p>
        ) : (
          <div className="migration-console">
            {consoleLines.map((line) => (
              <div key={line.id} className={`migration-console-line migration-console-${line.kind}`}>
                {line.text}
              </div>
            ))}
            <div ref={consoleEndRef} />
          </div>
        )}
      </div>

      <div className="card">
        <h3>Live request trace</h3>
        {liveTrace.length > 0 ? (
          <TraceTimeline trace={liveTrace} />
        ) : (
          <p className="sparkline-empty">Run the migration above to watch requests route in real time.</p>
        )}
      </div>

      <div className="card">
        <h3>Request log (most recent first)</h3>
        {log.length === 0 ? (
          <p className="sparkline-empty">No requests run yet.</p>
        ) : (
          <div className="table-scroll">
            <table>
              <thead>
                <tr>
                  <th>Operation</th>
                  <th>Routed to</th>
                  <th>Result</th>
                  <th>Latency</th>
                  <th>Hops</th>
                </tr>
              </thead>
              <tbody>
                {log.map((entry) => (
                  <tr key={entry.id}>
                    <td>{entry.operation}</td>
                    <td>
                      <span className={`badge badge-mode-${entry.mode}`}>{entry.mode}</span>
                    </td>
                    <td>{entry.result}</td>
                    <td>{entry.latency_ms.toFixed(1)} ms</td>
                    <td>{entry.hops}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>

      <div className="card">
        <h3>Cumulative comparison</h3>
        {!hasComparisonData ? (
          <p className="sparkline-empty">No data yet — run the migration above to populate this.</p>
        ) : (
          <>
            <ModeBarChart
              bars={(['monolith', 'microservices'] as Mode[])
                .filter((m) => byMode[m])
                .map((m) => ({ label: m, value: byMode[m]!.avg_ms, color: MODE_HEX[m] }))}
            />
            <div className="sparkline-grid">
              {(['monolith', 'microservices'] as Mode[]).map((m) => (
                <div key={m}>
                  <div className="sparkline-mode-label">
                    <span className="status-dot" style={{ background: MODE_HEX[m] }} aria-hidden="true" />
                    {m} {byMode[m] ? `(avg ${byMode[m]!.avg_ms.toFixed(1)} ms)` : '(no data)'}
                  </div>
                  <Sparkline values={byMode[m]?.recent_ms ?? []} color={MODE_HEX[m]} label={m} />
                </div>
              ))}
            </div>
            <p className="migration-note">
              See the full breakdown on <Link to="/compare">Compare Performance</Link>.
            </p>
          </>
        )}
      </div>
    </div>
  );
}
