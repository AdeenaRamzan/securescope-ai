// ── Scan modes mapped to API endpoints ──────────────────────────────
export type ScanMode = "quick" | "bilstm" | "cascade" | "explain";

export const SCAN_MODE_META: Record<
  ScanMode,
  { label: string; endpoint: string; phase: string; caption: string; icon: string }
> = {
  quick: {
    label: "Quick Scan",
    endpoint: "/scan",
    phase: "Phase 1",
    caption: "ANN + XGBoost + LightGBM ensemble ML",
    icon: "⚡",
  },
  bilstm: {
    label: "BiLSTM Scan",
    endpoint: "/scan/bilstm",
    phase: "Phase 2",
    caption: "BiLSTM sequence-model analysis",
    icon: "🧠",
  },
  cascade: {
    label: "Cascade Scan",
    endpoint: "/scan/cascade",
    phase: "Phase 1 + 2",
    caption: "Combined ensemble + BiLSTM cascade",
    icon: "🔗",
  },
  explain: {
    label: "Full Explain",
    endpoint: "/scan/deep",
    phase: "Phase 3",
    caption: "CodeBERT + RAG + LLM explanation",
    icon: "🔬",
  },
};

// ── API response shapes ─────────────────────────────────────────────

/** POST /scan — Phase 1 ensemble */
export interface Phase1Result {
  is_vulnerable: boolean;
  confidence: number;
  risk_level: RiskLevel;
  threshold_used: number;
  model_version: string;
  model_probs: {
    ann: number;
    xgboost: number;
    lightgbm: number;
  };
  features_fired: string[];
  scan_time_ms: number;
}

/** POST /scan/bilstm — Phase 2 BiLSTM */
export interface Phase2Result {
  is_vulnerable: boolean;
  confidence: number;
  risk_level: RiskLevel;
  threshold_used?: number;
  model_version?: string;
  model_probs?: {
    bilstm: number;
  };
  scan_time_ms: number;
}

/** POST /scan/deep — Phase 1 + 2 cascade */
export interface CascadeResult {
  is_vulnerable: boolean;
  confidence: number;
  risk_level: RiskLevel;
  phase1_confidence?: number;
  phase2_confidence?: number;
  model_version?: string;
  model_probs?: Record<string, number>;
  features_fired?: string[];
  scan_time_ms: number;
}

/** POST /scan/deep — Phase 3 CodeBERT + RAG + LLM */
export interface Phase3Result {
  is_vulnerable: boolean;
  confidence: number;
  risk_level: RiskLevel;
  vulnerability_type: string;
  danger: string;
  fix: string;
  owasp_ref: string;
  pipeline: string;
  llm: string;
  scan_time_ms: number;
}

export type RiskLevel = "HIGH" | "MEDIUM" | "LOW" | "SAFE" | "INCONCLUSIVE";

/** Unified scan result — discriminated by `_mode` tag we attach client-side */
export type ScanResult =
  | ({ _mode: "quick" } & Phase1Result)
  | ({ _mode: "bilstm" } & Phase2Result)
  | ({ _mode: "cascade" } & CascadeResult)
  | ({ _mode: "explain" } & Phase3Result);

// ── Scan history ────────────────────────────────────────────────────
export interface ScanHistoryItem {
  id: string;
  filename: string;
  timestamp: Date;
  code: string;
  mode: ScanMode;
  result: ScanResult;
  riskLevel: RiskLevel | null;
}

// ── Helpers ─────────────────────────────────────────────────────────
export function getRiskLevel(result: ScanResult): RiskLevel {
  if ("risk_level" in result && result.risk_level) return result.risk_level;
  // Phase 3 doesn't return risk_level — derive from confidence
  const conf = result.confidence;
  if (conf >= 0.75) return "HIGH";
  if (conf >= 0.5) return "MEDIUM";
  if (conf >= 0.25) return "LOW";
  return "SAFE";
}

export function formatPercent(value?: number | null): string {
  if (typeof value !== "number") return "N/A";
  return `${(value * 100).toFixed(1)}%`;
}

export function clampPercent(value?: number | null): number {
  if (typeof value !== "number") return 0;
  return Math.max(0, Math.min(100, value * 100));
}

export function formatVulnType(value?: string | null): string {
  if (!value || value === "unknown") return "Unknown";
  return value
    .split("_")
    .map((w) => w.charAt(0).toUpperCase() + w.slice(1))
    .join(" ");
}

export function timeAgo(date: Date): string {
  const seconds = Math.floor((Date.now() - date.getTime()) / 1000);
  if (seconds < 60) return "just now";
  const minutes = Math.floor(seconds / 60);
  if (minutes < 60) return `${minutes}m ago`;
  const hours = Math.floor(minutes / 60);
  if (hours < 24) return `${hours}h ago`;
  const days = Math.floor(hours / 24);
  return `${days}d ago`;
}
