"use client"

import { ShieldCheck, ShieldAlert, Zap, ArrowRight } from "lucide-react"
import type { ScanResult } from "@/lib/types"
import { getRiskLevel, formatPercent, clampPercent } from "@/lib/types"

interface OverviewTabProps {
  result: ScanResult
  onTabChange?: (tab: string) => void
}

export function OverviewTab({ result, onTabChange }: OverviewTabProps) {
  const riskLevel = getRiskLevel(result)
  const score = clampPercent(result.confidence)
  const isVulnerable = result.is_vulnerable

  const gaugeColor = score >= 70 ? '#ff4444' : score >= 40 ? '#ff9a3d' : '#00ff88'
  const circumference = 2 * Math.PI * 45
  const offset = circumference - (circumference * score) / 100

  const hasCascade = result._mode === 'cascade' && 'phase1_confidence' in result
  const hasFeatures = ('features_fired' in result) && Array.isArray((result as any).features_fired) && (result as any).features_fired.length > 0

  return (
    <div className="animate-fade-scale-in">
      <div className="grid gap-6 md:grid-cols-[280px_1fr]">
        {/* Left: Gauge */}
        <div className="premium-panel flex flex-col items-center justify-center rounded-2xl p-6">
          <div className="relative">
            <svg width="200" height="200" viewBox="0 0 100 100">
              {/* Background circle */}
              <circle
                cx="50" cy="50" r="45"
                fill="none"
                stroke="rgba(255,255,255,0.06)"
                strokeWidth="8"
              />
              {/* Foreground arc */}
              <circle
                cx="50" cy="50" r="45"
                fill="none"
                stroke={gaugeColor}
                strokeWidth="8"
                strokeLinecap="round"
                strokeDasharray={circumference}
                strokeDashoffset={offset}
                transform="rotate(-90 50 50)"
                className="animate-gauge"
                style={{ filter: `drop-shadow(0 0 8px ${gaugeColor}80)` }}
              />
              {/* Center text */}
              <text x="50" y="46" textAnchor="middle" fill={gaugeColor} fontSize="20" fontWeight="bold" fontFamily="var(--font-sans)">
                {score.toFixed(0)}
              </text>
              <text x="50" y="60" textAnchor="middle" fill="#64748b" fontSize="7" fontWeight="600" fontFamily="var(--font-sans)">
                SECURITY RISK
              </text>
            </svg>
          </div>
          <div className="mt-2 text-center">
            <div className="text-lg font-bold" style={{ color: gaugeColor }}>{riskLevel}</div>
            <div className="text-xs text-slate-500">{isVulnerable ? 'Vulnerability Detected' : 'Code Appears Safe'}</div>
          </div>
        </div>

        {/* Right: Details */}
        <div className="flex flex-col gap-4">
          {/* Status card */}
          <div className="premium-panel rounded-xl p-5">
            <div className="flex items-start gap-4">
              {isVulnerable ? (
                <div className="rounded-xl bg-red-500/10 p-3">
                  <ShieldAlert className="h-6 w-6 text-[#ff4444]" style={{ filter: 'drop-shadow(0 0 6px rgba(255,68,68,0.5))' }} />
                </div>
              ) : (
                <div className="rounded-xl bg-emerald-500/10 p-3">
                  <ShieldCheck className="h-6 w-6 text-[#00ff88]" style={{ filter: 'drop-shadow(0 0 6px rgba(0,255,136,0.5))' }} />
                </div>
              )}
              <div>
                <h3 className="text-base font-bold text-white">
                  {isVulnerable ? 'Vulnerability Detected' : 'No Vulnerabilities Detected'}
                </h3>
                <p className="mt-1 text-sm text-slate-400">
                  {isVulnerable
                    ? `Analysis indicates potential security risks with ${formatPercent(result.confidence)} confidence.`
                    : `Code passed security analysis with ${formatPercent(result.confidence)} vulnerability confidence.`}
                </p>
              </div>
            </div>
          </div>

          {/* Link to Explanation tab for explain mode */}
          {result._mode === 'explain' && onTabChange && (
            <button
              onClick={() => onTabChange('explanation')}
              className="group flex w-full items-center justify-between rounded-xl border border-[#7c3aed]/20 bg-[#7c3aed]/[0.06] px-5 py-4 transition-all hover:border-[#7c3aed]/40 hover:bg-[#7c3aed]/10"
            >
              <div className="flex flex-col gap-1">
                <span className="text-sm font-bold text-[#a78bfa]">View Explanation & Fix</span>
                <span className="text-xs text-slate-500">See what an attacker can do, recommended fixes & OWASP references</span>
              </div>
              <ArrowRight className="h-5 w-5 text-[#7c3aed] transition-transform group-hover:translate-x-1" />
            </button>
          )}

          {/* Cascade breakdown */}
          {hasCascade && (
            <div className="premium-panel rounded-xl p-5">
              <h4 className="mb-4 text-sm font-semibold text-slate-300">Cascade Analysis</h4>
              <div className="space-y-3">
                {[
                  { label: 'Phase 1 Confidence', value: (result as any).phase1_confidence, color: '#00d5ff' },
                  { label: 'Phase 2 Confidence', value: (result as any).phase2_confidence, color: '#7c3aed' },
                  { label: 'Combined', value: result.confidence, color: '#ff3ea5' },
                ].map((item) => (
                  <div key={item.label}>
                    <div className="mb-1.5 flex items-center justify-between">
                      <span className="text-xs text-slate-500">{item.label}</span>
                      <span className="text-xs font-semibold text-slate-200">{formatPercent(item.value)}</span>
                    </div>
                    <div className="meter-track h-2 overflow-hidden rounded-full">
                      <div
                        className="animate-fill-bar h-full rounded-full"
                        style={{
                          width: `${clampPercent(item.value)}%`,
                          background: item.color,
                          boxShadow: `0 0 10px ${item.color}50`,
                        }}
                      />
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Features fired */}
          {hasFeatures && (
            <div className="premium-panel rounded-xl p-5">
              <div className="mb-3 flex items-center gap-2">
                <Zap className="h-4 w-4 text-[#00d5ff]" style={{ filter: 'drop-shadow(0 0 6px rgba(0,213,255,0.5))' }} />
                <span className="text-sm font-semibold text-slate-300">AST Features Detected</span>
                <span className="rounded-full bg-[#00d5ff]/10 px-2 py-0.5 text-[10px] font-bold text-[#00d5ff]">
                  AST-POWERED
                </span>
              </div>
              <div className="flex flex-wrap gap-2">
                {((result as any).features_fired as string[]).map((feature: string, i: number) => (
                  <span
                    key={feature}
                    className="animate-fade-scale-in rounded-full border border-[#00d5ff]/20 bg-[#00d5ff]/8 px-3 py-1.5 text-xs font-semibold text-[#00d5ff]"
                    style={{ animationDelay: `${i * 50}ms`, animationFillMode: 'both' }}
                  >
                    {feature}
                  </span>
                ))}
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}
