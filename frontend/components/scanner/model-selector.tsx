"use client"

export type ScanMode = "ensemble" | "bilstm" | "cascade"

interface ModelSelectorProps {
  selectedMode: ScanMode
  onModeChange: (mode: ScanMode) => void
}

const modes = [
  {
    id: "ensemble" as const,
    label: "Ensemble Features",
    description: "ANN, XGBoost, and LightGBM over handcrafted security signals.",
  },
  {
    id: "bilstm" as const,
    label: "BiLSTM Sequence",
    description: "Token sequence modeling for deeper contextual vulnerability patterns.",
  },
  {
    id: "cascade" as const,
    label: "Cascade P1+P2",
    description: "Fast feature gate plus BiLSTM confirmation through /scan/deep.",
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

      <div className="grid gap-2 md:grid-cols-3">
        {modes.map((mode) => {
          const active = selectedMode === mode.id

          return (
            <button
              key={mode.id}
              type="button"
              onClick={() => onModeChange(mode.id)}
              className={`min-h-24 rounded-lg border p-3 text-left transition-smooth ${
                active
                  ? "border-primary/60 bg-primary/10 shadow-lg shadow-primary/10"
                  : "border-border bg-muted/30 hover:border-primary/30 hover:bg-muted/50"
              }`}
            >
              <span
                className={`block text-sm font-semibold ${
                  active ? "text-primary" : "text-foreground"
                }`}
              >
                {mode.label}
              </span>
              <span className="mt-1 block text-xs leading-5 text-muted-foreground">
                {mode.description}
              </span>
            </button>
          )
        })}
      </div>
    </div>
  )
}
