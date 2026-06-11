"use client"

import { useState, useCallback } from "react"
import { ScannerHeader } from "./header"
import { CodeInput } from "./code-input"
import { ScanButton } from "./scan-button"
import { ScanResults, type ScanResult } from "./scan-results"
import { ErrorDisplay } from "./error-display"
import { ModelSelector, type ScanMode } from "./model-selector"

const API_BASE = process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://localhost:8000"

const endpoints: Record<ScanMode, string> = {
  ensemble: "/scan",
  bilstm: "/scan/bilstm",
  cascade: "/scan/deep",
}

export function ScannerDashboard() {
  const [code, setCode] = useState("")
  const [mode, setMode] = useState<ScanMode>("ensemble")
  const [loading, setLoading] = useState(false)
  const [result, setResult] = useState<ScanResult | null>(null)
  const [error, setError] = useState<string | null>(null)

  const handleScan = useCallback(async () => {
    if (!code.trim()) return

    setLoading(true)
    setResult(null)
    setError(null)

    try {
      const response = await fetch(`${API_BASE}${endpoints[mode]}`, {
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
            <ScanButton
              onClick={handleScan}
              loading={loading}
              disabled={!code.trim()}
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
