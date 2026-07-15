import { Link } from 'react-router-dom';

export function OverviewPage() {
  return (
    <div>
      <h1>Monolith to Microservices Migration</h1>
      <p>
        This project lets you run the same arithmetic operation through two different backend
        architectures — a traditional <strong>monolith</strong> and a decomposed{' '}
        <strong>microservices</strong> topology — and see exactly what happens on the wire:
        which services were hit, how long each hop took, and what the end-to-end latency looks
        like.
      </p>
      <div className="card">
        <h2>Start here: watch the migration happen</h2>
        <p>
          The app starts out <strong>running the monolithic architecture</strong>. Head to{' '}
          <Link to="/migration">Start Migration</Link> to migrate it to microservices stage
          by stage — watch individual requests get routed to the monolith or to the new services in
          real time, until the app is <strong>running fully on microservices</strong>, then compare
          the performance difference.
        </p>
      </div>

      <div className="card">
        <h2>Explore further</h2>
        <p>
          <Link to="/operations">Run Operation</Link> to trigger a single sum or multiply call in
          either mode and watch the request trace play out hop by hop.
        </p>
        <p>
          Then check <Link to="/health">Service Health</Link>, dig into{' '}
          <Link to="/compare">Compare Performance</Link>, or browse{' '}
          <Link to="/history">Recent History</Link>.
        </p>
        <p>
          New to the concepts? Start with{' '}
          <Link to="/learn">What Are Microservices?</Link> in the Learn section.
        </p>
      </div>
    </div>
  );
}
