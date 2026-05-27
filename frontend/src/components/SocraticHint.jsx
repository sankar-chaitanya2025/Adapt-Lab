export default function SocraticHint({ hint }) {
  if (!hint) return null;

  return (
    <div className="animate-fade-in">
      <div className="rounded-xl bg-gradient-to-br from-hint-500/10 to-hint-600/5 border border-hint-500/20 p-4">
        <div className="flex items-start gap-3">
          {/* Thinking Icon */}
          <div className="shrink-0 mt-0.5">
            <div className="w-8 h-8 rounded-full bg-hint-500/20 flex items-center justify-center">
              <svg className="w-4 h-4 text-hint-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z" />
              </svg>
            </div>
          </div>

          {/* Hint Text */}
          <div className="flex-1">
            <p className="text-xs font-medium text-hint-400 uppercase tracking-wider mb-1">
              Think about it...
            </p>
            <p className="text-sm text-hint-200 italic leading-relaxed">
              {hint}
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}
