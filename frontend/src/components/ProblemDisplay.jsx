export default function ProblemDisplay({ problem }) {
  if (!problem) return null;

  return (
    <div className="space-y-4">
      {/* Title + Difficulty Badge */}
      <div className="flex items-start justify-between gap-3">
        <h2 className="text-lg font-semibold text-surface-100">{problem.title}</h2>
        <span className="shrink-0 px-2.5 py-1 text-xs font-medium rounded-full bg-accent-600/20 text-accent-400 border border-accent-500/30">
          Lvl {problem.difficulty}
        </span>
      </div>

      {/* Concept Tag */}
      <div className="flex items-center gap-2">
        <span className="text-xs text-surface-400 bg-surface-700/50 px-2 py-0.5 rounded">
          {problem.concept_id?.replace(/_/g, ' ')}
        </span>
      </div>

      {/* Description */}
      <p className="text-sm text-surface-300 leading-relaxed">
        {problem.description}
      </p>

      {/* Test Cases */}
      {problem.test_cases && problem.test_cases.length > 0 && (
        <div>
          <h3 className="text-sm font-medium text-surface-200 mb-2 flex items-center gap-2">
            <svg className="w-4 h-4 text-accent-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2" />
            </svg>
            Test Cases
          </h3>
          <div className="overflow-hidden rounded-lg border border-surface-700/50">
            <table className="w-full text-sm">
              <thead>
                <tr className="bg-surface-800/80">
                  <th className="px-3 py-2 text-left text-xs font-medium text-surface-400 uppercase tracking-wider">#</th>
                  <th className="px-3 py-2 text-left text-xs font-medium text-surface-400 uppercase tracking-wider">Input</th>
                  <th className="px-3 py-2 text-left text-xs font-medium text-surface-400 uppercase tracking-wider">Expected Output</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-surface-700/30">
                {problem.test_cases.map((tc, i) => (
                  <tr key={i} className="hover:bg-surface-800/40 transition-colors">
                    <td className="px-3 py-2 text-surface-500 font-mono text-xs">{i + 1}</td>
                    <td className="px-3 py-2 text-surface-300 font-mono text-xs whitespace-pre-wrap">
                      {tc.input || <span className="text-surface-500 italic">none</span>}
                    </td>
                    <td className="px-3 py-2 text-surface-300 font-mono text-xs whitespace-pre-wrap">
                      {tc.expected_output}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}
    </div>
  );
}
