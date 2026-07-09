"use client"

import { useState, useCallback } from "react"
import type { ScanMode, ScanResult, ScanHistoryItem } from "@/lib/types"
import { getRiskLevel } from "@/lib/types"
import { scanCode } from "@/lib/api"
import { Sidebar } from "./sidebar"
import { HeroSection } from "./hero-section"
import { CodeInputSection } from "./code-input-section"
import { CapabilityCards } from "./capability-cards"
import { ScanModeSelector } from "./scan-mode-selector"
import { ResultsView } from "./results-view"
import { AlertTriangle } from "lucide-react"

export function Dashboard() {
  // ── Core state ──────────────────────────────────────────────
  const [code, setCode] = useState("")
  const [filename, setFilename] = useState("input.py")
  const [scanMode, setScanMode] = useState<ScanMode>("quick")
  const [loading, setLoading] = useState(false)
  const [result, setResult] = useState<ScanResult | null>(null)
  const [error, setError] = useState<string | null>(null)
  const [activeView, setActiveView] = useState<"dashboard" | "results">("dashboard")

  // ── Scan history (session-only) ─────────────────────────────
  const [scanHistory, setScanHistory] = useState<ScanHistoryItem[]>([])

  // ── Handlers ────────────────────────────────────────────────
  const handleScan = useCallback(async () => {
    if (!code.trim()) return

    setLoading(true)
    setError(null)

    try {
      const data = await scanCode(code, scanMode)
      setResult(data)
      setActiveView("results")

      // Add to history
      const historyItem: ScanHistoryItem = {
        id: crypto.randomUUID(),
        filename,
        timestamp: new Date(),
        code,
        mode: scanMode,
        result: data,
        riskLevel: getRiskLevel(data),
      }
      setScanHistory((prev) => [historyItem, ...prev])
    } catch (err) {
      setError(
        err instanceof Error
          ? err.message
          : "An unexpected error occurred. Please try again."
      )
    } finally {
      setLoading(false)
    }
  }, [code, scanMode, filename])

  const handleClear = useCallback(() => {
    setCode("")
    setFilename("input.py")
    setResult(null)
    setError(null)
    setActiveView("dashboard")
  }, [])

  const handleSelectHistoryItem = useCallback((item: ScanHistoryItem) => {
    setCode(item.code)
    setFilename(item.filename)
    setScanMode(item.mode)
    setResult(item.result)
    setActiveView("results")
  }, [])

  const handleDeleteHistoryItem = useCallback((id: string) => {
    setScanHistory((prev) => prev.filter((item) => item.id !== id))
  }, [])

  const handleNavigate = useCallback((view: "dashboard" | "results") => {
    setActiveView(view)
    if (view === "dashboard") {
      setResult(null)
      setError(null)
    }
  }, [])

  // ── Render ──────────────────────────────────────────────────
  return (
    <div className="flex h-screen overflow-hidden bg-[#0a0a0f]">
      {/* Sidebar */}
      <Sidebar
        activeView={activeView}
        onNavigate={handleNavigate}
        scanHistory={scanHistory}
        onSelectHistoryItem={handleSelectHistoryItem}
        onDeleteHistoryItem={handleDeleteHistoryItem}
      />

      {/* Main content */}
      <main className="dot-grid flex-1 overflow-y-auto">
        <div className="mx-auto max-w-5xl px-6 py-8 lg:px-10 lg:py-10">
          {activeView === "dashboard" ? (
            <div className="flex flex-col gap-10">
              {/* Hero */}
              <HeroSection />

              {/* Code Input */}
              <section aria-label="Code input">
                <CodeInputSection
                  code={code}
                  onChange={setCode}
                  onClear={handleClear}
                  disabled={loading}
                  filename={filename}
                  onFilenameChange={setFilename}
                />
              </section>

              {/* Capability Cards */}
              <section aria-label="Detection capabilities">
                <CapabilityCards />
              </section>

              {/* Scan Mode Selector */}
              <section aria-label="Scan mode selection">
                <ScanModeSelector
                  selectedMode={scanMode}
                  onModeChange={setScanMode}
                  onScan={handleScan}
                  loading={loading}
                  disabled={!code.trim()}
                />
              </section>

              {/* Error */}
              {error && (
                <div className="animate-slide-in-bottom flex items-start gap-3 rounded-xl border border-red-500/20 bg-red-500/[0.06] p-4">
                  <AlertTriangle className="mt-0.5 h-5 w-5 shrink-0 text-[#ff4444]" />
                  <div>
                    <p className="text-sm font-semibold text-red-300">Scan Error</p>
                    <p className="mt-1 text-sm text-slate-400">{error}</p>
                  </div>
                </div>
              )}

              {/* Footer */}
              <footer className="pb-4 text-center">
                <p className="text-[10px] text-slate-600">
                  SecureScope AI v2.0 &mdash; Multi-phase vulnerability analysis
                </p>
              </footer>
            </div>
          ) : (
            /* Results view */
            result && (
              <div className="flex flex-col gap-6">
                {/* Back button */}
                <button
                  onClick={() => handleNavigate("dashboard")}
                  className="flex w-fit items-center gap-2 rounded-xl px-4 py-2 text-sm font-medium text-slate-400 transition-all hover:bg-white/[0.04] hover:text-white"
                >
                  ← New Scan
                </button>

                {/* Results header */}
                <div className="flex items-center gap-4">
                  <h2 className="text-2xl font-bold text-white">Scan Results</h2>
                  <span className="rounded-full border border-[#00d5ff]/20 bg-[#00d5ff]/10 px-3 py-1 text-xs font-semibold text-[#00d5ff]">
                    {filename}
                  </span>
                </div>

                <ResultsView result={result} code={code} />
              </div>
            )
          )}
        </div>
      </main>
    </div>
  )
}
