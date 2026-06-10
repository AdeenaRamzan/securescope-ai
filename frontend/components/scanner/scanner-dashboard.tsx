"use client"

import { useState, useCallback } from "react"
import { ScannerHeader } from "./header"
import { CodeInput } from "./code-input"
import { ScanButton } from "./scan-button"
import { ScanResults, type ScanResult } from "./scan-results"
import { BiLSTMScanResults, type BiLSTMScanResult } from "./bilstm-scan-results"
import { ErrorDisplay } from "./error-display"
import { Tabs, TabsList, TabsTrigger } from "@/components/ui/tabs"

const API_BASE = "https://adeenaramzan93-securescope-ai-api.hf.space"

type ScannerMode = "ensemble" | "bilstm"

export function ScannerDashboard() {
  const [code, setCode] = useState("")
  const [mode, setMode] = useState<ScannerMode>("ensemble")
  const [loading, setLoading] = useState(false)
  const [ensembleResult, setEnsembleResult] = useState<ScanResult | null>(null)
  const [bilstmResult, setBilstmResult] = useState<BiLSTMScanResult | null>(null)
  const [error, setError] = useState<string | null>(null)

  const handleScan = useCallback(async () => {
    if (!code.trim()) return

    setLoading(true)
    setEnsembleResult(null)
    setBilstmResult(null)
    setError(null)

    const endpoint = mode === "ensemble" ? "/scan" : "/scan/bilstm"

    try {
      const response = await fetch(`${API_BASE}${endpoint}`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ code }),
      })

      if (!response.ok) {
        throw new Error(`Server responded with ${response.status}`)
      }

      const data = await response.json()

      if (mode === "ensemble") {
        setEnsembleResult(data as ScanResult)
      } else {
        setBilstmResult(data as BiLSTMScanResult)
      }
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

  const hasResult = ensembleResult !== null || bilstmResult !== null

  return (
    <main className="dot-grid flex min-h-screen items-start justify-center px-4 py-12 sm:px-6 lg:px-8">
      <div className="w-full max-w-2xl">
        <div className="flex flex-col gap-8">
          <ScannerHeader />

          <section className="flex flex-col gap-4" aria-label="Code scanner">
            <div className="flex justify-center">
              <Tabs
                value={mode}
                onValueChange={(value) => setMode(value as ScannerMode)}
              >
                <TabsList>
                  <TabsTrigger value="ensemble">Ensemble Features</TabsTrigger>
                  <TabsTrigger value="bilstm">BiLSTM Sequence</TabsTrigger>
                </TabsList>
              </Tabs>
            </div>

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

          {hasResult && (
            <section
              aria-label="Scan results"
              className="rounded-lg border border-border bg-card p-5"
            >
              {ensembleResult && <ScanResults result={ensembleResult} />}
              {bilstmResult && <BiLSTMScanResults result={bilstmResult} />}
            </section>
          )}

          <footer className="flex items-center justify-center pb-4">
            <p className="text-xs text-muted-foreground/50">
              SecureScope AI v1.0 &mdash;{" "}
              {mode === "ensemble"
                ? "Ensemble vulnerability detection"
                : "BiLSTM sequence analysis"}
            </p>
          </footer>
        </div>
      </div>
    </main>
  )
}
