"use client"

import { Loader2, Search, Zap } from "lucide-react"

interface ScanButtonsProps {
  onQuickScan: () => void
  onDeepScan: () => void
  loading: boolean
  disabled: boolean
  loadingType?: "quick" | "deep"
}

export function ScanButtons({
  onQuickScan,
  onDeepScan,
  loading,
  disabled,
  loadingType = "quick",
}: ScanButtonsProps) {
  return (
    <div className="grid w-full grid-cols-1 gap-3 sm:grid-cols-2">
      <button
        onClick={onQuickScan}
        disabled={loading || disabled}
        className="group relative h-14 overflow-hidden rounded-xl border px-6 py-3 text-sm font-bold text-white transition-all duration-300 hover:scale-[1.03] disabled:cursor-not-allowed"
        style={{
          background: "linear-gradient(135deg, #6366f1 0%, #4f46e5 100%)",
          borderColor: "#818cf8",
          boxShadow:
            "0 0 22px rgba(99, 102, 241, 0.68), 0 0 48px rgba(99, 102, 241, 0.34), inset 0 1px 0 rgba(255, 255, 255, 0.24)",
        }}
      >
        <div
          className="absolute inset-0 opacity-0 transition-opacity duration-300 group-hover:opacity-100"
          style={{
            background:
              "radial-gradient(circle at center, rgba(165, 180, 252, 0.35), transparent 65%)",
            boxShadow:
              "inset 0 0 24px rgba(129, 140, 248, 0.45), 0 0 36px rgba(99, 102, 241, 0.58)",
          }}
        />
        <span className="relative flex items-center justify-center gap-2">
          {loading && loadingType === "quick" ? (
            <>
              <Loader2 className="h-4 w-4 animate-spin" />
              Scanning...
            </>
          ) : (
            <>
              <Zap className="h-4 w-4" />
              Quick Scan
            </>
          )}
        </span>
      </button>

      <button
        onClick={onDeepScan}
        disabled={loading || disabled}
        className="group relative h-14 overflow-hidden rounded-xl border px-6 py-3 text-sm font-bold text-white transition-all duration-300 hover:scale-[1.03] disabled:cursor-not-allowed"
        style={{
          background: "linear-gradient(135deg, #06b6d4 0%, #0891b2 100%)",
          borderColor: "#22d3ee",
          boxShadow:
            "0 0 22px rgba(6, 182, 212, 0.68), 0 0 48px rgba(6, 182, 212, 0.34), inset 0 1px 0 rgba(255, 255, 255, 0.24)",
        }}
      >
        <div
          className="absolute inset-0 opacity-0 transition-opacity duration-300 group-hover:opacity-100"
          style={{
            background:
              "radial-gradient(circle at center, rgba(103, 232, 249, 0.35), transparent 65%)",
            boxShadow:
              "inset 0 0 24px rgba(34, 211, 238, 0.45), 0 0 36px rgba(6, 182, 212, 0.58)",
          }}
        />
        <span className="relative flex items-center justify-center gap-2">
          {loading && loadingType === "deep" ? (
            <>
              <Loader2 className="h-4 w-4 animate-spin" />
              <span className="flex flex-col leading-tight">
                <span>Analyzing with AI...</span>
                <span className="text-[11px] font-medium opacity-75">
                  Deep analysis takes 10-30 seconds
                </span>
              </span>
            </>
          ) : (
            <>
              <Search className="h-4 w-4" />
              Deep Scan
            </>
          )}
        </span>
      </button>
    </div>
  )
}
