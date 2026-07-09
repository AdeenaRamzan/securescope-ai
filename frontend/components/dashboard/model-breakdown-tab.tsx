"use client"

import { Brain } from "lucide-react"
import type { ScanResult } from "@/lib/types"
import { formatPercent, clampPercent } from "@/lib/types"
import {
  PieChart, Pie, Cell, ResponsiveContainer,
  BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip,
} from "recharts"

interface ModelBreakdownTabProps {
  result: ScanResult
}

const CHART_COLORS = ['#00d5ff', '#7c3aed', '#ff3ea5']

function CustomTooltip({ active, payload }: any) {
  if (!active || !payload?.length) return null
  return (
    <div className="rounded-lg border border-white/10 bg-[#10131a] px-3 py-2 text-xs shadow-xl">
      <span className="font-semibold text-white">{payload[0].name}: </span>
      <span className="text-slate-300">{(payload[0].value * 100).toFixed(1)}%</span>
    </div>
  )
}

function BarTooltip({ active, payload }: any) {
  if (!active || !payload?.length) return null
  return (
    <div className="rounded-lg border border-white/10 bg-[#10131a] px-3 py-2 text-xs shadow-xl">
      <span className="font-semibold text-white">{payload[0].payload.name}: </span>
      <span className="text-slate-300">{payload[0].value.toFixed(1)}%</span>
    </div>
  )
}

