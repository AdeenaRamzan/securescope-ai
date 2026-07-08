"use client"

import { useState, useCallback } from "react"
import { ScannerHeader } from "./header"
import { CodeInput } from "./code-input"
import { ScanButtons } from "./scan-buttons"
import { ScanResults, type ScanResult } from "./scan-results"
import { AiSecurityAnalysis } from "./ai-security-analysis"
import { ErrorDisplay } from "./error-display"
import { ModelSelector, type ScanMode } from "./model-selector"

const API_BASE = process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://localhost:8000"

const endpoints: Record<ScanMode, string> = {
  ensemble: "/scan",
  bilstm: "/scan/bilstm",
  cascade: "/scan/cascade",
  deep: "/scan/deep",
}

export function ScannerDashboard() {
  const [code, setCode] = useState("")
  const [mode, setMode] = useState<ScanMode>("ensemble")
  const [loading, setLoading] = useState(false)
  const [loadingType, setLoadingType] = useState<"quick" | "deep">("quick")
  const [lastScanType, setLastScanType] = useState<"quick" | "deep">("quick")
  const [result, setResult] = useState<ScanResult | null>(null)
  const [error, setError] = useState<string | null>(null)
  const quickButtonLabel =
    mode === "bilstm" ? "Run BiLSTM" : mode === "cascade" ? "Run P1 + P2" : "Quick Scan"

  const handleScan = useCallback(async (scanType: "quick" | "deep") => {
    if (!code.trim()) return

    setLoading(true)
    setLoadingType(scanType)
    setLastScanType(scanType)
    setResult(null)
    setError(null)

    try {
      const selectedMode = scanType === "deep" ? "deep" : mode === "deep" ? "ensemble" : mode
      const endpoint = endpoints[selectedMode]
      setMode(selectedMode)

      const response = await fetch(`${API_BASE}${endpoint}`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ code, language: "python" }),
      })

      if (!response.ok) {
        throw new Error(`Server responded with ${response.status}`)
      }

      const data = await response.json()
      setResult(data as ScanResult)
    } catch (err) {
      setError(
        err instanceof Error
          ? err.message
          : "An unexpected error occurred. Please try again."
      )
    } finally {
      setLoading(false)
    }
  }, [code, mode])

  const handleClear = useCallback(() => {
    setCode("")
    setResult(null)
    setError(null)
  }, [])

  return (
    <main className="dot-grid flex min-h-screen items-start justify-center px-4 py-10 sm:px-6 lg:px-8">
      <div className="w-full max-w-4xl">
        <div className="flex flex-col gap-8">
          <ScannerHeader mode={mode} />

          <section className="flex flex-wrap items-center justify-center gap-3">
            {[
              { label: "Phase 1: Ensemble ML", color: "#06b6d4", highlight: false },
              { label: "Phase 2: BiLSTM", color: "#06b6d4", highlight: false },
              { label: "Phase 3: CodeBERT + RAG", color: "#ec4899", highlight: true },
            ].map((badge) => (
              <span
                key={badge.label}
                className={`rounded-full border px-3 py-1.5 text-xs font-semibold ${
                  badge.highlight ? "animate-pulse" : ""
                }`}
                style={{
                  borderColor: badge.color,
                  color: badge.color,
                  background: `${badge.color}18`,
                  boxShadow: badge.highlight
                    ? `0 0 20px ${badge.color}70, 0 0 40px ${badge.color}40`
                    : `0 0 14px ${badge.color}55, 0 0 28px ${badge.color}25`,
                  textShadow: `0 0 10px ${badge.color}50`,
                }}
              >
                {badge.label}
              </span>
            ))}
          </section>

          <section className="glass rounded-lg p-4" aria-label="Model selection">
            <ModelSelector selectedMode={mode} onModeChange={setMode} />
          </section>

          <section className="flex flex-col gap-4" aria-label="Code scanner">
            <CodeInput
              code={code}
              onChange={setCode}
              onClear={handleClear}
              disabled={loading}
            />
            <ScanButtons
              onQuickScan={() => handleScan("quick")}
              onDeepScan={() => handleScan("deep")}
              loading={loading}
              disabled={!code.trim()}
              loadingType={loadingType}
              quickLabel={quickButtonLabel}
            />
          </section>

          {error && (
            <section aria-label="Scan error">
              <ErrorDisplay message={error} />
            </section>
          )}

          {result && (
            <section
              aria-label="Scan results"
              className="glass rounded-lg p-6"
            >
              <ScanResults result={result} mode={mode} />
              {lastScanType === "deep" &&
                (result.danger || result.fix || result.owasp_ref) && (
                  <AiSecurityAnalysis
                    danger={result.danger ?? ""}
                    fix={result.fix ?? ""}
                    owaspRef={result.owasp_ref ?? ""}
                  />
                )}
            </section>
          )}

          <footer className="flex items-center justify-center pb-4">
            <p className="text-xs text-muted-foreground/50">
              SecureScope AI v1.0 &mdash; Multi-mode vulnerability analysis
            </p>
          </footer>
        </div>
      </div>
    </main>
  )
}
