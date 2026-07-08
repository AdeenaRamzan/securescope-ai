"use client"

import { Shield } from "lucide-react"
import type { ScanMode } from "./model-selector"

const modeConfig: Record<ScanMode, { description: string; badges: string[] }> = {
  ensemble: {
    description: "Fast Python vulnerability screening with ensemble machine learning.",
    badges: ["Phase 1: Ensemble ML", "Quick Scan", "Real-time"],
  },
  bilstm: {
    description: "Sequential Python token analysis for deeper vulnerability context.",
    badges: ["Phase 2: BiLSTM", "Sequence Learning", "Token Analysis"],
  },
  cascade: {
    description: "Phase 1 ensemble and Phase 2 BiLSTM combined cascade.",
    badges: ["Phase 1 + Phase 2", "Cascade Inference", "Model Fusion"],
  },
  deep: {
    description: "Full AI security analysis with CodeBERT, OWASP retrieval, and generated fixes.",
    badges: ["Phase 3: CodeBERT + RAG", "OWASP Context", "AI Fix"],
  },
}

interface ScannerHeaderProps {
  mode?: ScanMode
}

export function ScannerHeader({ mode = "ensemble" }: ScannerHeaderProps) {
  const config = modeConfig[mode]

  return (
    <header className="flex flex-col items-center gap-4 text-center">
      <div className="relative">
        <div className="absolute inset-0 h-12 w-12 animate-pulse rounded-full bg-primary/30 blur-2xl" aria-hidden="true" />
        <Shield className="relative h-12 w-12 text-primary drop-shadow-lg" />
      </div>

      <div className="flex flex-col items-center gap-2">
        <h1 className="text-4xl font-bold tracking-tight text-foreground drop-shadow-lg">
          SecureScope AI
        </h1>
        <p className="max-w-md text-sm text-muted-foreground transition-smooth">
          {config.description}
        </p>
      </div>

      <div className="flex flex-wrap items-center justify-center gap-2">
        {config.badges.map((badge) => (
          <span
            key={badge}
            className="glass rounded-full px-3 py-1.5 text-xs font-medium text-foreground/80 transition-smooth hover:text-primary"
          >
            {badge}
          </span>
        ))}
      </div>
    </header>
  )
}
