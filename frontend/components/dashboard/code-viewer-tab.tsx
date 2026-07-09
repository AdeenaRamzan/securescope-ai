"use client"

import { useState } from "react"
import { Copy, Check } from "lucide-react"
import { Prism as SyntaxHighlighter } from 'react-syntax-highlighter'
import { vscDarkPlus } from 'react-syntax-highlighter/dist/esm/styles/prism'

interface CodeViewerTabProps {
  code: string
}

export function CodeViewerTab({ code }: CodeViewerTabProps) {
  const [copied, setCopied] = useState(false)

  const handleCopy = async () => {
    await navigator.clipboard.writeText(code)
    setCopied(true)
    setTimeout(() => setCopied(false), 2000)
  }

  if (!code) {
    return (
      <div className="animate-fade-scale-in flex flex-col items-center gap-3 py-12 text-center">
        <p className="text-sm text-slate-500">No code submitted</p>
      </div>
    )
  }

  return (
    <div className="animate-fade-scale-in">
      <div className="mb-3 flex items-center justify-between">
        <span className="text-sm font-semibold text-slate-300">Submitted Code</span>
        <button
          onClick={handleCopy}
          className="glass-sm flex items-center gap-1.5 rounded-lg px-3 py-1.5 text-xs font-medium text-slate-400 transition-all hover:text-[#00d5ff]"
        >
          {copied ? <Check className="h-3.5 w-3.5" /> : <Copy className="h-3.5 w-3.5" />}
          {copied ? 'Copied!' : 'Copy Code'}
        </button>
      </div>
      <SyntaxHighlighter
        language="python"
        style={vscDarkPlus}
        showLineNumbers
        wrapLines
        customStyle={{
          background: '#0a0d14',
          padding: '1.5rem',
          margin: 0,
          borderRadius: '12px',
          fontSize: '13px',
          lineHeight: '1.6',
          border: '1px solid rgba(255,255,255,0.06)',
        }}
        lineNumberStyle={{ color: '#374151', paddingRight: '1em' }}
      >
        {code}
      </SyntaxHighlighter>
    </div>
  )
}
