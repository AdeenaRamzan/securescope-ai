"use client"

import { ShieldAlert, ShieldCheck, ShieldQuestion } from "lucide-react"

export interface ScanResult {
  is_vulnerable: boolean
  confidence: number
  risk_level: "HIGH" | "MEDIUM" | "LOW" | "SAFE" | "INCONCLUSIVE"
  model_probs: {
    ann: number
    xgboost: number
    lightgbm: number
  }
  features_fired: string[]
  scan_time_ms: number
  model_version: string
  threshold_used: number
}

const riskConfig: Record<
  ScanResult["risk_level"],
  { color: string; glow: string; bgColor: string; icon: typeof ShieldAlert }
> = {
  HIGH: {
    color: "text-red-400",
    glow: "glow-red",
    bgColor: "bg-red-500/10 border-red-500/30",
    icon: ShieldAlert,
  },
  MEDIUM: {
    color: "text-orange-400",
    glow: "glow-orange",
    bgColor: "bg-orange-500/10 border-orange-500/30",
    icon: ShieldAlert,
  },
  LOW: {
    color: "text-yellow-400",
    glow: "glow-yellow",
    bgColor: "bg-yellow-500/10 border-yellow-500/30",
    icon: ShieldAlert,
  },
  SAFE: {
    color: "text-primary",
    glow: "glow-green",
    bgColor: "bg-primary/10 border-primary/30",
    icon: ShieldCheck,
  },
  INCONCLUSIVE: {
    color: "text-muted-foreground",
    glow: "",
    bgColor: "bg-muted border-border",
    icon: ShieldQuestion,
  },
}

interface ScanResultsProps {
  result: ScanResult
}

export function ScanResults({ result }: ScanResultsProps) {
  const config = riskConfig[result.risk_level]
  const RiskIcon = config.icon

  return (
    <div className="flex flex-col gap-4">
      {/* Risk Badge */}
      <div className="flex justify-center">
        <div
          className={`${config.bgColor} ${config.glow} animate-pulse-glow flex items-center gap-3 rounded-xl border px-6 py-3`}
        >
          <RiskIcon className={`h-6 w-6 ${config.color}`} />
          <span className={`text-xl font-bold ${config.color}`}>
            {result.risk_level}
          </span>
        </div>
      </div>

      {/* Confidence Bar */}
      <div className="rounded-lg border border-border bg-card p-4">
        <div className="mb-2 flex items-center justify-between">
          <span className="text-sm text-muted-foreground">Confidence</span>
          <span className="text-sm font-semibold text-foreground">
            {(result.confidence * 100).toFixed(1)}%
          </span>
        </div>
        <div className="h-2 w-full overflow-hidden rounded-full bg-muted">
          <div
            className="animate-fill-bar h-full rounded-full"
            style={{
              width: `${result.confidence * 100}%`,
              background: "linear-gradient(90deg, #00ff88, #00d4ff)",
            }}
          />
        </div>
      </div>

      {/* Model Probabilities */}
      <div className="grid grid-cols-3 gap-3">
        {(
          [
            { name: "ANN", key: "ann" },
            { name: "XGBoost", key: "xgboost" },
            { name: "LightGBM", key: "lightgbm" },
          ] as const
        ).map((model) => (
          <div
            key={model.key}
            className="flex flex-col items-center gap-1 rounded-lg border border-border bg-card p-3"
          >
            <span className="text-[11px] font-medium text-muted-foreground uppercase tracking-wider">
              {model.name}
            </span>
            <span className="text-lg font-bold text-foreground">
              {(result.model_probs[model.key] * 100).toFixed(1)}%
            </span>
          </div>
        ))}
      </div>

      {/* Features Fired */}
      {result.features_fired.length > 0 && (
        <div className="rounded-lg border border-border bg-card p-4">
          <p className="mb-2.5 text-xs font-medium text-muted-foreground uppercase tracking-wider">
            Features Detected
          </p>
          <div className="flex flex-wrap gap-1.5">
            {result.features_fired.map((feature) => (
              <span
                key={feature}
                className="rounded-full bg-primary/10 px-2.5 py-0.5 text-[11px] font-medium text-primary"
              >
                {feature}
              </span>
            ))}
          </div>
        </div>
      )}

      {/* Footer */}
      <div className="flex items-center justify-between border-t border-border pt-3">
        <span className="text-xs text-muted-foreground">
          Scan time: {result.scan_time_ms.toFixed(0)}ms
        </span>
        <span className="text-xs text-muted-foreground">
          Model: {result.model_version}
        </span>
      </div>
    </div>
  )
}
