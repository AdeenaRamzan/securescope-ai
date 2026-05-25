"use client"

interface CodeInputProps {
  code: string
  onChange: (code: string) => void
  disabled: boolean
}

export function CodeInput({ code, onChange, disabled }: CodeInputProps) {
  return (
    <div className="group relative rounded-lg border border-border bg-card transition-all focus-within:border-primary/50 focus-within:glow-green">
      <div className="flex items-center justify-between border-b border-border px-4 py-2">
        <div className="flex items-center gap-2">
          <div className="flex gap-1.5">
            <span className="h-2.5 w-2.5 rounded-full bg-[#ff5f57]" aria-hidden="true" />
            <span className="h-2.5 w-2.5 rounded-full bg-[#febc2e]" aria-hidden="true" />
            <span className="h-2.5 w-2.5 rounded-full bg-[#28c840]" aria-hidden="true" />
          </div>
          <span className="text-xs text-muted-foreground">input.py</span>
        </div>
        <span className="rounded bg-primary/10 px-2 py-0.5 text-[10px] font-medium text-primary">
          Python
        </span>
      </div>

      <textarea
        value={code}
        onChange={(e) => onChange(e.target.value)}
        disabled={disabled}
        placeholder="Paste your Python code here..."
        className="code-textarea w-full resize-none bg-transparent px-4 py-4 font-mono text-sm text-foreground placeholder:text-muted-foreground/50 focus:outline-none disabled:cursor-not-allowed disabled:opacity-50"
        style={{ minHeight: "200px" }}
        spellCheck={false}
        aria-label="Python code input"
      />
    </div>
  )
}
