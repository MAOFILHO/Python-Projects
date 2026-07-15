import { useEffect, useState } from 'react';
import type { TraceHop } from '../api/types';
import './TraceTimeline.css';

interface TraceTimelineProps {
  trace: TraceHop[];
  onDone?: () => void;
}

export function TraceTimeline({ trace, onDone }: TraceTimelineProps) {
  const [visibleCount, setVisibleCount] = useState(0);

  useEffect(() => {
    setVisibleCount(0);
    if (trace.length === 0) {
      onDone?.();
      return;
    }

    let cancelled = false;
    let index = 0;
    const timers: ReturnType<typeof setTimeout>[] = [];

    const step = () => {
      if (cancelled) return;
      index += 1;
      setVisibleCount(index);
      if (index >= trace.length) {
        onDone?.();
        return;
      }
      timers.push(setTimeout(step, 350));
    };

    timers.push(setTimeout(step, 350));

    return () => {
      cancelled = true;
      timers.forEach(clearTimeout);
    };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [trace]);

  if (trace.length === 0) {
    return null;
  }

  return (
    <ol className="trace-timeline" aria-label="Request trace">
      {trace.slice(0, visibleCount).map((hop, i) => (
        <li className="trace-hop card" key={`${hop.service}-${i}`}>
          <span
            className={`status-dot status-dot-${hop.status}`}
            aria-hidden="true"
          />
          <div className="trace-hop-body">
            <div className="trace-hop-title">
              <strong>{hop.service}</strong>
              <span className="trace-hop-action">{hop.action}</span>
            </div>
            <div className="trace-hop-meta">
              <span>{hop.duration_ms.toFixed(1)} ms</span>
              <span aria-label={`status ${hop.status}`}>
                {hop.status === 'ok' ? 'OK' : 'Error'}
              </span>
            </div>
          </div>
        </li>
      ))}
    </ol>
  );
}
