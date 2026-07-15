export function StranglerFigDiagram() {
  const stages = [
    { title: 'Stage 1', desc: '100% → Monolith' },
    { title: 'Stage 2', desc: 'Proxy splits traffic → Monolith + New Service' },
    { title: 'Stage 3', desc: '100% → Microservices (monolith retired)' },
  ];

  return (
    <svg
      viewBox="0 0 780 180"
      role="img"
      aria-label="Three stage diagram of the Strangler Fig migration: stage one all traffic to the monolith, stage two a proxy splits traffic between the monolith and a new service, stage three all traffic goes to microservices and the monolith is retired"
      className="learn-diagram"
    >
      {stages.map((stage, i) => {
        const x = 20 + i * 260;
        return (
          <g key={stage.title}>
            <rect x={x} y="30" width="230" height="110" rx="10" fill="#eef1f6" stroke="#0a1a3c" strokeWidth="2" />
            <text x={x + 115} y="55" textAnchor="middle" fontSize="14" fontWeight="700" fill="#0a1a3c">
              {stage.title}
            </text>
            <foreignObject x={x + 15} y="65" width="200" height="65">
              <div
                style={{
                  fontSize: '12px',
                  color: '#1f2937',
                  textAlign: 'center',
                  fontFamily: 'sans-serif',
                  lineHeight: 1.35,
                }}
              >
                {stage.desc}
              </div>
            </foreignObject>
            {i < stages.length - 1 && (
              <line
                x1={x + 235}
                y1="85"
                x2={x + 255}
                y2="85"
                stroke="#6b7280"
                strokeWidth="2"
                markerEnd="url(#sf-arrow)"
              />
            )}
          </g>
        );
      })}
      <defs>
        <marker id="sf-arrow" markerWidth="8" markerHeight="8" refX="6" refY="4" orient="auto">
          <path d="M0,0 L8,4 L0,8 Z" fill="#6b7280" />
        </marker>
      </defs>
    </svg>
  );
}
