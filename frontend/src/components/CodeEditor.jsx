import Editor from '@monaco-editor/react';

export default function CodeEditor({ value, onChange, language = 'c' }) {
  const handleEditorChange = (val) => {
    if (onChange) onChange(val);
  };

  return (
    <div className="h-full rounded-b-xl overflow-hidden border border-surface-700/50 border-t-0">
      <Editor
        height="100%"
        language={language}
        value={value}
        onChange={handleEditorChange}
        theme="vs-dark"
        options={{
          minimap: { enabled: false },
          fontSize: 14,
          fontFamily: "'JetBrains Mono', 'Fira Code', monospace",
          automaticLayout: true,
          scrollBeyondLastLine: false,
          padding: { top: 16, bottom: 16 },
          lineNumbers: 'on',
          renderLineHighlight: 'line',
          bracketPairColorization: { enabled: true },
          tabSize: 4,
          insertSpaces: true,
          wordWrap: 'off',
          smoothScrolling: true,
          cursorBlinking: 'smooth',
          cursorSmoothCaretAnimation: 'on',
        }}
        loading={
          <div className="flex items-center justify-center h-full bg-surface-900">
            <div className="flex items-center gap-3 text-surface-400">
              <svg className="w-5 h-5 animate-spin" fill="none" viewBox="0 0 24 24">
                <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
                <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z" />
              </svg>
              Loading editor...
            </div>
          </div>
        }
      />
    </div>
  );
}
