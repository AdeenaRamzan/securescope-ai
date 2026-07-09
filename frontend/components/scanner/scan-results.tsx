"use client"

import { Activity, GitBranch, ShieldAlert, ShieldCheck, ShieldQuestion } from "lucide-react"
import type { ScanMode } from "./model-selector"

export interface ScanResult {
  is_vulnerable: boolean
  confidence: number
  risk_level: "HIGH" | "MEDIUM" | "LOW" | "SAFE" | "INCONCLUSIVE"
  phase1_confidence?: number
  phase2_confidence?: number
  model_probs?: {
    ann?: number
    xgboost?: number
    lightgbm?: number
    bilstm?: number
  }
  features_fired?: string[]
  scan_time_ms: number
  model_version?: string
  threshold_used?: number
  model_name?: string
  vulnerability_type?: string
  danger?: string
  fix?: string
  owasp_ref?: string
  pipeline?: string
  llm?: string
  sequence?: {
    max_len: number
    vocab_size: number
  }
}

const riskConfig: Record<
  ScanResult["risk_level"],
  { color: string; glow: string; bgColor: string; icon: typeof ShieldAlert }
> = {
  HIGH: {
    color: "text-red-300",
    glow: "glow-red",
    bgColor: "bg-red-500/10 border-red-400/35",
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
    color: "text-cyan-200",
    glow: "glow-green",
    bgColor: "bg-primary/10 border-primary/35",
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
  mode: ScanMode
}

const modeLabels: Record<ScanMode, string> = {
  ensemble: "Ensemble Features",
  bilstm: "BiLSTM Sequence",
  cascade: "Phase 1 + Phase 2",
  deep: "CodeBERT + RAG",
}

const modelBreakdown = [
  { name: "ANN", key: "ann" },
  { name: "XGBoost", key: "xgboost" },
  { name: "LightGBM", key: "lightgbm" },
  { name: "BiLSTM", key: "bilstm" },
] as const

function formatPercent(value?: number) {
  if (typeof value !== "number") return "N/A"
  return `${(value * 100).toFixed(1)}%`
}

function clampPercent(value?: number) {
  if (typeof value !== "number") return 0
  return Math.max(0, Math.min(100, value * 100))
}

function formatVulnerabilityType(value?: string) {
  if (!value || value === "unknown") return "Unknown"
  return value
    .split("_")
    .map((part) => part.charAt(0).toUpperCase() + part.slice(1))
    .join(" ")
}

export function ScanResults({ result, mode }: ScanResultsProps) {
  const config = riskConfig[result.risk_level]
  const RiskIcon = config.icon
  const isDeepScan = mode === "deep"
  const phase1 = result.phase1_confidence
  const phase2 = result.phase2_confidence
  const featuresFired = result.features_fired ?? []
  const modelLabel = result.model_version ?? result.model_name ?? result.pipeline ?? "Phase 3"
  const modelRows = modelBreakdown.filter(
    (model) => typeof result.model_probs?.[model.key] === "number"
  )
  const breakdownRows = isDeepScan
    ? [
        {
          label: "CodeBERT Confidence",
          value: result.confidence,
          display: formatPercent(result.confidence),
        },
        {
          label: "Vulnerability Type",
          display: formatVulnerabilityType(result.vulnerability_type),
        },
        {
          label: "RAG Analysis",
          display:
            result.danger || result.fix || result.owasp_ref
              ? "Generated"
              : result.is_vulnerable
                ? "Not returned"
                : "Not needed",
        },
      ]
    : [
        {
          label: "Phase 1 Confidence",
          value: phase1,
          display: formatPercent(phase1),
        },
        {
          label: "Phase 2 Confidence",
          value: phase2,
          display: formatPercent(phase2),
        },
        {
          label: "Combined Confidence",
          value: result.confidence,
          display: formatPercent(result.confidence),
        },
      ]

  return (
    <div className="flex flex-col gap-5 animate-slide-in-bottom">
      <div className="flex justify-center">
        <div
          className={`${config.bgColor} ${config.glow} animate-pulse-glow flex items-center gap-4 rounded-2xl border px-8 py-4 shadow-2xl`}
          style={{
            background:
              result.risk_level === "HIGH"
                ? "linear-gradient(145deg, rgba(70, 14, 22, 0.72), rgba(16, 8, 13, 0.96))"
                : "linear-gradient(145deg, rgba(0, 213, 255, 0.14), rgba(8, 12, 18, 0.96))",
          }}
        >
          <RiskIcon className={`h-8 w-8 ${config.color} neon-text`} />
          <div className="flex flex-col items-start">
            <span className={`text-3xl font-bold ${config.color} neon-text`}>
              {result.risk_level}
            </span>
            <span className="mt-0.5 text-xs font-medium text-slate-400">
              {result.is_vulnerable ? "Vulnerability Detected" : "No Vulnerability"}
            </span>
          </div>
        </div>
      </div>

      <div className="grid gap-4 md:grid-cols-[220px_1fr]">
        <div className="premium-panel flex flex-col items-center justify-center rounded-lg p-5">
          <div
            className="relative flex h-36 w-36 items-center justify-center rounded-full shadow-[0_0_34px_rgba(0,213,255,0.18)]"
            style={{
              background: `conic-gradient(var(--primary) ${clampPercent(result.confidence)}%, rgba(3,8,14,0.95) 0)`,
            }}
          >
            <div className="absolute inset-3 rounded-full border border-cyan-400/10 bg-[#060a10]" />
            <div className="relative text-center">
              <div className="text-3xl font-bold text-primary neon-text">
                {formatPercent(result.confidence)}
              </div>
              <div className="mt-1 text-[10px] font-semibold uppercase tracking-wider text-slate-500">
                Confidence
              </div>
            </div>
          </div>
        </div>

        <div className="premium-panel rounded-lg p-4">
          <div className="mb-4 flex items-center justify-between gap-3">
            <div className="flex items-center gap-2">
              <GitBranch className="h-4 w-4 text-secondary neon-text" />
              <span className="text-sm font-semibold text-slate-100">
                Model Breakdown
              </span>
            </div>
            <span className="rounded-full border border-primary/20 bg-primary/10 px-3 py-1 text-xs font-semibold text-primary shadow-[0_0_18px_rgba(0,213,255,0.12)]">
              {modeLabels[mode]}
            </span>
          </div>

          <div className="space-y-3">
            {breakdownRows.map((item) => (
              <div key={item.label}>
                <div className="mb-1.5 flex items-center justify-between">
                  <span className="text-xs font-medium text-slate-500">{item.label}</span>
                  <span className="text-xs font-semibold text-slate-200">
                    {item.display}
                  </span>
                </div>
                {typeof item.value === "number" && (
                  <div className="meter-track h-2 overflow-hidden rounded-full">
                    <div
                      className="animate-fill-bar h-full rounded-full bg-gradient-to-r from-primary via-cyan-200 to-secondary shadow-[0_0_16px_rgba(0,213,255,0.35)]"
                      style={{ width: `${clampPercent(item.value)}%` }}
                    />
                  </div>
                )}
              </div>
            ))}
          </div>
        </div>
      </div>

      {modelRows.length > 0 && (
        <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-4">
          {modelRows.map((model) => (
            <div
              key={model.key}
              className="premium-panel flex flex-col items-center gap-2 rounded-lg p-3 transition-smooth hover:border-primary/45 hover:shadow-[0_0_24px_rgba(0,213,255,0.12)]"
            >
              <span className="text-[10px] font-semibold uppercase tracking-wider text-slate-500">
                {model.name}
              </span>
              <div className="text-2xl font-bold text-slate-100">
                {formatPercent(result.model_probs?.[model.key])}
              </div>
              <div className="meter-track h-1 w-full overflow-hidden rounded-full">
                <div
                  className="h-full bg-gradient-to-r from-primary to-secondary shadow-[0_0_12px_rgba(255,62,165,0.32)]"
                  style={{ width: `${clampPercent(result.model_probs?.[model.key])}%` }}
                />
              </div>
            </div>
          ))}
        </div>
      )}

      <div className="grid gap-3 sm:grid-cols-3">
        {[
          { label: "Pipeline", value: modeLabels[mode] },
          { label: "Scan Time", value: `${result.scan_time_ms.toFixed(0)}ms` },
          { label: "Model", value: modelLabel },
        ].map((item) => (
          <div
            key={item.label}
            className="premium-panel flex flex-col gap-1 rounded-lg p-3"
          >
            <span className="text-[10px] font-semibold uppercase tracking-wider text-slate-500">
              {item.label}
            </span>
            <span className="truncate text-sm font-semibold text-slate-100">{item.value}</span>
          </div>
        ))}
      </div>

      {featuresFired.length > 0 && (
        <div className="premium-panel rounded-lg p-4">
          <div className="mb-3 flex items-center gap-2">
            <Activity className="h-4 w-4 text-secondary neon-text" />
            <p className="text-xs font-semibold uppercase tracking-wider text-slate-500">
              Security Insights
            </p>
          </div>
          <div className="flex flex-wrap gap-2">
            {featuresFired.map((feature) => (
              <span
                key={feature}
                className="animate-fade-scale-in rounded-full border border-primary/15 bg-primary/10 px-3 py-1.5 text-xs font-semibold text-primary shadow-[0_0_18px_rgba(0,213,255,0.1)] transition-smooth hover:border-primary/35 hover:bg-primary/15"
              >
                {feature}
              </span>
            ))}
          </div>
        </div>
      )}
    </div>
  )
}
