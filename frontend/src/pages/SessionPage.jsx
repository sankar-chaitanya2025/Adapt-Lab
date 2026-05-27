import { useState, useEffect } from 'react';
import useSession from '../hooks/useSession';
import CodeEditor from '../components/CodeEditor';
import ProblemDisplay from '../components/ProblemDisplay';
import SocraticHint from '../components/SocraticHint';
import SubmissionControls from '../components/SubmissionControls';

export default function SessionPage() {
  const {
    currentProblem,
    sessionId,
    submissionResult,
    socraticHint,
    isLoading,
    error,
    startSession,
    submitCode,
    nextProblem,
    clearError,
  } = useSession();

  const [code, setCode] = useState('');
  const [initialized, setInitialized] = useState(false);

  // Load first problem on mount
  useEffect(() => {
    if (!initialized) {
      setInitialized(true);
      startSession().catch(() => {});
    }
  }, [initialized, startSession]);

  // Reset editor when new problem loads
  useEffect(() => {
    if (currentProblem?.starter_code) {
      setCode(currentProblem.starter_code);
    }
  }, [currentProblem]);

  const handleSubmit = async () => {
    if (!sessionId || !code.trim()) return;
    try {
      await submitCode(sessionId, code);
    } catch {
      // Error is handled by the hook
    }
  };

  const handleNext = async () => {
    try {
      await nextProblem();
    } catch {
      // Error is handled by the hook
    }
  };

  // Loading state for initial problem generation
  if (!currentProblem && isLoading) {
    return (
      <div className="h-[calc(100vh-4rem)] flex items-center justify-center">
        <div className="text-center">
          <div className="inline-flex items-center justify-center w-16 h-16 bg-surface-800 rounded-2xl mb-4">
            <svg className="w-8 h-8 text-accent-400 animate-spin" fill="none" viewBox="0 0 24 24">
              <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
              <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z" />
            </svg>
          </div>
          <h2 className="text-lg font-semibold text-surface-200 mb-1">Generating Your Problem</h2>
          <p className="text-sm text-surface-400">The AI is crafting a challenge just for you...</p>
        </div>
      </div>
    );
  }

  // Error state
  if (!currentProblem && error) {
    return (
      <div className="h-[calc(100vh-4rem)] flex items-center justify-center">
        <div className="text-center max-w-md">
          <div className="inline-flex items-center justify-center w-16 h-16 bg-danger-400/10 rounded-2xl mb-4">
            <svg className="w-8 h-8 text-danger-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.964-.833-2.732 0L4.082 16.5c-.77.833.192 2.5 1.732 2.5z" />
            </svg>
          </div>
          <h2 className="text-lg font-semibold text-surface-200 mb-1">Something went wrong</h2>
          <p className="text-sm text-surface-400 mb-4">{error}</p>
          <button onClick={() => { clearError(); startSession(); }} className="btn-primary">
            Try Again
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="h-[calc(100vh-4rem)] flex">
      {/* Left Panel — Problem + Hints (40%) */}
      <div className="w-[40%] flex flex-col border-r border-surface-700/50 overflow-hidden">
        {/* Problem Area */}
        <div className="flex-1 overflow-y-auto p-5 space-y-4">
          <ProblemDisplay problem={currentProblem} />

          {/* Submission results */}
          {submissionResult && submissionResult.results && (
            <div className="animate-fade-in">
              <h3 className="text-sm font-medium text-surface-200 mb-2">Results</h3>
              <div className="space-y-1.5">
                {submissionResult.results.map((r, i) => (
                  <div
                    key={i}
                    className={`flex items-center gap-2 px-3 py-2 rounded-lg text-xs font-mono ${
                      r.status === 'accepted'
                        ? 'bg-accent-500/10 text-accent-400 border border-accent-500/20'
                        : 'bg-danger-400/10 text-danger-400 border border-danger-400/20'
                    }`}
                  >
                    {r.status === 'accepted' ? (
                      <svg className="w-3.5 h-3.5 shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                      </svg>
                    ) : (
                      <svg className="w-3.5 h-3.5 shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                      </svg>
                    )}
                    <span>Test {r.test_index + 1}: {r.status === 'accepted' ? 'Passed' : r.status.replace(/_/g, ' ')}</span>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Congratulations message */}
          {submissionResult?.outcome === 'pass' && (
            <div className="animate-slide-up bg-gradient-to-br from-accent-500/10 to-emerald-500/10 border border-accent-500/20 rounded-xl p-4 text-center">
              <div className="text-3xl mb-2">🎉</div>
              <p className="text-sm font-semibold text-accent-400">All tests passed!</p>
              <p className="text-xs text-surface-400 mt-1">Great work! Click "Next Problem" to continue.</p>
            </div>
          )}

          {/* Socratic Hint */}
          <SocraticHint hint={socraticHint} />
        </div>
      </div>

      {/* Right Panel — Editor (60%) */}
      <div className="w-[60%] flex flex-col overflow-hidden">
        {/* Editor Header */}
        <div className="bg-surface-800/80 border-b border-surface-700/50 px-4 py-2.5 flex items-center justify-between">
          <div className="flex items-center gap-2">
            <div className="flex gap-1.5">
              <div className="w-3 h-3 rounded-full bg-danger-400/60" />
              <div className="w-3 h-3 rounded-full bg-warning-400/60" />
              <div className="w-3 h-3 rounded-full bg-accent-400/60" />
            </div>
            <span className="text-xs text-surface-400 ml-2 font-mono">solution.c</span>
          </div>
          <span className="text-xs text-surface-500">C (GCC)</span>
        </div>

        {/* Monaco Editor */}
        <div className="flex-1 overflow-hidden">
          <CodeEditor
            value={code}
            onChange={setCode}
            language="c"
          />
        </div>

        {/* Control Bar */}
        <SubmissionControls
          onSubmit={handleSubmit}
          onNext={handleNext}
          isLoading={isLoading}
          submissionResult={submissionResult}
        />
      </div>
    </div>
  );
}
