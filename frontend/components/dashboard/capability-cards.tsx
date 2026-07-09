"use client"

import { Database, Key, Terminal, Code, FolderSearch } from "lucide-react"

const capabilities = [
  { icon: Database, name: "SQL Injection", desc: "Detect unsafe query construction", color: "#ff4444" },
  { icon: Key, name: "Hardcoded Secrets", desc: "Find exposed credentials & keys", color: "#ff9a3d" },
  { icon: Terminal, name: "eval/exec", desc: "Flag dangerous code execution", color: "#ffcc00" },
  { icon: Code, name: "Command Injection", desc: "Identify OS command risks", color: "#00d5ff" },
  { icon: FolderSearch, name: "Path Traversal", desc: "Detect directory escape attacks", color: "#7c3aed" },
]

export function CapabilityCards() {
  return (
    <div className="grid grid-cols-2 gap-3 sm:grid-cols-3 lg:grid-cols-5">
      {capabilities.map((cap) => {
        const Icon = cap.icon
        return (
          <div key={cap.name} className="capability-card flex flex-col items-center gap-2.5 p-4 text-center">
            <div
              className="flex h-10 w-10 items-center justify-center rounded-xl"
              style={{
                background: `${cap.color}15`,
                border: `1px solid ${cap.color}30`,
              }}
            >
              <Icon className="h-5 w-5" style={{ color: cap.color }} />
            </div>
            <span className="text-sm font-semibold text-slate-200">{cap.name}</span>
            <span className="text-[11px] leading-tight text-slate-500">{cap.desc}</span>
            <div
              className="h-0.5 w-8 rounded-full"
              style={{ background: `${cap.color}60` }}
            />
          </div>
        )
      })}
    </div>
  )
}
