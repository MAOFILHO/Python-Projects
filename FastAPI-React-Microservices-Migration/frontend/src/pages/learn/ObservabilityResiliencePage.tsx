import { Link } from 'react-router-dom';
import { DefinitionTooltip } from '../../components/DefinitionTooltip';

export function ObservabilityResiliencePage() {
  return (
    <article className="learn-article">
      <h1>Observability &amp; Resilience</h1>

      <p>
        A distributed system needs more supporting infrastructure than a monolith to stay
        debuggable and resilient, simply because a single user request can now cross process and
        network boundaries multiple times before it's done.
      </p>

      <h2>API Gateway responsibilities</h2>
      <ul>
        <li>
          <strong>Abstract Complexity.</strong> Clients don't need to know where dozens of
          individual services actually live.
        </li>
        <li>
          <strong>Traffic Routing.</strong> Routing requests by URL path or hostname is what makes
          the Strangler Fig pattern possible in the first place — the gateway is the switchboard
          that decides monolith vs. new service.
        </li>
        <li>
          <strong>Resilience.</strong> A central point where patterns like the{' '}
          <DefinitionTooltip term="Circuit Breaker" /> can prevent one failing service from
          cascading into a system-wide outage.
        </li>
      </ul>

      <h2>Observability standards</h2>
      <ul>
        <li>
          <strong>Centralized Logging.</strong> Local-only logs on each service are close to
          useless for debugging a request that touched five services. Aggregating logs across
          services is what lets you see overall system health at a glance.
        </li>
        <li>
          <strong>Distributed Tracing.</strong> Following a single request as it crosses multiple
          services is exactly what this app's correlation ID (<code>X-Request-ID</code>) and trace
          timeline demonstrate — go to <Link to="/operations">Run Operation</Link> and watch a
          trace play out hop by hop.
        </li>
        <li>
          <strong>Active Monitoring.</strong> Automated liveness checks that continuously verify
          services are actually responding, not just that they were deployed successfully.
        </li>
        <li>
          <strong>Health Checks.</strong> Detecting an offline service before a user hits an error
          is the whole point of the <Link to="/health">Service Health</Link> page in this lab.
        </li>
      </ul>

      <h2>Resilience patterns</h2>
      <p>
        A <DefinitionTooltip term="Circuit Breaker" /> returns an immediate failure for an
        operation that's likely to fail, instead of letting requests pile up and exhaust
        resources while waiting on a struggling downstream service. At the extreme end of
        proactively testing for failure sits <DefinitionTooltip term="Chaos Monkey" />, Netflix's
        tool that randomly disables production services to force engineers to design for graceful
        degradation rather than assuming everything will always be up.
      </p>
    </article>
  );
}
