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
          <div className="w-full border-t border-primary/15" />
        </div>
        <div className="relative flex justify-center">
          <span className="bg-[#060a10] px-3 text-xs font-semibold uppercase tracking-wider text-primary neon-text">
            AI Security Analysis
          </span>
        </div>
      </div>

      <div className="premium-panel rounded-lg border-l-4 border-l-red-500 p-4">
        <div className="flex items-start gap-3">
          <AlertTriangle className="mt-0.5 h-5 w-5 flex-shrink-0 text-red-300 neon-text" />
          <div className="min-w-0 flex-1">
            <h3 className="mb-2 text-sm font-semibold text-red-300">
              What an attacker can do
            </h3>
            <p className="whitespace-pre-wrap break-words text-sm leading-relaxed text-slate-300">
              {danger}
            </p>
          </div>
        </div>
      </div>

      <div className="premium-panel rounded-lg border-l-4 border-l-cyan-400 p-4">
        <div className="mb-3 flex items-center justify-between gap-3">
          <div className="flex items-center gap-2">
            <CheckCircle2 className="h-5 w-5 flex-shrink-0 text-cyan-300 neon-text" />
            <h3 className="text-sm font-semibold text-cyan-300">
              Recommended Fix
            </h3>
          </div>
          {fix && (
            <button
              onClick={handleCopyCode}
              className="rounded border border-cyan-400/25 bg-cyan-400/10 px-2 py-1 text-xs font-semibold text-cyan-200 transition-smooth hover:bg-cyan-400/15"
            >
              {copied ? "Copied" : "Copy"}
            </button>
          )}
        </div>
        <div className="overflow-hidden rounded-lg border border-cyan-400/10 bg-[#05090f] shadow-inner">
          <pre className="overflow-x-auto whitespace-pre-wrap break-words p-4 font-mono text-xs leading-relaxed text-emerald-300">
            <code>{fix || "No fix was returned by the AI analysis."}</code>
          </pre>
        </div>
      </div>

      <div className="premium-panel rounded-lg border-l-4 border-l-fuchsia-500 p-4">
        <div className="flex items-start gap-3">
          <ExternalLink className="mt-0.5 h-5 w-5 flex-shrink-0 text-fuchsia-300 neon-text" />
          <div className="min-w-0 flex-1">
            <h3 className="mb-2 text-sm font-semibold text-fuchsia-300">
              OWASP Reference
            </h3>
            <p className="whitespace-pre-wrap break-words text-sm leading-relaxed text-slate-300">
              {owaspRef || "OWASP"}
            </p>
          </div>
        </div>
      </div>
    </section>
  )
}
