import { useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../hooks/useAuth';
import LoginForm from '../components/LoginForm';

export default function LoginPage() {
  const { isAuthenticated } = useAuth();
  const navigate = useNavigate();

  useEffect(() => {
    if (isAuthenticated) {
      navigate('/session', { replace: true });
    }
  }, [isAuthenticated, navigate]);

  return (
    <div className="min-h-screen flex flex-col items-center justify-center px-4 bg-gradient-to-br from-surface-950 via-surface-900 to-surface-950">
      {/* Background decoration */}
      <div className="absolute inset-0 overflow-hidden pointer-events-none">
        <div className="absolute top-1/4 left-1/4 w-96 h-96 bg-accent-500/5 rounded-full blur-3xl" />
        <div className="absolute bottom-1/4 right-1/4 w-96 h-96 bg-blue-500/5 rounded-full blur-3xl" />
      </div>

      <div className="relative z-10 w-full max-w-md">
        {/* Logo + Title */}
        <div className="text-center mb-8">
          <div className="inline-flex items-center justify-center w-16 h-16 bg-gradient-to-br from-accent-400 to-accent-600 rounded-2xl mb-4 shadow-lg shadow-accent-500/20">
            <span className="text-white font-bold text-2xl">A</span>
          </div>
          <h1 className="text-3xl font-bold bg-gradient-to-r from-accent-400 via-accent-300 to-emerald-400 bg-clip-text text-transparent">
            AdaptLab
          </h1>
          <p className="mt-2 text-surface-400 text-sm">
            Adaptive AI-powered C programming tutor
          </p>
        </div>

        <LoginForm />
      </div>
    </div>
  );
}
