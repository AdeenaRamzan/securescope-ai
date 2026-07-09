"use client"

import { useState, useRef } from "react"
import { Upload, X, FileCode } from "lucide-react"

interface CodeInputSectionProps {
  code: string
  onChange: (code: string) => void
  onClear: () => void
  disabled: boolean
  filename: string
  onFilenameChange: (name: string) => void
}

export function CodeInputSection({
  code,
  onChange,
  onClear,
  disabled,
  filename,
  onFilenameChange,
}: CodeInputSectionProps) {
  const [isDragging, setIsDragging] = useState(false)
  const fileInputRef = useRef<HTMLInputElement>(null)

  const handleFileUpload = (file: File) => {
    if (!file.name.endsWith(".py") && file.type !== "text/plain") return
    onFilenameChange(file.name)
    const reader = new FileReader()
    reader.onload = (e) => onChange(String(e.target?.result ?? ""))
    reader.readAsText(file)
  }

  return (
    <div className="flex flex-col gap-3">
      <div
        className={`group relative overflow-hidden rounded-2xl transition-all ${
          isDragging
            ? "drag-active border-2 border-dashed border-[#00d5ff]/40"
            : "border border-white/[0.06] hover:border-[#00d5ff]/20"
        }`}
        style={{ background: '#0a0d14' }}
        onDragOver={(e) => { e.preventDefault(); setIsDragging(true) }}
        onDragLeave={() => setIsDragging(false)}
        onDrop={(e) => {
          e.preventDefault()
          setIsDragging(false)
          const file = e.dataTransfer.files[0]
          if (file) handleFileUpload(file)
        }}
      >
        {/* Drag overlay */}
        {isDragging && (
          <div className="absolute inset-0 z-10 flex flex-col items-center justify-center gap-3 bg-[#00d5ff]/[0.04] backdrop-blur-sm">
            <Upload className="h-10 w-10 text-[#00d5ff] animate-bounce" />
            <p className="text-sm font-semibold text-[#00d5ff]">Drop your Python file here...</p>
          </div>
        )}

        {/* Terminal chrome */}
        <div className="flex items-center justify-between border-b border-white/[0.06] px-5 py-3">
          <div className="flex items-center gap-3">
            <div className="flex gap-2">
              <span className="h-3 w-3 rounded-full bg-[#ff5f57]" />
              <span className="h-3 w-3 rounded-full bg-[#febc2e]" />
              <span className="h-3 w-3 rounded-full bg-[#28c840]" />
            </div>
            <div className="flex items-center gap-2">
              <FileCode className="h-3.5 w-3.5 text-slate-500" />
              <span className="text-xs text-slate-400">{filename}</span>
            </div>
          </div>
          <span className="rounded bg-[#00d5ff]/10 px-2 py-0.5 text-[10px] font-semibold text-[#00d5ff]">
            Python
          </span>
        </div>

        {/* Textarea */}
        <textarea
          value={code}
          onChange={(e) => onChange(e.target.value)}
          disabled={disabled}
          placeholder={"# Paste your Python code here...\n# Or drag and drop a .py file\n\nimport os\ndef process(user_input):\n    os.system(user_input)  # Potential vulnerability"}
          className="code-textarea w-full resize-none bg-transparent px-5 py-4 font-mono text-sm leading-relaxed text-slate-200 placeholder:text-slate-600 focus:outline-none disabled:cursor-not-allowed disabled:opacity-50"
          style={{ minHeight: '280px' }}
          spellCheck={false}
          aria-label="Python code input"
        />
      </div>

      {/* Action bar */}
      <div className="flex items-center gap-3">
        <input
          ref={fileInputRef}
          type="file"
          accept=".py,text/plain"
          onChange={(e) => {
            const file = e.target.files?.[0]
            if (file) handleFileUpload(file)
          }}
          className="hidden"
        />
        <button
          onClick={() => fileInputRef.current?.click()}
          disabled={disabled}
          className="glass-sm flex items-center gap-2 rounded-xl px-4 py-2.5 text-sm font-medium text-slate-400 transition-all hover:border-[#00d5ff]/25 hover:text-[#00d5ff] disabled:opacity-50"
        >
          <Upload className="h-4 w-4" />
          Upload .py
        </button>
        {code && (
          <button
            onClick={onClear}
            disabled={disabled}
            className="flex items-center gap-2 rounded-xl px-4 py-2.5 text-sm font-medium text-slate-500 transition-all hover:bg-white/[0.04] hover:text-slate-300 disabled:opacity-50"
          >
            <X className="h-4 w-4" />
            Clear
          </button>
        )}
        <span className="ml-auto text-xs text-slate-600">
          {code.length.toLocaleString()} chars
        </span>
      </div>
    </div>
  )
}
