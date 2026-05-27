export default function SubmissionControls({
  onSubmit,
  onNext,
  isLoading,
  submissionResult,
}) {
  const allPassed = submissionResult?.outcome === 'pass';
  const hasFailed = submissionResult?.outcome === 'fail';
  const results = submissionResult?.results || [];
  const passedCount = results.filter(r => r.status === 'accepted').length;

  return (
    <div className="bg-surface-800/80 border-t border-surface-700/50 px-4 py-3">
      <div className="flex items-center justify-between">
        {/* Results Summary */}
        <div className="flex items-center gap-3">
          {submissionResult && (
            <div className="flex items-center gap-2 text-sm">
              {allPassed ? (
                <span className="flex items-center gap-1.5 text-accent-400 font-medium">
                  <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                  </svg>
                  All tests passed!
                </span>
              ) : (
                <span className="flex items-center gap-1.5 text-surface-300">
                  <span className={`font-mono font-medium ${hasFailed ? 'text-danger-400' : 'text-surface-400'}`}>
                    {passedCount}/{results.length}
                  </span>
                  visible tests passed
                </span>
              )}
            </div>
          )}
        </div>

        {/* Buttons */}
        <div className="flex items-center gap-3">
          <button
            onClick={onSubmit}
            disabled={isLoading || allPassed}
            className="btn-primary flex items-center gap-2"
          >
            {isLoading ? (
              <>
                <svg className="w-4 h-4 animate-spin" fill="none" viewBox="0 0 24 24">
                  <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
                  <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z" />
                </svg>
                Running...
              </>
            ) : (
              <>
                <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M14.752 11.168l-3.197-2.132A1 1 0 0010 9.87v4.263a1 1 0 001.555.832l3.197-2.132a1 1 0 000-1.664z" />
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
                Submit
              </>
            )}
          </button>

          {allPassed && (
            <button
              onClick={onNext}
              disabled={isLoading}
              className="btn-primary bg-gradient-to-r from-accent-500 to-emerald-500 hover:from-accent-400 hover:to-emerald-400 flex items-center gap-2 animate-fade-in"
            >
              <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 7l5 5m0 0l-5 5m5-5H6" />
              </svg>
              Next Problem
            </button>
          )}
        </div>
      </div>
    </div>
  );
}
