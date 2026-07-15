import { glossary } from '../content/glossary';

export function GlossaryPage() {
  const sorted = [...glossary].sort((a, b) => a.term.localeCompare(b.term));

  return (
    <article className="learn-article">
      <h1>Glossary</h1>
      <p>Key terms used throughout the Learn section, alphabetized.</p>
      <dl className="glossary-list card">
        {sorted.map((entry) => (
          <div className="glossary-entry" key={entry.term}>
            <dt>{entry.term}</dt>
            <dd>{entry.definition}</dd>
          </div>
        ))}
      </dl>
    </article>
  );
}
