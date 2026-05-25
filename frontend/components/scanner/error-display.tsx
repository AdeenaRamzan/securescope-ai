"use client"

import { AlertTriangle } from "lucide-react"

interface ErrorDisplayProps {
  message: string
}

export function ErrorDisplay({ message }: ErrorDisplayProps) {
  return (
    <div className="glow-red flex items-start gap-3 rounded-lg border border-red-500/30 bg-red-500/5 p-4">
      <AlertTriangle className="mt-0.5 h-5 w-5 shrink-0 text-red-400" />
      <div className="flex flex-col gap-1">
        <p className="text-sm font-medium text-red-400">Scan Failed</p>
        <p className="text-sm text-red-400/70">{message}</p>
      </div>
    </div>
  )
}
