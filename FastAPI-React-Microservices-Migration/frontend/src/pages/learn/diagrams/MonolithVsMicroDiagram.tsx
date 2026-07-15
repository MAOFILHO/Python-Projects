export function MonolithVsMicroDiagram() {
  return (
    <svg
      viewBox="0 0 760 320"
      role="img"
      aria-label="Diagram contrasting a monolith, a single deployable unit with stacked modules and a shared database, with microservices, an API gateway routing to independently deployable service and database pairs"
      className="learn-diagram"
    >
      {/* Monolith box */}
      <rect x="10" y="20" width="260" height="280" rx="10" fill="#eef1f6" stroke="#0a1a3c" strokeWidth="2" />
      <text x="140" y="45" textAnchor="middle" fontSize="14" fontWeight="700" fill="#0a1a3c">
        Monolith
      </text>
      <text x="140" y="62" textAnchor="middle" fontSize="11" fill="#6b7280">
        (single deployable unit)
      </text>

      {['Module A', 'Module B', 'Module C'].map((label, i) => (
        <g key={label}>
          <rect x="30" y={80 + i * 50} width="220" height="36" rx="6" fill="#ffffff" stroke="#c7cede" />
          <text x="140" y={80 + i * 50 + 23} textAnchor="middle" fontSize="12" fill="#1f2937">
            {label}
          </text>
        </g>
      ))}

      <rect x="30" y="250" width="220" height="36" rx="6" fill="#e8f1fc" stroke="#2563eb" />
      <text x="140" y="273" textAnchor="middle" fontSize="12" fontWeight="600" fill="#0a1a3c">
        Shared database
      </text>

      {/* Arrow */}
      <line x1="280" y1="160" x2="360" y2="160" stroke="#6b7280" strokeWidth="2" markerEnd="url(#arrowhead)" />
      <text x="320" y="145" textAnchor="middle" fontSize="11" fill="#6b7280">
        decompose
      </text>

      {/* Microservices box */}
      <rect x="370" y="20" width="380" height="280" rx="10" fill="#eef1f6" stroke="#0a1a3c" strokeWidth="2" />
      <text x="560" y="45" textAnchor="middle" fontSize="14" fontWeight="700" fill="#0a1a3c">
        Microservices
      </text>
      <text x="560" y="62" textAnchor="middle" fontSize="11" fill="#6b7280">
        (independently deployable)
      </text>

      <rect x="460" y="78" width="200" height="36" rx="6" fill="#ff8c00" />
      <text x="560" y="101" textAnchor="middle" fontSize="12" fontWeight="700" fill="#ffffff">
        API Gateway
      </text>

      {[0, 1, 2].map((i) => {
        const x = 390 + i * 125;
        return (
          <g key={i}>
            <line x1="560" y1="114" x2={x + 50} y2="150" stroke="#6b7280" strokeWidth="1.5" markerEnd="url(#arrowhead)" />
            <rect x={x} y="150" width="100" height="34" rx="6" fill="#ffffff" stroke="#c7cede" />
            <text x={x + 50} y="171" textAnchor="middle" fontSize="11" fill="#1f2937">
              Service {i + 1}
            </text>
            <rect x={x} y="196" width="100" height="34" rx="6" fill="#e8f1fc" stroke="#2563eb" />
            <text x={x + 50} y="217" textAnchor="middle" fontSize="11" fontWeight="600" fill="#0a1a3c">
              DB {i + 1}
            </text>
          </g>
        );
      })}

      <defs>
        <marker id="arrowhead" markerWidth="8" markerHeight="8" refX="6" refY="4" orient="auto">
          <path d="M0,0 L8,4 L0,8 Z" fill="#6b7280" />
        </marker>
      </defs>
    </svg>
  );
}
