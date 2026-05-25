"use client"

import { Loader2, Scan } from "lucide-react"

interface ScanButtonProps {
  onClick: () => void
  loading: boolean
  disabled: boolean
}

export function ScanButton({ onClick, loading, disabled }: ScanButtonProps) {
  return (
    <button
      onClick={onClick}
      disabled={disabled || loading}
      className="scan-gradient flex w-full items-center justify-center gap-2 rounded-lg px-6 py-3.5 text-sm font-bold text-primary-foreground transition-all hover:brightness-110 disabled:cursor-not-allowed disabled:opacity-50"
    >
      {loading ? (
        <>
          <Loader2 className="h-4 w-4 animate-spin" />
          Scanning...
        </>
      ) : (
        <>
          <Scan className="h-4 w-4" />
          Scan Code
        </>
      )}
    </button>
  )
}
