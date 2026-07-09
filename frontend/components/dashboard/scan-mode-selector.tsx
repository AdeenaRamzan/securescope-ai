"use client"

import { Zap, Brain, Link, Microscope, Loader2, Play } from "lucide-react"
import type { ScanMode } from "@/lib/types"
import { SCAN_MODE_META } from "@/lib/types"

interface ScanModeSelectorProps {
  selectedMode: ScanMode
  onModeChange: (mode: ScanMode) => void
  onScan: () => void
  loading: boolean
  disabled: boolean
}

const modeIcons: Record<ScanMode, typeof Zap> = {
  quick: Zap,
  bilstm: Brain,
  cascade: Link,
  explain: Microscope,
}

const modeColors: Record<ScanMode, string> = {
  quick: "#00d5ff",
  bilstm: "#7c3aed",
  cascade: "#ff9a3d",
  explain: "#ff3ea5",
}

const modes: ScanMode[] = ["quick", "bilstm", "cascade", "explain"]

export function ScanModeSelector({
  selectedMode,
  onModeChange,
  onScan,
  loading,
  disabled,
}: ScanModeSelectorProps) {
  const color = modeColors[selectedMode]

  return (
    <div className="flex flex-col gap-4">
      {/* Header */}
      <div className="flex items-center gap-3">
        <span className="text-xs font-semibold uppercase tracking-widest text-slate-500">
          Select Analysis Mode
        </span>
        <div className="h-px flex-1 bg-gradient-to-r from-white/[0.06] to-transparent" />
      </div>

      {/* Mode grid */}
      <div className="grid grid-cols-2 gap-3 lg:grid-cols-4">
        {modes.map((mode) => {
          const Icon = modeIcons[mode]
          const meta = SCAN_MODE_META[mode]
          const isActive = selectedMode === mode
          const c = modeColors[mode]

          return (
            <button
              key={mode}
              onClick={() => onModeChange(mode)}
              className={`mode-btn px-4 py-4 text-left ${isActive ? "active" : ""}`}
              style={
                isActive
                  ? {
                      borderColor: `${c}60`,
                      boxShadow: `0 0 25px ${c}18, inset 0 1px 0 rgba(255,255,255,0.05)`,
                    }
                  : undefined
              }
            >
              <Icon
                className="mb-2 h-5 w-5"
                style={{
                  color: isActive ? c : `${c}90`,
                  filter: isActive ? `drop-shadow(0 0 8px ${c}80)` : 'none',
                }}
              />
              <div className="mb-1 text-sm font-semibold" style={{ color: isActive ? '#fff' : '#cbd5e1' }}>
                {meta.label}
              </div>
              <div className="mb-1.5">
                <span
                  className="rounded-md px-1.5 py-0.5 text-[9px] font-bold uppercase tracking-wider"
                  style={{
                    background: `${c}18`,
                    color: `${c}cc`,
                  }}
                >
                  {meta.phase}
                </span>
              </div>
              <div className="text-[11px] leading-snug text-slate-500">{meta.caption}</div>
            </button>
          )
        })}
      </div>

      {/* Scan button */}
      <button
        onClick={onScan}
        disabled={loading || disabled}
        className="group relative flex h-14 w-full items-center justify-center gap-2.5 overflow-hidden rounded-xl text-sm font-bold text-white transition-all duration-300 hover:scale-[1.02] disabled:cursor-not-allowed disabled:opacity-60"
        style={{
          background: `linear-gradient(135deg, ${color}, ${color}99)`,
          boxShadow: `0 0 30px ${color}50, 0 0 60px ${color}20, inset 0 1px 0 rgba(255,255,255,0.2)`,
        }}
      >
        <div
          className="absolute inset-0 opacity-0 transition-opacity duration-300 group-hover:opacity-100"
          style={{
            background: `radial-gradient(circle at center, ${color}40, transparent 70%)`,
          }}
        />
        <span className="relative flex items-center gap-2.5">
          {loading ? (
            <>
              <Loader2 className="h-5 w-5 animate-spin" />
              <span>Analyzing...</span>
              {selectedMode === "explain" && (
                <span className="text-xs font-normal opacity-70">(may take 10-30s)</span>
              )}
            </>
          ) : (
            <>
              <Play className="h-5 w-5" />
              Run {SCAN_MODE_META[selectedMode].label}
            </>
          )}
        </span>
      </button>
    </div>
  )
}
