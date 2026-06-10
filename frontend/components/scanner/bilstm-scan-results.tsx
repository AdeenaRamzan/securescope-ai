"use client"

import { ShieldAlert, ShieldCheck } from "lucide-react"

export interface BiLSTMScanResult {
  is_vulnerable: boolean
  confidence: number
  risk_level: "HIGH" | "MEDIUM" | "LOW" | "SAFE" | "INCONCLUSIVE"
  threshold_used: number
  model_version: string
  model_name: string
  model_probs: {
    bilstm: number
  }
  sequence: {
    max_len: number
    vocab_size: number
  }
  scan_time_ms: number
}

interface BiLSTMScanResultsProps {
  result: BiLSTMScanResult
}

export function BiLSTMScanResults({ result }: BiLSTMScanResultsProps) {
  const isVulnerable = result.is_vulnerable
  const StatusIcon = isVulnerable ? ShieldAlert : ShieldCheck
  const statusColor = isVulnerable ? "text-red-400" : "text-primary"
  const statusBg = isVulnerable
    ? "bg-red-500/10 border-red-500/30 glow-red"
    : "bg-primary/10 border-primary/30 glow-green"

  return (
    <div className="flex flex-col gap-4">
      <div className="flex justify-center">
        <div
          className={`${statusBg} animate-pulse-glow flex items-center gap-3 rounded-xl border px-6 py-3`}
        >
          <StatusIcon className={`h-6 w-6 ${statusColor}`} />
          <span className={`text-xl font-bold ${statusColor}`}>
            {isVulnerable ? "VULNERABLE" : "SAFE"}
          </span>
        </div>
      </div>

      <div className="rounded-lg border border-border bg-card p-4">
        <div className="mb-2 flex items-center justify-between">
          <span className="text-sm text-muted-foreground">
            Vulnerable Probability
          </span>
          <span className="text-sm font-semibold text-foreground">
            {(result.confidence * 100).toFixed(1)}%
          </span>
        </div>
        <div className="h-2 w-full overflow-hidden rounded-full bg-muted">
          <div
            className="animate-fill-bar h-full rounded-full"
            style={{
              width: `${result.confidence * 100}%`,
              background: isVulnerable
                ? "linear-gradient(90deg, #ff6b6b, #ff4757)"
                : "linear-gradient(90deg, #00ff88, #00d4ff)",
            }}
          />
        </div>
        <p className="mt-2 text-xs text-muted-foreground">
          Threshold: {(result.threshold_used * 100).toFixed(0)}%
        </p>
      </div>

      <div className="grid grid-cols-2 gap-3">
        <div className="flex flex-col items-center gap-1 rounded-lg border border-border bg-card p-3">
          <span className="text-[11px] font-medium text-muted-foreground uppercase tracking-wider">
            Decision
          </span>
          <span
            className={`text-lg font-bold ${isVulnerable ? "text-red-400" : "text-primary"}`}
          >
            {isVulnerable ? "Vulnerable" : "Safe"}
          </span>
        </div>
        <div className="flex flex-col items-center gap-1 rounded-lg border border-border bg-card p-3">
          <span className="text-[11px] font-medium text-muted-foreground uppercase tracking-wider">
            BiLSTM Score
          </span>
          <span className="text-lg font-bold text-foreground">
            {(result.model_probs.bilstm * 100).toFixed(1)}%
          </span>
        </div>
      </div>

      <div className="flex items-center justify-between border-t border-border pt-3">
        <span className="text-xs text-muted-foreground">
          Scan time: {result.scan_time_ms.toFixed(0)}ms
        </span>
        <span className="text-xs text-muted-foreground">
          {result.model_version}
        </span>
      </div>
    </div>
  )
}
