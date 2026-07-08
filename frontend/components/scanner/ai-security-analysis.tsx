"use client"

import { useState } from "react"
import { AlertTriangle, CheckCircle2, ExternalLink } from "lucide-react"

interface AiSecurityAnalysisProps {
  danger: string
  fix: string
  owaspRef: string
}

export function AiSecurityAnalysis({
  danger,
  fix,
  owaspRef,
}: AiSecurityAnalysisProps) {
  const [copied, setCopied] = useState(false)

  const handleCopyCode = async () => {
    await navigator.clipboard.writeText(fix)
    setCopied(true)
    window.setTimeout(() => setCopied(false), 2000)
  }

  return (
    <section className="mt-6 flex flex-col gap-4 animate-slide-in-bottom">
      <div className="relative py-3">
        <div className="absolute inset-0 flex items-center">
          <div className="w-full border-t border-border/40" />
        </div>
        <div className="relative flex justify-center">
          <span className="bg-background px-3 text-xs font-semibold uppercase tracking-wider text-primary">
            AI Security Analysis
          </span>
        </div>
      </div>

      <div className="glass rounded-lg border-l-4 border-l-red-500 p-4">
        <div className="flex items-start gap-3">
          <AlertTriangle className="mt-0.5 h-5 w-5 flex-shrink-0 text-red-400" />
          <div className="min-w-0 flex-1">
            <h3 className="mb-2 text-sm font-semibold text-red-400">
              What an attacker can do
            </h3>
            <p className="whitespace-pre-wrap break-words text-sm leading-relaxed text-foreground/75">
              {danger}
            </p>
          </div>
        </div>
      </div>

      <div className="glass rounded-lg border-l-4 border-l-teal-500 p-4">
        <div className="mb-3 flex items-center justify-between gap-3">
          <div className="flex items-center gap-2">
            <CheckCircle2 className="h-5 w-5 flex-shrink-0 text-teal-400" />
            <h3 className="text-sm font-semibold text-teal-400">
              Recommended Fix
            </h3>
          </div>
          {fix && (
            <button
              onClick={handleCopyCode}
              className="rounded border border-teal-500/30 bg-teal-500/10 px-2 py-1 text-xs text-teal-300 transition-smooth hover:bg-teal-500/20"
            >
              {copied ? "Copied" : "Copy"}
            </button>
          )}
        </div>
        <div className="overflow-hidden rounded-lg border border-border/50 bg-[#1a2133]">
          <pre className="overflow-x-auto whitespace-pre-wrap break-words p-4 font-mono text-xs leading-relaxed text-green-300">
            <code>{fix || "No fix was returned by the AI analysis."}</code>
          </pre>
        </div>
      </div>

      <div className="glass rounded-lg border-l-4 border-l-purple-500 p-4">
        <div className="flex items-start gap-3">
          <ExternalLink className="mt-0.5 h-5 w-5 flex-shrink-0 text-purple-400" />
          <div className="min-w-0 flex-1">
            <h3 className="mb-2 text-sm font-semibold text-purple-400">
              OWASP Reference
            </h3>
            <p className="whitespace-pre-wrap break-words text-sm leading-relaxed text-foreground/75">
              {owaspRef || "OWASP"}
            </p>
          </div>
        </div>
      </div>
    </section>
  )
}