export function ModelBreakdownTab({ result }: ModelBreakdownTabProps) {
  // Phase 1: Donut chart
  if (result._mode === 'quick') {
    const data = [
      { name: 'ANN', value: result.model_probs.ann },
      { name: 'XGBoost', value: result.model_probs.xgboost },
      { name: 'LightGBM', value: result.model_probs.lightgbm },
    ]

    return (
      <div className="animate-fade-scale-in">
        <div className="grid gap-6 md:grid-cols-[1fr_280px]">
          <div className="premium-panel flex items-center justify-center rounded-2xl p-6">
            <ResponsiveContainer width={260} height={260}>
              <PieChart>
                <Pie
                  data={data}
                  cx="50%" cy="50%"
                  innerRadius={70} outerRadius={100}
                  paddingAngle={3}
                  dataKey="value"
                  strokeWidth={0}
                >
                  {data.map((_, i) => (
                    <Cell key={i} fill={CHART_COLORS[i]} style={{ filter: `drop-shadow(0 0 6px ${CHART_COLORS[i]}60)` }} />
                  ))}
                </Pie>
                <Tooltip content={<CustomTooltip />} />
              </PieChart>
            </ResponsiveContainer>
          </div>
          <div className="flex flex-col gap-3">
            {data.map((item, i) => (
              <div key={item.name} className="premium-panel rounded-xl p-4">
                <div className="mb-2 flex items-center gap-2">
                  <div className="h-3 w-3 rounded-full" style={{ background: CHART_COLORS[i], boxShadow: `0 0 8px ${CHART_COLORS[i]}60` }} />
                  <span className="text-xs font-semibold uppercase tracking-wider text-slate-400">{item.name}</span>
                </div>
                <div className="text-2xl font-bold text-white">{formatPercent(item.value)}</div>
                <div className="mt-2 meter-track h-1.5 overflow-hidden rounded-full">
                  <div
                    className="animate-fill-bar h-full rounded-full"
                    style={{ width: `${clampPercent(item.value)}%`, background: CHART_COLORS[i] }}
                  />
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
    )
  }

  // Phase 2: BiLSTM gauge
  if (result._mode === 'bilstm') {
    const bilstmConf = result.model_probs?.bilstm ?? result.confidence

    return (
      <div className="animate-fade-scale-in mx-auto max-w-md">
        <div className="premium-panel flex flex-col items-center gap-5 rounded-2xl p-8">
          <div className="rounded-2xl bg-[#7c3aed]/10 p-4">
            <Brain className="h-12 w-12 text-[#7c3aed]" style={{ filter: 'drop-shadow(0 0 10px rgba(124,58,237,0.5))' }} />
          </div>
          <h3 className="text-sm font-semibold uppercase tracking-wider text-slate-400">BiLSTM Sequence Model</h3>
          <div className="text-5xl font-bold text-white">{formatPercent(bilstmConf)}</div>
          <div className="meter-track h-3 w-full overflow-hidden rounded-full">
            <div
              className="animate-fill-bar h-full rounded-full bg-[#7c3aed]"
              style={{ width: `${clampPercent(bilstmConf)}%`, boxShadow: '0 0 12px rgba(124,58,237,0.5)' }}
            />
          </div>
          <div className="flex gap-4 text-xs text-slate-500">
            {result.threshold_used !== undefined && (
              <span>Threshold: {formatPercent(result.threshold_used)}</span>
            )}
            {result.model_version && (
              <span>Version: {result.model_version}</span>
            )}
          </div>
        </div>
      </div>
    )
  }

  // Cascade: Bar chart
  if (result._mode === 'cascade') {
    const data = [
      { name: 'Phase 1', value: clampPercent(result.phase1_confidence), fill: '#00d5ff' },
      { name: 'Phase 2', value: clampPercent(result.phase2_confidence), fill: '#7c3aed' },
      { name: 'Combined', value: clampPercent(result.confidence), fill: '#ff3ea5' },
    ]

    return (
      <div className="animate-fade-scale-in">
        <div className="premium-panel rounded-2xl p-6">
          <h3 className="mb-4 text-sm font-semibold text-slate-300">Phase Confidence Comparison</h3>
          <ResponsiveContainer width="100%" height={300}>
            <BarChart data={data} barSize={40}>
              <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.06)" />
              <XAxis dataKey="name" tick={{ fill: '#748194', fontSize: 12 }} axisLine={false} tickLine={false} />
              <YAxis tick={{ fill: '#748194', fontSize: 12 }} axisLine={false} tickLine={false} domain={[0, 100]} />
              <Tooltip content={<BarTooltip />} cursor={{ fill: 'rgba(255,255,255,0.03)' }} />
              <Bar dataKey="value" radius={[8, 8, 0, 0]}>
                {data.map((entry, i) => (
                  <Cell key={i} fill={entry.fill} style={{ filter: `drop-shadow(0 0 6px ${entry.fill}50)` }} />
                ))}
              </Bar>
            </BarChart>
          </ResponsiveContainer>
          {result.model_version && (
            <p className="mt-3 text-center text-xs text-slate-500">Model: {result.model_version}</p>
          )}
        </div>
      </div>
    )
  }

  // Phase 3: Pipeline visualization
  if (result._mode === 'explain') {
    const stages = [
      { label: 'Binary Detection', key: 'binary' },
      { label: 'Complete Analysis', key: 'complete' },
    ]
    // All stages complete since we got a response
    const stageIndex = 2

    return (
      <div className="animate-fade-scale-in">
        <div className="premium-panel rounded-2xl p-8">
          <h3 className="mb-8 text-center text-sm font-semibold text-slate-300">Pipeline Progress</h3>
          <div className="flex items-center justify-center gap-4">
            {stages.map((stage, i) => {
              const isComplete = i < stageIndex
              return (
                <div key={stage.key} className="flex items-center gap-4">
                  <div className="flex flex-col items-center gap-2">
                    <div
                      className={`flex h-14 w-14 items-center justify-center rounded-full border-2 text-sm font-bold ${
                        isComplete
                          ? 'border-[#00d5ff]/40 bg-[#00d5ff]/15 text-[#00d5ff]'
                          : 'border-white/10 bg-white/5 text-slate-500'
                      }`}
                      style={isComplete ? { boxShadow: '0 0 15px rgba(0,213,255,0.2)' } : undefined}
                    >
                      {i + 1}
                    </div>
                    <span className={`max-w-[120px] text-center text-xs font-medium ${isComplete ? 'text-[#00d5ff]' : 'text-slate-500'}`}>
                      {stage.label}
                    </span>
                  </div>
                  {i < stages.length - 1 && (
                    <div className={`mb-6 h-0.5 w-16 rounded-full ${i < stageIndex - 1 ? 'bg-[#00d5ff]' : 'bg-white/10'}`}
                      style={i < stageIndex - 1 ? { boxShadow: '0 0 8px rgba(0,213,255,0.4)' } : undefined}
                    />
                  )}
                </div>
              )
            })}
          </div>
          <div className="mt-6 flex items-center justify-center gap-2">
            <span className="rounded-full border border-[#00d5ff]/20 bg-[#00d5ff]/10 px-3 py-1 text-xs font-semibold text-[#00d5ff]">
              {result.pipeline}
            </span>
            {result.llm && (
              <span className="rounded-full border border-[#7c3aed]/20 bg-[#7c3aed]/10 px-3 py-1 text-xs font-semibold text-[#a78bfa]">
                {result.llm}
              </span>
            )}
          </div>
          <div className="mt-6 text-center">
            <div className="text-3xl font-bold text-white">{formatPercent(result.confidence)}</div>
            <div className="mt-1 text-xs text-slate-500">Overall Confidence</div>
          </div>
        </div>
      </div>
    )
  }

  return null
}
