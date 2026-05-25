"use client"

import { useState, useCallback } from "react"
import { ScannerHeader } from "./header"
import { CodeInput } from "./code-input"
import { ScanButton } from "./scan-button"
import { ScanResults, type ScanResult } from "./scan-results"
import { ErrorDisplay } from "./error-display"

export function ScannerDashboard() {
  const [code, setCode] = useState("")
  const [loading, setLoading] = useState(false)
  const [result, setResult] = useState<ScanResult | null>(null)
  const [error, setError] = useState<string | null>(null)

  const handleScan = useCallback(async () => {
    if (!code.trim()) return

    setLoading(true)
    setResult(null)
    setError(null)

    try {
      const response = await fetch("https://adeenaramzan93-securescope-ai-api.hf.space/scan", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ code }),
      })

      if (!response.ok) {
        throw new Error(`Server responded with ${response.status}`)
      }

      const data: ScanResult = await response.json()
      setResult(data)
    } catch (err) {
      setError(
        err instanceof Error
          ? err.message
          : "An unexpected error occurred. Please try again."
      )
    } finally {
      setLoading(false)
    }
  }, [code])

  return (
    <main className="dot-grid flex min-h-screen items-start justify-center px-4 py-12 sm:px-6 lg:px-8">
      <div className="w-full max-w-2xl">
        <div className="flex flex-col gap-8">
          <ScannerHeader />

          <section className="flex flex-col gap-4" aria-label="Code scanner">
            <CodeInput code={code} onChange={setCode} disabled={loading} />
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
              className="rounded-lg border border-border bg-card p-5"
            >
              <ScanResults result={result} />
            </section>
          )}

          <footer className="flex items-center justify-center pb-4">
            <p className="text-xs text-muted-foreground/50">
              SecureScope AI v1.0 &mdash; Ensemble vulnerability detection
            </p>
          </footer>
        </div>
      </div>
    </main>
  )
}
