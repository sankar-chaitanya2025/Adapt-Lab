import { useState, useEffect } from 'react';
import client from '../api/client';
import ProgressView from '../components/ProgressView';

export default function DashboardPage() {
  const [progress, setProgress] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    fetchProgress();
  }, []);

  const fetchProgress = async () => {
    setLoading(true);
    try {
      const res = await client.get('/progress');
      setProgress(res.data);
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to load progress');
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-[calc(100vh-4rem)]">
        <div className="flex items-center gap-3 text-surface-400">
          <svg className="w-5 h-5 animate-spin" fill="none" viewBox="0 0 24 24">
            <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
            <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z" />
          </svg>
          Loading progress...
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="flex items-center justify-center h-[calc(100vh-4rem)]">
        <div className="text-center">
          <p className="text-danger-400 mb-4">{error}</p>
          <button onClick={fetchProgress} className="btn-primary">Retry</button>
        </div>
      </div>
    );
  }

  const summary = progress?.summary || {};

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      {/* Header */}
      <div className="mb-8">
        <h1 className="text-2xl font-bold text-surface-100">Learning Dashboard</h1>
        <p className="text-sm text-surface-400 mt-1">Track your C programming mastery</p>
      </div>

      {/* Summary Cards */}
      <div className="grid grid-cols-2 sm:grid-cols-4 gap-4 mb-8">
        <div className="card text-center">
          <p className="text-3xl font-bold text-accent-400">{summary.mastered || 0}</p>
          <p className="text-xs text-surface-400 mt-1">Mastered</p>
        </div>
        <div className="card text-center">
          <p className="text-3xl font-bold text-blue-400">{summary.in_progress || 0}</p>
          <p className="text-xs text-surface-400 mt-1">In Progress</p>
        </div>
        <div className="card text-center">
          <p className="text-3xl font-bold text-danger-400">{summary.struggling || 0}</p>
          <p className="text-xs text-surface-400 mt-1">Struggling</p>
        </div>
        <div className="card text-center">
          <p className="text-3xl font-bold text-surface-400">{summary.not_started || 0}</p>
          <p className="text-xs text-surface-400 mt-1">Not Started</p>
        </div>
      </div>

      {/* Overall Progress Bar */}
      <div className="card mb-8">
        <div className="flex items-center justify-between mb-2">
          <span className="text-sm font-medium text-surface-200">Overall Progress</span>
          <span className="text-sm text-surface-400">
            {summary.mastered || 0}/{summary.total_concepts || 0} concepts mastered
          </span>
        </div>
        <div className="h-3 bg-surface-700 rounded-full overflow-hidden">
          <div
            className="h-full bg-gradient-to-r from-accent-500 to-emerald-500 rounded-full transition-all duration-700"
            style={{
              width: `${summary.total_concepts ? (summary.mastered / summary.total_concepts) * 100 : 0}%`,
            }}
          />
        </div>
      </div>

      {/* Concepts Grid */}
      <h2 className="text-lg font-semibold text-surface-200 mb-4">All Concepts</h2>
      <ProgressView concepts={progress?.concepts || []} />
    </div>
  );
}
