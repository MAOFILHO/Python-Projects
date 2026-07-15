import { Link } from 'react-router-dom';

export function TopBar() {
  return (
    <header className="topbar">
      <Link to="/" className="topbar-link">
        <span className="topbar-badge">C</span>
        <span className="topbar-title">Contoso</span>
      </Link>
      <span className="topbar-divider" aria-hidden="true" />
      <span className="topbar-subtitle">Monolith to Microservices Migration</span>
    </header>
  );
}
