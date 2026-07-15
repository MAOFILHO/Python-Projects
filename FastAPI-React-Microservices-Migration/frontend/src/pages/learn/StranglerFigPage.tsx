import { Link } from 'react-router-dom';
import { DefinitionTooltip } from '../../components/DefinitionTooltip';
import { StranglerFigDiagram } from './diagrams/StranglerFigDiagram';

export function StranglerFigPage() {
  return (
    <article className="learn-article">
      <h1>The Strangler Fig Migration Pattern</h1>

      <p>
        The <DefinitionTooltip term="Strangler Fig Pattern" /> takes its name from a real plant
        that germinates in the canopy of a host tree and gradually grows roots down around it,
        eventually replacing the host entirely. Applied to software, a new architecture
        incrementally "strangles" and replaces a legacy monolith, one capability at a time, rather
        than attempting a risky <DefinitionTooltip term="Big Bang Migration" />.
      </p>

      <div className="callout">
        Don't just read about it — <Link to="/migration">try the migration yourself</Link>. It
        stages traffic from 0% to 100% microservices and lets you run live requests at each step.
      </div>

      <div className="learn-diagram-wrap card">
        <StranglerFigDiagram />
      </div>

      <h2>The 7 core implementation steps</h2>
      <ul>
        <li>
          <strong>1. Domain Assessment &amp; Slicing.</strong> Identify{' '}
          <DefinitionTooltip term="Bounded Context">bounded contexts</DefinitionTooltip> using
          Domain-Driven Design so you know where the seams in the business domain actually are.
        </li>
        <li>
          <strong>2. Introduce a Proxy Layer / API Gateway.</strong> Put a gateway in front of the
          monolith. Initially, 100% of traffic still routes straight through to the monolith — the
          gateway changes nothing yet, it just becomes the new front door.
        </li>
        <li>
          <strong>3. Service Extraction.</strong> Clone a high-value, well-isolated capability out
          of the monolith into a new, independently deployable service.
        </li>
        <li>
          <strong>4. Anti-Corruption Layer (ACL).</strong> Build an{' '}
          <DefinitionTooltip term="Anti-Corruption Layer (ACL)" /> — an adapter or facade — so the
          remaining monolith can keep calling the extracted capability without being tightly
          coupled to the new service's interface.
        </li>
        <li>
          <strong>5. Traffic Redirection.</strong> The proxy starts routing specific paths to the
          new service while everything else stays on the monolith.
        </li>
        <li>
          <strong>6. Data Synchronization &amp; Ownership.</strong> The new service gets its own
          data store. If other parts of the monolith still need that data, a{' '}
          <DefinitionTooltip term="Synchronizing Agent" /> keeps the legacy database consistent in
          the meantime.
        </li>
        <li>
          <strong>7. Decommissioning.</strong> Repeat steps 3–6 until the monolith is a thin
          skeleton — or gone entirely.
        </li>
      </ul>

      <h2>Why not a Big Bang rewrite?</h2>
      <ul>
        <li>
          Legacy systems accumulate lost or undiscovered requirements over years. Migrating is as
          much a discovery process as an engineering one — you can't fully specify a rewrite
          upfront.
        </li>
        <li>
          Monoliths are moving targets. New features keep landing on the old system while a long
          rewrite is underway, so the rewrite is chasing a target that never stops moving.
        </li>
        <li>
          A rewrite delivers zero business value until the very end. The Strangler Fig approach
          delivers incremental value with every service extracted.
        </li>
        <li>
          Large rewrites are notoriously prone to late, expensive failure — the risk is
          concentrated in one enormous cutover instead of spread across many small, reversible
          steps.
        </li>
      </ul>
    </article>
  );
}
