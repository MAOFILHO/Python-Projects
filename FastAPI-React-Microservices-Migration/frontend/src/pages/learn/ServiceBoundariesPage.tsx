import { DefinitionTooltip } from '../../components/DefinitionTooltip';

export function ServiceBoundariesPage() {
  return (
    <article className="learn-article">
      <h1>Service Boundaries &amp; Anti-Patterns</h1>

      <p>
        Where you "cut" a monolith into services is the single most consequential design decision
        in a microservices migration. Get it wrong and you inherit all of the operational cost of
        a distributed system with none of the benefits.
      </p>

      <h2>How to find good boundaries</h2>
      <ul>
        <li>
          <strong>Business Capabilities over Technical Layers.</strong> Split by what the business
          does — Inventory Management, Billing, Notifications — not by technical tier
          (presentation vs. data). Cutting along technical layers is exactly the{' '}
          <DefinitionTooltip term="Wrong Cuts" /> anti-pattern described below.
        </li>
        <li>
          <strong><DefinitionTooltip term="Conway's Law" /></strong> — software architecture tends
          to mirror the communication structure of the organization that built it. If your teams
          are siloed by technical layer, your services probably will be too, whether you intend it
          or not.
        </li>
        <li>
          <strong><DefinitionTooltip term="Two-Pizza Team" /></strong> — small, autonomous teams,
          roughly 10-12 people (small enough to be fed by two pizzas), that own a service
          end-to-end, from creation through ongoing maintenance.
        </li>
        <li>
          <strong><DefinitionTooltip term="Bounded Context" /></strong> — a Domain-Driven Design
          concept for the boundary within which a particular business model applies. Techniques
          like Event Storming help a team find where one business domain ends and another begins.
          As a rule of thumb: a service should own both its data and its API.
        </li>
      </ul>

      <h2>Anti-patterns to avoid</h2>
      <p>
        The umbrella risk to watch for is the{' '}
        <strong><DefinitionTooltip term="Distributed Monolith" /></strong> — a system with all the
        network complexity of microservices, but the tight coupling of a monolith. Most of the
        anti-patterns below are ways of accidentally building one.
      </p>

      <h3>Technical anti-patterns</h3>
      <ul>
        <li>
          <strong><DefinitionTooltip term="Shared Persistence" /></strong> — multiple services
          reading and writing the same database schema. This couples teams at the data layer and
          kills independent deployability.
        </li>
        <li>
          <strong><DefinitionTooltip term="Megaservice" /></strong> — a service that takes on too
          many responsibilities and becomes a mini-monolith in disguise.
        </li>
        <li>
          <strong>Cyclic Dependency.</strong> Service A calls B, B calls C, and C calls back to A.
          This makes services impossible to deploy or test in isolation.
        </li>
        <li>
          <strong>Hardcoded Endpoints.</strong> Baking specific IPs or ports into a service instead
          of using service discovery makes topology changes brittle and manual.
        </li>
        <li>
          <strong>Inappropriate Service Intimacy.</strong> Reaching directly into another
          service's private data instead of going through its public API.
        </li>
        <li>
          <strong>Shared Libraries.</strong> Sharing business-logic dependencies across services
          forces synchronized, lockstep deployments — exactly what microservices are meant to
          avoid. This is why this project's own sum and multiply logic is intentionally
          duplicated across services rather than shared through a common library: it's a
          deliberate demonstration of avoiding this anti-pattern.
        </li>
      </ul>

      <h3>Organizational anti-patterns</h3>
      <ul>
        <li>
          <strong>Microservices as the Goal.</strong> Adopting the architecture for its own sake,
          rather than because it solves a real, concrete business need.
        </li>
        <li>
          <strong>Legacy Organization.</strong> Rigid, siloed Dev and Ops teams with manual release
          schedules undermine the whole point of independently deployable services.
        </li>
        <li>
          <strong>Magic Pixie Dust.</strong> The false belief that adopting microservices will
          automatically fix pre-existing organizational dysfunction. It won't — and it can make
          coordination problems worse if boundaries and ownership aren't sorted out first.
        </li>
      </ul>
    </article>
  );
}
