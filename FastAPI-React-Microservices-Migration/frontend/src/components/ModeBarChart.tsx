interface BarDatum {
  label: string;
  value: number;
  color: string;
}

export function ModeBarChart({ bars, unit = 'ms' }: { bars: BarDatum[]; unit?: string }) {
  const max = Math.max(...bars.map((b) => b.value), 1);
  const width = 400;
  const height = 160;
  const barWidth = 100;
  const gap = 60;

  return (
    <svg
      viewBox={`0 0 ${width} ${height}`}
      role="img"
      aria-label={bars.map((b) => `${b.label}: ${b.value.toFixed(1)} ${unit}`).join(', ')}
      className="mode-bar-chart"
    >
      {bars.map((bar, i) => {
        const barHeight = (bar.value / max) * 110;
        const x = 40 + i * (barWidth + gap);
        const y = 130 - barHeight;
        return (
          <g key={bar.label}>
            <rect x={x} y={y} width={barWidth} height={barHeight} fill={bar.color} rx={4} />
            <text x={x + barWidth / 2} y={y - 8} textAnchor="middle" fontSize="13" fontWeight="700" fill="#1f2937">
              {bar.value.toFixed(1)} {unit}
            </text>
            <text x={x + barWidth / 2} y={148} textAnchor="middle" fontSize="12" fill="#6b7280">
              {bar.label}
            </text>
          </g>
        );
      })}
    </svg>
  );
}
