import { NavLink } from 'react-router-dom';
import { sidebarNavGroups } from './SidebarNavData';

export function Sidebar() {
  return (
    <nav className="sidebar" aria-label="Main navigation">
      {sidebarNavGroups.map((group) => (
        <div className="sidebar-group" key={group.label}>
          <div className="sidebar-group-label">{group.label}</div>
          <ul className="sidebar-nav-list">
            {group.items.map((item) => (
              <li className="sidebar-nav-item" key={item.to}>
                <NavLink to={item.to} className={({ isActive }) => (isActive ? 'active' : '')}>
                  {item.label}
                </NavLink>
              </li>
            ))}
          </ul>
        </div>
      ))}
    </nav>
  );
}
