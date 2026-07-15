export function WhenNotToUsePage() {
  return (
    <article className="learn-article">
      <h1>When NOT to Use Microservices</h1>

      <p>
        Microservices solve real problems, but they aren't free — they trade one set of problems
        for another. A balanced view means knowing when a monolith is actually the better choice.
      </p>

      <h2>When a monolith wins</h2>
      <ul>
        <li>
          <strong>Simplicity is a priority.</strong> Monoliths are simpler to build, reason about,
          and deploy. Microservices add real distributed-systems complexity: network latency,
          partial failures, and eventual consistency between services that used to just be
          function calls in the same process.
        </li>
        <li>
          <strong>Unclear domains.</strong> If your business boundaries aren't well understood yet,
          splitting services prematurely tends to produce Wrong Cuts — boundaries that don't
          actually match how the business works, and that are expensive to redraw later once
          other services depend on them. It's often better to start monolithic and extract
          services once boundaries have proven stable.
        </li>
        <li>
          <strong>Small scale.</strong> For a small, low-complexity application, the operational
          overhead of running a distributed system — service discovery, distributed tracing,
          multiple deployment pipelines, network resilience — outweighs any scaling benefit you'd
          actually realize.
        </li>
      </ul>

      <h2>A quick decision checklist</h2>
      <ul>
        <li>Do we have more than one team that needs to deploy independently?</li>
        <li>Are our business domain boundaries actually well understood and reasonably stable?</li>
        <li>Do different parts of the system have meaningfully different scaling needs?</li>
        <li>
          Can we operate the added infrastructure — service discovery, centralized logging,
          distributed tracing, health checks — reliably, not just build it once?
        </li>
        <li>Is the complexity we're trying to solve organizational, or purely technical?</li>
        <li>
          Would extracting one or two well-isolated services (Strangler Fig style) solve the
          problem, rather than a full rewrite into many services?
        </li>
      </ul>

      <p>
        If most of the answers above are "no," a monolith — or a monolith with one or two
        carefully extracted services — is very likely the right call for now.
      </p>
    </article>
  );
}
