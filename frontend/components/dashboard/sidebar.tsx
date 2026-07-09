"use client"

import { useState } from "react"
import {
  Shield, LayoutDashboard, Plus, Trash2, Menu, X, History,
} from "lucide-react"
import type { ScanHistoryItem, RiskLevel } from "@/lib/types"
import { timeAgo } from "@/lib/types"

interface SidebarProps {
  activeView: "dashboard" | "results"
  onNavigate: (view: "dashboard" | "results") => void
  scanHistory: ScanHistoryItem[]
  onSelectHistoryItem: (item: ScanHistoryItem) => void
  onDeleteHistoryItem: (id: string) => void
}

const riskClass: Record<RiskLevel, string> = {
  HIGH: "risk-high",
  MEDIUM: "risk-medium",
  LOW: "risk-low",
  SAFE: "risk-safe",
  INCONCLUSIVE: "risk-inconclusive",
}

export function Sidebar({
  activeView,
  onNavigate,
  scanHistory,
  onSelectHistoryItem,
  onDeleteHistoryItem,
}: SidebarProps) {
  const [mobileOpen, setMobileOpen] = useState(false)

  const navItems = [
    { id: "dashboard" as const, label: "Dashboard", icon: LayoutDashboard },
    { id: "dashboard" as const, label: "New Scan", icon: Plus },
  ]

  const sidebarContent = (
    <div className="flex h-full flex-col">
      {/* Logo */}
      <div className="flex items-center gap-3 px-5 py-6">
        <div className="relative">
          <div className="absolute inset-0 animate-pulse rounded-full bg-[#00d5ff]/20 blur-xl" />
          <Shield className="relative h-8 w-8 text-[#00d5ff] drop-shadow-[0_0_12px_rgba(0,213,255,0.5)]" />
        </div>
        <div className="flex items-baseline gap-1">
          <span className="text-lg font-bold text-white">SecureScope</span>
          <span className="bg-gradient-to-r from-[#00d5ff] to-[#7c3aed] bg-clip-text text-lg font-bold text-transparent">
            AI
          </span>
        </div>
        <span className="ml-auto rounded-md bg-[#00d5ff]/10 px-1.5 py-0.5 text-[9px] font-bold text-[#00d5ff]">v2.0</span>
      </div>

      <div className="mx-4 mb-4 h-px bg-gradient-to-r from-transparent via-[#00d5ff]/20 to-transparent" />

      {/* Navigation */}
      <nav className="flex flex-col gap-1 px-3">
        {navItems.map((item, i) => {
          const Icon = item.icon
          const isActive = i === 0 && activeView === "dashboard"
          return (
            <button
              key={`${item.label}-${i}`}
              onClick={() => { onNavigate(item.id); setMobileOpen(false) }}
              className={`sidebar-item flex items-center gap-3 rounded-xl px-3 py-2.5 text-sm font-medium ${
                isActive ? "active text-[#00d5ff]" : "text-slate-400 hover:text-slate-200"
              }`}
            >
              <Icon className="h-4 w-4" />
              {item.label}
            </button>
          )
        })}
      </nav>

      <div className="mx-4 my-4 h-px bg-white/[0.06]" />

      {/* Scan History */}
      <div className="flex-1 overflow-hidden px-3">
        <div className="mb-3 flex items-center justify-between px-1">
          <div className="flex items-center gap-2">
            <History className="h-4 w-4 text-slate-500" />
            <span className="text-xs font-semibold uppercase tracking-wider text-slate-500">Scan History</span>
          </div>
          {scanHistory.length > 0 && (
            <span className="rounded-full bg-[#00d5ff]/10 px-2 py-0.5 text-[10px] font-bold text-[#00d5ff]">
              {scanHistory.length}
            </span>
          )}
        </div>

        <div className="custom-scrollbar flex max-h-[calc(100vh-340px)] flex-col gap-1 overflow-y-auto">
          {scanHistory.length === 0 ? (
            <div className="flex flex-col items-center gap-2 py-8 text-center">
              <Shield className="h-8 w-8 text-slate-700" />
              <p className="text-xs text-slate-600">No scans yet</p>
            </div>
          ) : (
            scanHistory.map((item) => (
              <div
                key={item.id}
                className="group flex cursor-pointer items-center gap-3 rounded-xl px-3 py-2.5 transition-all hover:bg-white/[0.04]"
                onClick={() => { onSelectHistoryItem(item); setMobileOpen(false) }}
              >
                <div className="min-w-0 flex-1">
                  <p className="truncate text-sm font-medium text-slate-300">{item.filename}</p>
                  <p className="text-[11px] text-slate-600">{timeAgo(item.timestamp)}</p>
                </div>
                {item.riskLevel && (
                  <span className={`${riskClass[item.riskLevel]} shrink-0 rounded-md px-2 py-0.5 text-[10px] font-bold`}>
                    {item.riskLevel}
                  </span>
                )}
                <button
                  onClick={(e) => { e.stopPropagation(); onDeleteHistoryItem(item.id) }}
                  className="shrink-0 rounded-lg p-1 text-slate-600 opacity-0 transition-all hover:bg-red-500/10 hover:text-red-400 group-hover:opacity-100"
                >
                  <Trash2 className="h-3.5 w-3.5" />
                </button>
              </div>
            ))
          )}
        </div>
      </div>

      {/* Bottom */}
      <div className="mt-auto px-5 pb-5">
        <div className="mb-3 h-px bg-gradient-to-r from-transparent via-white/[0.06] to-transparent" />
        <p className="text-center text-[10px] text-slate-600">
          Built by <span className="text-[#00d5ff]/60">Adeena Ramzan</span>
        </p>
      </div>
    </div>
  )

  return (
    <>
      {/* Mobile toggle */}
      <button
        onClick={() => setMobileOpen(!mobileOpen)}
        className="fixed left-4 top-4 z-50 rounded-xl bg-[#10131a] p-2.5 text-slate-400 shadow-lg lg:hidden"
        style={{ border: '1px solid rgba(255,255,255,0.08)' }}
      >
        {mobileOpen ? <X className="h-5 w-5" /> : <Menu className="h-5 w-5" />}
      </button>

      {/* Mobile overlay */}
      {mobileOpen && (
        <div
          className="fixed inset-0 z-40 bg-black/60 backdrop-blur-sm lg:hidden"
          onClick={() => setMobileOpen(false)}
        />
      )}

      {/* Sidebar */}
      <aside
        className={`sidebar-nav fixed left-0 top-0 z-40 h-full min-h-screen w-[280px] transform transition-transform duration-300 lg:sticky lg:top-0 lg:translate-x-0 lg:self-stretch ${
          mobileOpen ? "translate-x-0" : "-translate-x-full"
        }`}
      >
        {sidebarContent}
      </aside>
    </>
  )
}
