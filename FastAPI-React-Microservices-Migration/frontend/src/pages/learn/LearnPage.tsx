import { useEffect } from 'react';
import { useLocation } from 'react-router-dom';
import { WhatAreMicroservicesPage } from './WhatAreMicroservicesPage';
import { StranglerFigPage } from './StranglerFigPage';
import { ServiceBoundariesPage } from './ServiceBoundariesPage';
import { ObservabilityResiliencePage } from './ObservabilityResiliencePage';
import { WhenNotToUsePage } from './WhenNotToUsePage';
import { GlossaryPage } from '../GlossaryPage';
import './LearnPage.css';

// Everything that used to be a separate Learn/Glossary page and nav item is
// composed here into ONE scrollable page: "What Are Microservices?" renders
// first (it's what the LEARN nav item is labeled and links to), followed by
// an in-page index linking down to the rest via anchors, then each section
// in turn so those anchors actually resolve on the same page.
const SECTIONS = [
  { id: 'strangler-fig', label: 'The Strangler Fig Migration Pattern' },
  { id: 'service-boundaries', label: 'Service Boundaries & Anti-Patterns' },
  { id: 'observability', label: 'Observability & Resilience' },
  { id: 'when-not-to-use', label: 'When NOT to Use Microservices' },
  { id: 'glossary', label: 'Glossary' },
];

export function LearnPage() {
  const { hash } = useLocation();

  // React Router doesn't auto-scroll to a URL hash on client-side
  // navigation the way a full page load would - needed both for direct
  // links like /learn#observability and for the redirected legacy
  // /learn/observability-style routes in App.tsx.
  useEffect(() => {
    if (!hash) return;
    const el = document.getElementById(hash.slice(1));
    el?.scrollIntoView({ block: 'start' });
  }, [hash]);

  return (
    <div className="learn-page">
      <section id="what-are-microservices">
        <WhatAreMicroservicesPage />
      </section>

      <nav className="learn-index card" aria-label="More in the Learn section">
        <h3>More in this section</h3>
        <ul>
          {SECTIONS.map((s) => (
            <li key={s.id}>
              <a href={`#${s.id}`}>{s.label}</a>
            </li>
          ))}
        </ul>
      </nav>

      <section id="strangler-fig">
        <StranglerFigPage />
      </section>
      <section id="service-boundaries">
        <ServiceBoundariesPage />
      </section>
      <section id="observability">
        <ObservabilityResiliencePage />
      </section>
      <section id="when-not-to-use">
        <WhenNotToUsePage />
      </section>
      <section id="glossary">
        <GlossaryPage />
      </section>
    </div>
  );
}
