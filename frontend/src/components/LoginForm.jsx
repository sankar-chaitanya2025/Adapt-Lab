import { useState } from 'react';
import { useAuth } from '../hooks/useAuth';

export default function LoginForm() {
  const [isLogin, setIsLogin] = useState(true);
  const [username, setUsername] = useState('');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const { login, register, loading, error, clearError } = useAuth();

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (isLogin) {
      await login(username, password);
    } else {
      await register(username, email, password);
    }
  };

  const toggleMode = () => {
    setIsLogin(!isLogin);
    clearError();
  };

  return (
    <div className="w-full max-w-md mx-auto">
      {/* Tabs */}
      <div className="flex rounded-t-xl overflow-hidden border border-b-0 border-surface-700/50">
        <button
          onClick={() => { setIsLogin(true); clearError(); }}
          className={`flex-1 py-3 text-sm font-medium transition-all duration-200 ${
            isLogin
              ? 'bg-surface-800 text-accent-400 border-b-2 border-accent-400'
              : 'bg-surface-900 text-surface-400 hover:text-surface-200'
          }`}
        >
          Sign In
        </button>
        <button
          onClick={() => { setIsLogin(false); clearError(); }}
          className={`flex-1 py-3 text-sm font-medium transition-all duration-200 ${
            !isLogin
              ? 'bg-surface-800 text-accent-400 border-b-2 border-accent-400'
              : 'bg-surface-900 text-surface-400 hover:text-surface-200'
          }`}
        >
          Register
        </button>
      </div>

      {/* Form */}
      <div className="card rounded-t-none border-t-0">
        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label htmlFor="username" className="block text-sm font-medium text-surface-300 mb-1.5">
              Username
            </label>
            <input
              id="username"
              type="text"
              value={username}
              onChange={(e) => setUsername(e.target.value)}
              className="input-field"
              placeholder="Enter your username"
              required
              autoComplete="username"
            />
          </div>

          {!isLogin && (
            <div className="animate-fade-in">
              <label htmlFor="email" className="block text-sm font-medium text-surface-300 mb-1.5">
                Email
              </label>
              <input
                id="email"
                type="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                className="input-field"
                placeholder="you@example.com"
                required
                autoComplete="email"
              />
            </div>
          )}

          <div>
            <label htmlFor="password" className="block text-sm font-medium text-surface-300 mb-1.5">
              Password
            </label>
            <input
              id="password"
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              className="input-field"
              placeholder="••••••••"
              required
              autoComplete={isLogin ? 'current-password' : 'new-password'}
            />
          </div>

          {error && (
            <div className="animate-fade-in rounded-lg bg-danger-400/10 border border-danger-400/20 px-4 py-3 text-sm text-danger-400">
              {error}
            </div>
          )}

          <button
            type="submit"
            disabled={loading}
            className="btn-primary w-full flex items-center justify-center gap-2"
          >
            {loading ? (
              <>
                <svg className="w-4 h-4 animate-spin" fill="none" viewBox="0 0 24 24">
                  <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
                  <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z" />
                </svg>
                {isLogin ? 'Signing in...' : 'Creating account...'}
              </>
            ) : (
              isLogin ? 'Sign In' : 'Create Account'
            )}
          </button>
        </form>

        <p className="mt-4 text-center text-sm text-surface-400">
          {isLogin ? "Don't have an account? " : "Already have an account? "}
          <button
            onClick={toggleMode}
            className="text-accent-400 hover:text-accent-300 font-medium transition-colors"
          >
            {isLogin ? 'Register' : 'Sign in'}
          </button>
        </p>
      </div>
    </div>
  );
}
