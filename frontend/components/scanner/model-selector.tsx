"use client"

export type ScanMode = "ensemble" | "bilstm" | "cascade" | "deep"

interface ModelSelectorProps {
  selectedMode: ScanMode
  onModeChange: (mode: ScanMode) => void
}

const modes = [
  {
    id: "ensemble" as const,
    label: "Quick Scan",
    description: "Fast ensemble vulnerability screening",
  },
  {
    id: "bilstm" as const,
    label: "BiLSTM",
    description: "Sequential vulnerability patterns",
  },
  {
    id: "cascade" as const,
    label: "P1 + P2",
    description: "Phase 1 ensemble plus Phase 2 BiLSTM cascade",
  },
  {
    id: "deep" as const,
    label: "Deep Scan",
    description: "Phase 3 CodeBERT + OWASP RAG + AI fixes",
  },
]

export function ModelSelector({ selectedMode, onModeChange }: ModelSelectorProps) {
  return (
    <div className="space-y-3">
      <div className="flex items-center justify-between gap-3">
        <h2 className="text-sm font-semibold text-foreground/80">Analysis Mode</h2>
        <span className="text-xs text-muted-foreground">
          {modes.find((mode) => mode.id === selectedMode)?.label}
        </span>
      </div>

      <div className="grid gap-2 md:grid-cols-4">
        {modes.map((mode) => {
          const active = selectedMode === mode.id
          const accent = mode.id === "deep" ? "#ec4899" : "#06b6d4"

          return (
            <button
              key={mode.id}
              type="button"
              onClick={() => onModeChange(mode.id)}
              className="min-h-12 rounded-lg border px-4 py-3 text-center transition-smooth hover:bg-muted/50"
              style={{
                borderColor: active ? accent : "rgba(255,255,255,0.1)",
                background: active
                  ? mode.id === "deep"
                    ? "linear-gradient(135deg, #ec4899 0%, #be185d 100%)"
                    : "linear-gradient(135deg, #06b6d4 0%, #0891b2 100%)"
                  : "rgba(255,255,255,0.03)",
                boxShadow: active
                  ? `0 0 20px ${accent}66, 0 0 36px ${accent}33`
                  : "none",
              }}
            >
              <span
                className="block text-sm font-semibold"
                style={{ color: active ? "#ffffff" : accent }}
              >
                {mode.label}
              </span>
            </button>
          )
        })}
      </div>

      <div className="rounded-lg border border-primary/40 bg-primary/10 px-3 py-2 text-xs font-semibold text-muted-foreground">
        {modes.find((mode) => mode.id === selectedMode)?.description}
      </div>
    </div>
  )
}
