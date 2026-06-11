"use client"

import { useRef, useState } from "react"
import { Upload, X } from "lucide-react"
import { Button } from "@/components/ui/button"

interface CodeInputProps {
  code: string
  onChange: (code: string) => void
  onClear: () => void
  disabled: boolean
}

export function CodeInput({ code, onChange, onClear, disabled }: CodeInputProps) {
  const [isDragging, setIsDragging] = useState(false)
  const fileInputRef = useRef<HTMLInputElement>(null)

  const handleFileUpload = (file: File) => {
    if (!file.name.endsWith(".py") && file.type !== "text/plain") return

    const reader = new FileReader()
    reader.onload = (event) => {
      onChange(String(event.target?.result ?? ""))
    }
    reader.readAsText(file)
  }

  return (
    <div className="flex flex-col gap-2">
      <div
        className={`group relative rounded-lg border transition-all ${
          isDragging
            ? "border-primary/60 bg-primary/5 glow-green"
            : "border-border bg-card focus-within:border-primary/50 focus-within:glow-green"
        }`}
        onDragOver={(event) => {
          event.preventDefault()
          setIsDragging(true)
        }}
        onDragLeave={() => setIsDragging(false)}
        onDrop={(event) => {
          event.preventDefault()
          setIsDragging(false)
          const file = event.dataTransfer.files[0]
          if (file) handleFileUpload(file)
        }}
      >
        <div className="flex items-center justify-between border-b border-border px-4 py-2">
          <div className="flex items-center gap-2">
            <div className="flex gap-1.5">
              <span className="h-2.5 w-2.5 rounded-full bg-[#ff5f57]" aria-hidden="true" />
              <span className="h-2.5 w-2.5 rounded-full bg-[#febc2e]" aria-hidden="true" />
              <span className="h-2.5 w-2.5 rounded-full bg-[#28c840]" aria-hidden="true" />
            </div>
            <span className="text-xs text-muted-foreground">input.py</span>
          </div>
          <span className="rounded bg-primary/10 px-2 py-0.5 text-[10px] font-medium text-primary">
            Python
          </span>
        </div>

        <textarea
          value={code}
          onChange={(event) => onChange(event.target.value)}
          disabled={disabled}
          placeholder={isDragging ? "Drop your Python file here..." : "Paste your Python code here..."}
          className="code-textarea w-full resize-none bg-transparent px-4 py-4 font-mono text-sm text-foreground placeholder:text-muted-foreground/50 focus:outline-none disabled:cursor-not-allowed disabled:opacity-50"
          style={{ minHeight: "260px" }}
          spellCheck={false}
          aria-label="Python code input"
        />
      </div>

      <div className="flex flex-wrap items-center gap-2">
        <input
          ref={fileInputRef}
          type="file"
          accept=".py,text/plain"
          onChange={(event) => {
            const file = event.target.files?.[0]
            if (file) handleFileUpload(file)
          }}
          className="hidden"
          aria-label="Upload Python file"
        />
        <Button
          size="sm"
          variant="outline"
          onClick={() => fileInputRef.current?.click()}
          disabled={disabled}
          className="gap-2 transition-smooth"
        >
          <Upload className="h-4 w-4" />
          Upload File
        </Button>
        {code && (
          <Button
            size="sm"
            variant="ghost"
            onClick={onClear}
            disabled={disabled}
            className="gap-2 text-muted-foreground transition-smooth hover:text-foreground"
          >
            <X className="h-4 w-4" />
            Clear
          </Button>
        )}
      </div>
    </div>
  )
}
