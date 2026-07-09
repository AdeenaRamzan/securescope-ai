"use client"

import { useState } from "react"
import { AlertTriangle, CheckCircle2, ExternalLink, Microscope, Copy, Check } from "lucide-react"
import type { ScanResult } from "@/lib/types"
import { formatVulnType } from "@/lib/types"
import { Prism as SyntaxHighlighter } from 'react-syntax-highlighter'
import { vscDarkPlus } from 'react-syntax-highlighter/dist/esm/styles/prism'

interface ExplanationTabProps {
  result: ScanResult
}

export function ExplanationTab({ result }: ExplanationTabProps) {
  const [copied, setCopied] = useState(false)

  const isExplain = result._mode === 'explain'
  const hasData = isExplain && (result.danger || result.fix || result.owasp_ref)

  const handleCopy = async () => {
    if (isExplain && result.fix) {
      await navigator.clipboard.writeText(result.fix)
      setCopied(true)
      setTimeout(() => setCopied(false), 2000)
    }
  }

  if (!hasData) {
    return (
      <div className="animate-fade-scale-in">
        <div className="premium-panel flex flex-col items-center gap-5 rounded-2xl p-10 text-center">
          <div className="rounded-2xl bg-slate-800/50 p-5">
            <Microscope className="h-16 w-16 text-slate-600" />
          </div>
          <h3 className="text-lg font-bold text-slate-300">AI Explanation Not Available</h3>
          <p className="max-w-md text-sm leading-relaxed text-slate-500">
            Run a <span className="font-semibold text-[#ff3ea5]">Full Explain</span> scan to get CodeBERT + RAG powered
            security analysis with vulnerability details, recommended fixes, and OWASP references.
          </p>
          <div className="flex gap-2">
            {['CodeBERT Analysis', 'RAG Context', 'LLM Fixes'].map((label) => (
              <span key={label} className="rounded-full border border-[#7c3aed]/25 bg-[#7c3aed]/10 px-3 py-1.5 text-xs font-semibold text-[#a78bfa]">
                {label}
              </span>
            ))}
          </div>
        </div>
      </div>
    )
  }

  const phase3 = result as Extract<ScanResult, { _mode: 'explain' }>

  return (
    <div className="animate-fade-scale-in flex flex-col gap-4">
      {/* DANGER card */}
      {phase3.danger && (
        <div className="danger-card rounded-xl p-5">
          <div className="mb-3 flex items-start justify-between">
            <div className="flex items-center gap-2">
              <AlertTriangle className="h-5 w-5 text-[#ff4444]" style={{ filter: 'drop-shadow(0 0 6px rgba(255,68,68,0.5))' }} />
              <span className="text-sm font-bold text-[#ff6b6b]">What an attacker can do</span>
            </div>
            {phase3.vulnerability_type && (
              <span className="rounded-md bg-red-500/15 px-2 py-0.5 text-[10px] font-bold text-red-400">
                {formatVulnType(phase3.vulnerability_type)}
              </span>
            )}
          </div>
          <p className="whitespace-pre-wrap text-sm leading-relaxed text-slate-300">
            {phase3.danger}
          </p>
        </div>
      )}

      {/* FIX card */}
      {phase3.fix && (
        <div className="fix-card rounded-xl p-5">
          <div className="mb-3 flex items-center justify-between">
            <div className="flex items-center gap-2">
              <CheckCircle2 className="h-5 w-5 text-[#00d5ff]" style={{ filter: 'drop-shadow(0 0 6px rgba(0,213,255,0.5))' }} />
              <span className="text-sm font-bold text-[#67e8f9]">Recommended Fix</span>
            </div>
            <button
              onClick={handleCopy}
              className="flex items-center gap-1.5 rounded-lg border border-[#00d5ff]/20 bg-[#00d5ff]/10 px-3 py-1.5 text-xs font-semibold text-[#00d5ff] transition-all hover:bg-[#00d5ff]/15"
            >
              {copied ? <Check className="h-3.5 w-3.5" /> : <Copy className="h-3.5 w-3.5" />}
              {copied ? 'Copied!' : 'Copy'}
            </button>
          </div>
          <div className="overflow-hidden rounded-lg border border-white/[0.06]" style={{ background: '#0a0d14' }}>
            <SyntaxHighlighter
              language="python"
              style={vscDarkPlus}
              showLineNumbers
              customStyle={{ background: 'transparent', padding: '1rem', margin: 0, fontSize: '13px' }}
              lineNumberStyle={{ color: '#374151', paddingRight: '1em' }}
            >
              {phase3.fix}
            </SyntaxHighlighter>
          </div>
        </div>
      )}

      {/* REF card */}
      {phase3.owasp_ref && (
        <div className="ref-card rounded-xl p-5">
          <div className="mb-3 flex items-center gap-2">
            <ExternalLink className="h-5 w-5 text-[#7c3aed]" style={{ filter: 'drop-shadow(0 0 6px rgba(124,58,237,0.5))' }} />
            <span className="text-sm font-bold text-[#a78bfa]">OWASP Reference</span>
          </div>
          <a
            href={getOwaspUrl(phase3.vulnerability_type, phase3.owasp_ref)}
            target="_blank"
            rel="noopener noreferrer"
            className="group flex items-center gap-2 text-sm leading-relaxed text-[#a78bfa] underline decoration-[#7c3aed]/30 underline-offset-4 transition-all hover:text-[#c4b5fd] hover:decoration-[#7c3aed]/60"
          >
            {phase3.owasp_ref}
            <ExternalLink className="h-3.5 w-3.5 shrink-0 opacity-50 transition-opacity group-hover:opacity-100" />
          </a>
        </div>
      )}
    </div>
  )
}

