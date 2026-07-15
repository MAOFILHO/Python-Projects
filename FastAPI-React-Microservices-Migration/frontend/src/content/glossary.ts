export interface GlossaryEntry {
  term: string;
  definition: string;
}

export const glossary: GlossaryEntry[] = [
  {
    term: 'Anti-Corruption Layer (ACL)',
    definition:
      "A facade or adapter used during migration to translate calls between a monolith and a new microservice, so the legacy caller's interface doesn't need to change.",
  },
  {
    term: 'Big Bang Migration',
    definition:
      'A high-risk strategy of replacing an entire monolithic system with a new architecture in a single operation, with no incremental value delivery.',
  },
  {
    term: 'Bounded Context',
    definition:
      'A central Domain-Driven Design (DDD) pattern defining the boundaries within which a particular business domain model applies.',
  },
  {
    term: 'Circuit Breaker',
    definition:
      'A pattern that returns an immediate failure for an operation likely to fail, preventing resource exhaustion and cascading failures.',
  },
  {
    term: "Conway's Law",
    definition:
      'Software architecture tends to mirror the communication structure of the organization that built it.',
  },
  {
    term: 'Distributed Monolith',
    definition:
      'A system made of multiple services that are so tightly coupled they must still be deployed and scaled together — the worst of both worlds.',
  },
  {
    term: 'Megaservice',
    definition: 'A service that takes on too many responsibilities, effectively becoming a "mini-monolith."',
  },
  {
    term: 'Polyglot Persistence',
    definition:
      "The practice of using different database technologies (relational, NoSQL, cache, graph) for different services, based on each service's specific needs.",
  },
  {
    term: 'Strangler Fig Pattern',
    definition:
      'A modernization strategy of incrementally building a new system around a legacy monolith until the monolith is entirely replaced.',
  },
  {
    term: 'Synchronizing Agent',
    definition:
      "A tactical bridge that keeps a new microservice's database and the legacy monolith's database consistent during migration.",
  },
  {
    term: 'Two-Pizza Team',
    definition:
      'A small, autonomous team (roughly 10-12 people, small enough to be fed by two pizzas) that owns a service end-to-end, from creation to maintenance.',
  },
  {
    term: 'Twelve-Factor App',
    definition:
      'A methodology of design patterns for building software-as-a-service applications, widely used as a baseline for microservices.',
  },
  {
    term: 'Wrong Cuts',
    definition:
      'An anti-pattern where services are split along technical layers (e.g. presentation vs. data) rather than business capabilities, leading to tightly coupled, hard-to-maintain services.',
  },
  {
    term: 'Shared Persistence',
    definition:
      'Multiple services reading/writing the same database schema, which couples them at the data layer and undermines independent deployability.',
  },
  {
    term: 'Chaos Monkey',
    definition:
      'A resilience-testing tool (originated at Netflix) that randomly disables production services to force systems to be designed for graceful failure.',
  },
];

export const glossaryMap: Record<string, string> = Object.fromEntries(
  glossary.map((entry) => [entry.term, entry.definition]),
);
