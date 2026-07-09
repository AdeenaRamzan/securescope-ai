"use client"

import { useState } from "react"
import {
  Shield, Clock, Cpu, AlertTriangle, Activity, BarChart3, FileCode, MessageSquare,
} from "lucide-react"
import type { ScanResult } from "@/lib/types"
import { getRiskLevel, formatPercent, formatVulnType } from "@/lib/types"
import { OverviewTab } from "./overview-tab"
import { ModelBreakdownTab } from "./model-breakdown-tab"
import { ExplanationTab } from "./explanation-tab"
import { CodeViewerTab } from "./code-viewer-tab"

interface ResultsViewProps {
  result: ScanResult
  code: string
}

const riskColors: Record<string, string> = {
  HIGH: "#ff4444",
  MEDIUM: "#ff9a3d",
  LOW: "#ffcc00",
  SAFE: "#00ff88",
  INCONCLUSIVE: "#748194",
}

type Tab = "overview" | "breakdown" | "explanation" | "code"

const tabs: { id: Tab; label: string; icon: typeof Shield }[] = [
  { id: "overview", label: "Overview", icon: Shield },
  { id: "breakdown", label: "Model Breakdown", icon: BarChart3 },
  { id: "explanation", label: "Explanation", icon: MessageSquare },
  { id: "code", label: "Code Viewer", icon: FileCode },
]

export function ResultsView({ result, code }: ResultsViewProps) {
  const [activeTab, setActiveTab] = useState<Tab>("overview")
  const riskLevel = getRiskLevel(result)
  const riskColor = riskColors[riskLevel] ?? "#748194"

  const statCards = [
    {
      label: "Risk Level",
      value: riskLevel,
      icon: Shield,
      color: riskColor,
    },
    {
      label: "Confidence",
      value: formatPercent(result.confidence),
      icon: Activity,
      color: "#00d5ff",
    },
    {
      label: "Scan Time",
      value: 'scan_time_ms' in result ? `${(result as any).scan_time_ms?.toFixed(0) ?? '—'}ms` : 'N/A',
      icon: Clock,
      color: "#7c3aed",
    },
    {
      label: result._mode === "explain" ? "Pipeline" : "Model",
      value:
        result._mode === "explain"
          ? result.pipeline?.replace(/_/g, " ") ?? "N/A"
          : ('model_version' in result ? (result as any).model_version : result._mode) ?? result._mode,
      icon: Cpu,
      color: "#ff3ea5",
    },
    ...(result._mode === "explain"
      ? [
          {
            label: "Vuln Type",
            value: formatVulnType(result.vulnerability_type),
            icon: AlertTriangle,
            color: "#ff9a3d",
          },
        ]
      : []),
  ]

  return (
    <div className="animate-slide-in-bottom flex flex-col gap-6">
      {/* Stat cards */}
      <div className={`grid gap-3 ${result._mode === 'explain' ? 'grid-cols-2 md:grid-cols-3 lg:grid-cols-5' : 'grid-cols-2 md:grid-cols-4'}`}>
        {statCards.map((stat) => {
          const Icon = stat.icon
          return (
            <div key={stat.label} className="stat-card p-4">
              <div className="mb-2 flex items-center gap-2">
                <Icon className="h-4 w-4" style={{ color: `${stat.color}80` }} />
                <span className="text-[10px] font-semibold uppercase tracking-wider text-slate-500">
                  {stat.label}
                </span>
              </div>
              <div
                className="truncate text-xl font-bold"
                style={{ color: stat.label === "Risk Level" ? stat.color : "#fff" }}
              >
                {stat.value}
              </div>
            </div>
          )
        })}
      </div>

      {/* Tab navigation */}
      <div className="flex gap-1 border-b border-white/[0.06]">
        {tabs.map((tab) => {
          const Icon = tab.icon
          const isActive = activeTab === tab.id
          return (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id)}
              className={`flex items-center gap-2 px-4 py-3 text-sm font-medium transition-all ${
                isActive
                  ? "text-[#00d5ff] tab-active"
                  : "text-slate-500 hover:text-slate-300"
              }`}
            >
              <Icon className="h-4 w-4" />
              <span className="hidden sm:inline">{tab.label}</span>
            </button>
          )
        })}
      </div>

      {/* Tab content */}
      <div>
        {activeTab === "overview" && <OverviewTab result={result} onTabChange={(t) => setActiveTab(t as Tab)} />}
        {activeTab === "breakdown" && <ModelBreakdownTab result={result} />}
        {activeTab === "explanation" && <ExplanationTab result={result} />}
        {activeTab === "code" && <CodeViewerTab code={code} />}
      </div>
    </div>
  )
}
