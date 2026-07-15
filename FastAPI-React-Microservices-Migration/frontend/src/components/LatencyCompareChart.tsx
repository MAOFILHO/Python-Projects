interface LatencyCompareChartProps {
  monolithMs: number | null;
  microservicesMs: number | null;
}

export function LatencyCompareChart({ monolithMs, microservicesMs }: LatencyCompareChartProps) {
  if (monolithMs === null || microservicesMs === null) {
    return null;
  }

  const max = Math.max(monolithMs, microservicesMs, 1);
  const bars = [
    { label: 'Monolith', value: monolithMs, color: 'var(--navy)' },
    { label: 'Microservices', value: microservicesMs, color: 'var(--orange)' },
  ];

  return (
    <div className="card">
      <h3>Latency: Last Monolith vs. Last Microservices Run</h3>
      <div className="latency-bars">
        {bars.map((bar) => (
          <div className="latency-bar-row" key={bar.label}>
            <span className="latency-bar-label">{bar.label}</span>
            <div className="latency-bar-track">
              <div
                className="latency-bar-fill"
                style={{
                  width: `${(bar.value / max) * 100}%`,
                  background: bar.color,
                }}
              />
            </div>
            <span className="latency-bar-value">{bar.value.toFixed(1)} ms</span>
          </div>
        ))}
      </div>
    </div>
  );
}
