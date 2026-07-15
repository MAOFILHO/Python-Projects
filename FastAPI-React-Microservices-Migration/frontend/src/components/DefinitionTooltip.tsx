import { useId, useState } from 'react';
import { glossaryMap } from '../content/glossary';
import './DefinitionTooltip.css';

interface DefinitionTooltipProps {
  term: string;
  children?: React.ReactNode;
}

export function DefinitionTooltip({ term, children }: DefinitionTooltipProps) {
  const [open, setOpen] = useState(false);
  const tooltipId = useId();
  const definition = glossaryMap[term];

  if (!definition) {
    return <>{children ?? term}</>;
  }

  return (
    <span className="def-tooltip-wrap">
      <button
        type="button"
        className="def-tooltip-trigger"
        aria-describedby={tooltipId}
        title={definition}
        onMouseEnter={() => setOpen(true)}
        onMouseLeave={() => setOpen(false)}
        onFocus={() => setOpen(true)}
        onBlur={() => setOpen(false)}
        onClick={() => setOpen((prev) => !prev)}
      >
        {children ?? term}
      </button>
      {open && (
        <span role="tooltip" id={tooltipId} className="def-tooltip-bubble">
          <strong>{term}:</strong> {definition}
        </span>
      )}
    </span>
  );
}
