"use client"

import { Shield } from "lucide-react"

const badges = [
  "ANN + XGBoost + LightGBM",
  "22 Features",
  "Real-time",
]

export function ScannerHeader() {
  return (
    <header className="flex flex-col items-center gap-4 text-center">
      <div className="relative">
        <Shield className="h-12 w-12 text-primary" />
        <div className="absolute inset-0 h-12 w-12 rounded-full blur-xl bg-primary/20" aria-hidden="true" />
      </div>

      <div className="flex flex-col items-center gap-2">
        <h1 className="text-3xl font-bold tracking-tight text-foreground">
          SecureScope AI
        </h1>
        <p className="text-muted-foreground text-sm">
          AI-Powered Python Vulnerability Scanner
        </p>
      </div>

      <div className="flex flex-wrap items-center justify-center gap-2">
        {badges.map((badge) => (
          <span
            key={badge}
            className="rounded-full border border-border bg-muted/50 px-3 py-1 text-xs text-muted-foreground"
          >
            {badge}
          </span>
        ))}
      </div>
    </header>
  )
}
