export function Sparkline({ values, color, label }: { values: number[]; color: string; label: string }) {
  if (values.length === 0) {
    return <p className="sparkline-empty">No recent samples.</p>;
  }

  const width = 240;
  const height = 48;
  const max = Math.max(...values);
  const min = Math.min(...values);
  const range = max - min || 1;

  const points = values
    .map((v, i) => {
      const x = values.length === 1 ? 0 : (i / (values.length - 1)) * width;
      const y = height - ((v - min) / range) * height;
      return `${x},${y}`;
    })
    .join(' ');

  return (
    <svg
      viewBox={`0 0 ${width} ${height}`}
      role="img"
      aria-label={`${label} recent latency sparkline, from ${min.toFixed(1)} to ${max.toFixed(1)} ms`}
      className="sparkline"
    >
      <polyline points={points} fill="none" stroke={color} strokeWidth={2} />
    </svg>
  );
}
