import { useEffect, useState } from 'react';
import { fetchHealth } from '../api/health';
import { ApiError } from '../api/client';
import type { HealthResponse } from '../api/types';
import { ServiceStatusCard } from '../components/ServiceStatusCard';
import '../components/ServiceStatusCard.css';

export function ServiceHealthPage() {
  const [health, setHealth] = useState<HealthResponse | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    let cancelled = false;

    async function load() {
      try {
        const data = await fetchHealth();
        if (!cancelled) {
          setHealth(data);
          setError(null);
        }
      } catch (err) {
        if (!cancelled) {
          setError(
            err instanceof ApiError
              ? `Unable to reach the gateway: ${err.message}`
              : 'Unable to reach the gateway.',
          );
        }
      } finally {
        if (!cancelled) setLoading(false);
      }
    }

    load();
    const interval = setInterval(load, 5000);

    return () => {
      cancelled = true;
      clearInterval(interval);
    };
  }, []);

  return (
    <div>
      <h1>Service Health</h1>
      <p>Live status of every backend service, polled every 5 seconds.</p>

      {loading && !health && !error && <p>Checking service health…</p>}

      {error && (
        <div className="error-box" role="alert">
          {error}
        </div>
      )}

      {health && (
        <>
          <div className={`callout ${health.overall === 'ok' ? '' : 'health-degraded'}`}>
            {health.overall === 'ok'
              ? 'All services are healthy.'
              : 'One or more services are degraded or unreachable.'}
          </div>

          {health.services.length === 0 ? (
            <div className="empty-box">No services reported.</div>
          ) : (
            <div className="service-grid">
              {health.services.map((service) => (
                <ServiceStatusCard service={service} key={service.service} />
              ))}
            </div>
          )}
        </>
      )}
    </div>
  );
}
