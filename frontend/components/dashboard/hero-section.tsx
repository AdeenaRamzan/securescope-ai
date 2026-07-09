"use client"

import { Lock } from "lucide-react"

export function HeroSection() {
  return (
    <section className="flex flex-col items-center gap-5 text-center">
      {/* Top badge */}
      <div
        className="rounded-full border border-[#00d5ff]/25 bg-[#00d5ff]/[0.07] px-5 py-2 text-xs font-bold uppercase tracking-widest text-[#00d5ff]"
        style={{ boxShadow: '0 0 20px rgba(0,213,255,0.1), 0 0 40px rgba(0,213,255,0.05)' }}
      >
        AI-Powered · 3-Phase Analysis Engine
      </div>

      {/* Hero heading */}
      <div className="flex flex-col gap-2">
        <h1 className="text-4xl font-bold tracking-tight text-white md:text-5xl lg:text-6xl">
          Detect Vulnerabilities
        </h1>
        <h2
          className="text-4xl font-bold tracking-tight md:text-5xl lg:text-6xl"
          style={{
            background: 'linear-gradient(135deg, #00d5ff 0%, #7c3aed 50%, #ff3ea5 100%)',
            WebkitBackgroundClip: 'text',
            WebkitTextFillColor: 'transparent',
          }}
        >
          Before They Strike
        </h2>
      </div>

      {/* Subtitle */}
      <p className="mx-auto max-w-2xl text-base leading-relaxed text-slate-400 md:text-lg">
        Advanced AI-powered code analysis combining ensemble ML, BiLSTM sequence models,
        and CodeBERT with RAG for comprehensive Python vulnerability detection.
      </p>

      {/* Tech badges */}
      <div className="flex flex-wrap items-center justify-center gap-2">
        {[
          { label: "CodeBERT", color: "#00d5ff" },
          { label: "RAG", color: "#7c3aed" },
          { label: "BiLSTM", color: "#ff3ea5" },
          { label: "Ensemble ML", color: "#00d5ff" },
        ].map((badge) => (
          <span
            key={badge.label}
            className="rounded-full border px-3 py-1.5 text-xs font-semibold"
            style={{
              borderColor: `${badge.color}40`,
              color: badge.color,
              background: `${badge.color}12`,
              boxShadow: `0 0 12px ${badge.color}30`,
            }}
          >
            {badge.label}
          </span>
        ))}
      </div>

      {/* Trust line */}
      <div className="flex items-center gap-1.5 text-xs text-slate-500">
        <Lock className="h-3.5 w-3.5" />
        <span>Isolated analysis via secure API</span>
      </div>
    </section>
  )
}