const OWASP_URLS: Record<string, string> = {
  // Map by vulnerability type key
  sql_injection: "https://cheatsheetseries.owasp.org/cheatsheets/SQL_Injection_Prevention_Cheat_Sheet.html",
  cmd_injection: "https://cheatsheetseries.owasp.org/cheatsheets/OS_Command_Injection_Defense_Cheat_Sheet.html",
  command_injection: "https://cheatsheetseries.owasp.org/cheatsheets/OS_Command_Injection_Defense_Cheat_Sheet.html",
  insecure_eval: "https://cheatsheetseries.owasp.org/cheatsheets/Injection_Prevention_Cheat_Sheet.html",
  path_traversal: "https://cheatsheetseries.owasp.org/cheatsheets/Input_Validation_Cheat_Sheet.html",
  hardcoded_secret: "https://cheatsheetseries.owasp.org/cheatsheets/Secrets_Management_Cheat_Sheet.html",
}

// Direct URL map based on the reference title/text
const REF_URLS: Record<string, string> = {
  "sql injection prevention cheat sheet": "https://cheatsheetseries.owasp.org/cheatsheets/SQL_Injection_Prevention_Cheat_Sheet.html",
  "os command injection defense cheat sheet": "https://cheatsheetseries.owasp.org/cheatsheets/OS_Command_Injection_Defense_Cheat_Sheet.html",
  "injection prevention cheat sheet": "https://cheatsheetseries.owasp.org/cheatsheets/Injection_Prevention_Cheat_Sheet.html",
  "input validation cheat sheet": "https://cheatsheetseries.owasp.org/cheatsheets/Input_Validation_Cheat_Sheet.html",
  "secrets management cheat sheet": "https://cheatsheetseries.owasp.org/cheatsheets/Secrets_Management_Cheat_Sheet.html",
}

function getOwaspUrl(vulnType: string, owaspRef: string): string {
  const refLower = owaspRef?.toLowerCase().trim() || ""
  
  // 1. Direct match on reference name
  if (REF_URLS[refLower]) {
    return REF_URLS[refLower]
  }

  // 2. Match Secure Coding Practices project page
  if (refLower.includes("secure coding practices") || refLower.includes("secure_coding_practices")) {
    return "https://owasp.org/www-project-secure-coding-practices-quick-reference-guide/"
  }

  // 3. Match by vulnerability type key
  const typeKey = vulnType?.toLowerCase().replace(/\s+/g, "_")
  if (typeKey && OWASP_URLS[typeKey]) {
    return OWASP_URLS[typeKey]
  }

  // 4. Fallback build
  const slug = owaspRef.replace(/\s+/g, "_")
  return `https://cheatsheetseries.owasp.org/cheatsheets/${slug}.html`
}
