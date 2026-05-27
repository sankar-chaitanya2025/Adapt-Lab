const STATUS_CONFIG = {
  mastered: {
    bg: 'bg-accent-500/10',
    border: 'border-accent-500/30',
    text: 'text-accent-400',
    bar: 'bg-accent-500',
    label: 'Mastered',
  },
  in_progress: {
    bg: 'bg-blue-500/10',
    border: 'border-blue-500/30',
    text: 'text-blue-400',
    bar: 'bg-blue-500',
    label: 'In Progress',
  },
  struggling: {
    bg: 'bg-danger-400/10',
    border: 'border-danger-400/30',
    text: 'text-danger-400',
    bar: 'bg-danger-400',
    label: 'Struggling',
  },
  not_started: {
    bg: 'bg-surface-700/10',
    border: 'border-surface-600/30',
    text: 'text-surface-400',
    bar: 'bg-surface-600',
    label: 'Not Started',
  },
};

export default function ProgressView({ concepts }) {
  if (!concepts || concepts.length === 0) {
    return (
      <div className="text-center text-surface-400 py-12">
        No progress data yet. Start practicing to see your progress!
      </div>
    );
  }

  return (
    <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
      {concepts.map((concept) => {
        const status = concept.mastery_level >= 3 ? 'mastered' : (concept.status || 'not_started');
        const config = STATUS_CONFIG[status] || STATUS_CONFIG.not_started;
        const successRate = concept.attempts > 0
          ? Math.round((concept.successes / concept.attempts) * 100)
          : 0;
        const masteryPercent = (concept.mastery_level / 5) * 100;

        return (
          <div
            key={concept.id}
            className={`card ${config.bg} border ${config.border} hover:scale-[1.02] transition-transform duration-200`}
          >
            {/* Header */}
            <div className="flex items-start justify-between mb-3">
              <div>
                <h3 className="text-sm font-semibold text-surface-100">
                  {concept.title}
                </h3>
                <p className="text-xs text-surface-400 mt-0.5">Level {concept.level}</p>
              </div>
              <span className={`badge ${config.bg} ${config.text} border ${config.border}`}>
                {config.label}
              </span>
            </div>

            {/* Mastery Bar */}
            <div className="mb-3">
              <div className="flex items-center justify-between text-xs mb-1">
                <span className="text-surface-400">Mastery</span>
                <span className={`font-mono font-medium ${config.text}`}>
                  {concept.mastery_level}/5
                </span>
              </div>
              <div className="h-1.5 bg-surface-700 rounded-full overflow-hidden">
                <div
                  className={`h-full rounded-full ${config.bar} transition-all duration-500`}
                  style={{ width: `${masteryPercent}%` }}
                />
              </div>
            </div>

            {/* Stats */}
            <div className="grid grid-cols-3 gap-2 text-center">
              <div>
                <p className="text-xs text-surface-500">Attempts</p>
                <p className="text-sm font-medium text-surface-200">{concept.attempts}</p>
              </div>
              <div>
                <p className="text-xs text-surface-500">Success</p>
                <p className="text-sm font-medium text-surface-200">{successRate}%</p>
              </div>
              <div>
                <p className="text-xs text-surface-500">Fails</p>
                <p className="text-sm font-medium text-surface-200">{concept.failures}</p>
              </div>
            </div>
          </div>
        );
      })}
    </div>
  );
}
