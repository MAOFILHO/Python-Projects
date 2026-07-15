import type { ServiceHealthEntry } from '../api/types';

export function ServiceStatusCard({ service }: { service: ServiceHealthEntry }) {
  const isUp = service.status === 'ok';
  return (
    <div className="card service-status-card">
      <div className="service-status-card-header">
        <span className={`status-dot ${isUp ? 'status-dot-ok' : 'status-dot-down'}`} aria-hidden="true" />
        <strong>{service.service}</strong>
      </div>
      <span className={`badge ${isUp ? 'badge-ok' : 'badge-down'}`}>{isUp ? 'Up' : 'Down'}</span>
      <div className="service-status-card-latency">{service.latency_ms.toFixed(1)} ms</div>
    </div>
  );
}
