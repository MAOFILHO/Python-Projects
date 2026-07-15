import { DefinitionTooltip } from '../../components/DefinitionTooltip';
import { MonolithVsMicroDiagram } from './diagrams/MonolithVsMicroDiagram';

export function WhatAreMicroservicesPage() {
  return (
    <article className="learn-article">
      <h1>What Are Microservices?</h1>

      <p>
        A <strong>microservice</strong> is a small, independently deployable service that owns a
        single bounded business capability — along with its own data and its own API. A{' '}
        <strong>microservices architecture</strong> is what you get when many such services are
        composed together and communicate with each other over the network to deliver a complete
        application.
      </p>

      <p>
        Contrast that with a <strong>monolith</strong>: one codebase, one deployment artifact, and
        typically one shared database. Every feature — billing, inventory, notifications, search —
        lives in the same process and ships together, every time.
      </p>

      <div className="learn-diagram-wrap card">
        <MonolithVsMicroDiagram />
      </div>

      <h2>Key advantages</h2>
      <ul>
        <li>
          <strong>Independent Scaling.</strong> Scale only the services under load — the checkout
          service during a sale, say — instead of scaling the entire monolith just because one
          part of it is hot.
        </li>
        <li>
          <strong>Faster, Safer Change Cycles.</strong> A team can deploy one service without
          redeploying everything else. Blast radius shrinks: a bad deploy affects one capability,
          not the whole system.
        </li>
        <li>
          <strong>Technology &amp; Data Autonomy.</strong> Different services can use different
          languages, frameworks, and databases suited to their own workload — a practice known as{' '}
          <DefinitionTooltip term="Polyglot Persistence" />.
        </li>
        <li>
          <strong>Organizational Alignment.</strong> Services map to business capabilities, and
          teams can own a service end-to-end, from design to production operation.
        </li>
      </ul>

      <p>
        One common misconception: microservices don't strictly require containers. You could run
        each service as a bare process. In practice, though, containers (Docker) plus an
        orchestrator (Kubernetes) have become the dominant, standardized way to package, run, and
        orchestrate dozens or hundreds of independently deployable units — which is why this lab's
        backend is built and run that way.
      </p>

      <p>
        Curious what the latency tradeoff looks like in practice? Head to{' '}
        <a href="/compare">Compare Performance</a> after running a few operations.
      </p>
    </article>
  );
}
