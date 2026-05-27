import { Outlet, NavLink, useNavigate } from 'react-router-dom';
import { useAuth } from '../hooks/useAuth';

export default function Layout() {
  const { user, logout } = useAuth();
  const navigate = useNavigate();

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  return (
    <div className="min-h-screen flex flex-col">
      {/* Navigation Bar */}
      <nav className="bg-surface-900/80 backdrop-blur-md border-b border-surface-700/50 sticky top-0 z-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between h-16">
            {/* Logo */}
            <div className="flex items-center gap-3">
              <div className="w-8 h-8 bg-gradient-to-br from-accent-400 to-accent-600 rounded-lg flex items-center justify-center">
                <span className="text-white font-bold text-sm">A</span>
              </div>
              <span className="text-xl font-bold bg-gradient-to-r from-accent-400 to-accent-300 bg-clip-text text-transparent">
                AdaptLab
              </span>
            </div>

            {/* Nav Links */}
            <div className="flex items-center gap-1">
              <NavLink
                to="/session"
                className={({ isActive }) =>
                  `px-4 py-2 rounded-lg text-sm font-medium transition-all duration-200 ${
                    isActive
                      ? 'bg-accent-600/20 text-accent-400'
                      : 'text-surface-300 hover:text-surface-100 hover:bg-surface-800'
                  }`
                }
              >
                <span className="flex items-center gap-2">
                  <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 20l4-16m4 4l4 4-4 4M6 16l-4-4 4-4" />
                  </svg>
                  Practice
                </span>
              </NavLink>

              <NavLink
                to="/dashboard"
                className={({ isActive }) =>
                  `px-4 py-2 rounded-lg text-sm font-medium transition-all duration-200 ${
                    isActive
                      ? 'bg-accent-600/20 text-accent-400'
                      : 'text-surface-300 hover:text-surface-100 hover:bg-surface-800'
                  }`
                }
              >
                <span className="flex items-center gap-2">
                  <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
                  </svg>
                  Dashboard
                </span>
              </NavLink>
            </div>

            {/* User + Logout */}
            <div className="flex items-center gap-4">
              <span className="text-sm text-surface-400">
                {user?.username}
              </span>
              <button
                onClick={handleLogout}
                className="px-3 py-1.5 text-sm text-surface-400 hover:text-surface-100 hover:bg-surface-800 rounded-lg transition-all duration-200"
              >
                Logout
              </button>
            </div>
          </div>
        </div>
      </nav>

      {/* Page Content */}
      <main className="flex-1">
        <Outlet />
      </main>
    </div>
  );
}
