import { Link, useLocation } from 'react-router-dom';
import {
  Bell,
  FileText,
  FolderOpen,
  LayoutDashboard,
  LogOut,
  MessageSquare,
  ShieldAlert,
  Search,
  Upload,
} from 'lucide-react';
import './Header.css';

const navItems = [
  { path: '/dashboard', label: 'Dashboard', icon: LayoutDashboard },
  { path: '/chat', label: 'Policy Chat', icon: MessageSquare },
  { path: '/tasks', label: 'Submit Task', icon: FileText },
  { path: '/scenarios', label: 'Scenario Tasks', icon: ShieldAlert },
  { path: '/resume', label: 'Resume Check', icon: Upload },
  { path: '/materials', label: 'Materials', icon: FolderOpen },
];

const getInitials = (user) =>
  (user.name || user.email || 'U')
    .split(' ')
    .map((part) => part[0])
    .join('')
    .slice(0, 2)
    .toUpperCase();

export function Topbar({ user }) {
  const initials = getInitials(user);

  return (
    <div className="topbar">
      <div className="topbar-search">
        <Search size={18} />
        <input type="text" value="" placeholder="Search or type a command" readOnly aria-label="Search" />
        <span className="shortcut">Ctrl K</span>
      </div>

      <div className="topbar-actions">
        <Link to="/materials" className="topbar-cta">
          <span className="plus-sign">+</span>
          Upload Material
        </Link>
        <button type="button" className="icon-button" aria-label="Notifications">
          <Bell size={18} />
        </button>
        <Link to="/profile" className="avatar-link" aria-label="Profile">
          <div className="avatar-badge">{initials}</div>
        </Link>
      </div>
    </div>
  );
}

function Header({ user, onLogout }) {
  const location = useLocation();
  const initials = getInitials(user);

  return (
    <header className="app-header">
      <aside className="sidebar">
        <div className="brand-block">
          <div className="brand-mark">
            <span></span>
            <span></span>
            <span></span>
            <span></span>
          </div>
          <div>
            <p className="brand-name">Office Assist</p>
            <span className="brand-subtitle">Training Workspace</span>
          </div>
        </div>

        <div className="sidebar-section-label">Main</div>
        <nav className="sidebar-nav">
          {navItems.map((item) => {
            const Icon = item.icon;
            return (
              <Link
                key={item.path}
                to={item.path}
                className={`nav-link ${location.pathname === item.path ? 'active' : ''}`}
              >
                <Icon size={18} />
                <span>{item.label}</span>
              </Link>
            );
          })}
        </nav>

        <div className="sidebar-footer">
          <Link to="/profile" className={`profile-chip ${location.pathname === '/profile' ? 'active' : ''}`}>
            <div className="avatar-badge small">{initials}</div>
            <div>
              <strong>{user.name || 'Profile'}</strong>
              <span>{user.role}</span>
            </div>
          </Link>

          <button onClick={onLogout} className="logout-btn">
            <LogOut size={18} />
            <span>Logout</span>
          </button>
        </div>
      </aside>
    </header>
  );
}

export default Header;
