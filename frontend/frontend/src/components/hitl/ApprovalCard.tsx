"use client";

import { useState } from "react";
import type { HITLRequestSummary } from "@/lib/api";

interface Props {
  request: HITLRequestSummary;
  onDecision: (id: string, approved: boolean, rationale: string) => Promise<void>;
}

export interface RiskBand {
  label: "Low" | "Medium" | "High";
  color: string;
  explanation: string;
}

/**
 * Map a 0–1 risk score to an operator-facing band. The 0.70 boundary mirrors the agent governance
 * human-review threshold (CLAUDE.md LLM09): at/above it, an action is treated as high-risk.
 */
export function riskBand(score: number): RiskBand {
  if (score >= 0.7) {
    return {
      label: "High",
      color: "#dc2626",
      explanation:
        "At or above the 0.70 human-review threshold — high-risk. Review the proposed action carefully before approving.",
    };
  }
  if (score >= 0.4) {
    return {
      label: "Medium",
      color: "#d97706",
      explanation: "Moderate risk — confirm the action matches intent before approving.",
    };
  }
  return {
    label: "Low",
    color: "#16a34a",
    explanation: "Below the elevated-risk band — routine review.",
  };
}

export function ApprovalCard({ request, onDecision }: Props) {
  const [rationale, setRationale] = useState("");
  const [submitting, setSubmitting] = useState(false);

  const handle = async (approved: boolean) => {
    if (!rationale.trim()) return;
    setSubmitting(true);
    try {
      await onDecision(request.requestId, approved, rationale);
    } finally {
      setSubmitting(false);
    }
  };

  const band = riskBand(request.riskScore);

  return (
    <article
      style={{
        border: "1px solid #e5e7eb",
        borderRadius: "8px",
        padding: "1.25rem",
        background: "#fff",
      }}
    >
      <header
        style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start" }}
      >
        <div>
          <strong>{request.actionType}</strong>
          <span style={{ marginLeft: "0.5rem", fontSize: "0.75rem", color: "#6b7280" }}>
            {request.agentId}
          </span>
        </div>
        <span
          style={{ color: band.color, fontWeight: 600, fontSize: "0.875rem" }}
          aria-label={`Risk ${band.label}, ${(request.riskScore * 100).toFixed(0)} percent`}
        >
          {band.label} · risk {(request.riskScore * 100).toFixed(0)}%
        </span>
      </header>

      <details style={{ marginTop: "0.5rem", fontSize: "0.75rem", color: "#6b7280" }}>
        <summary style={{ cursor: "pointer" }}>Why this risk level?</summary>
        <span>{band.explanation}</span>
      </details>

      <p
        style={{
          marginTop: "0.75rem",
          marginBottom: "0.25rem",
          fontSize: "0.75rem",
          color: "#374151",
        }}
      >
        Proposed action — PII-masked preview (raw parameters never leave the gateway):
      </p>
      <pre
        style={{
          padding: "0.75rem",
          background: "#f3f4f6",
          borderRadius: "4px",
          fontSize: "0.8rem",
          overflow: "auto",
          whiteSpace: "pre-wrap",
        }}
      >
        {request.contextSummary}
      </pre>

      <p style={{ marginTop: "0.5rem", fontSize: "0.75rem", color: "#9ca3af" }}>
        Expires: {new Date(request.expiresAt).toLocaleString()}
      </p>

      <div style={{ marginTop: "1rem" }}>
        <textarea
          value={rationale}
          onChange={(e) => setRationale(e.target.value)}
          placeholder="Rationale (required)"
          rows={2}
          style={{
            width: "100%",
            padding: "0.5rem",
            borderRadius: "4px",
            border: "1px solid #d1d5db",
          }}
        />
        <div style={{ marginTop: "0.5rem", display: "flex", gap: "0.5rem" }}>
          <button
            onClick={() => handle(true)}
            disabled={submitting || !rationale.trim()}
            style={{
              padding: "0.5rem 1rem",
              background: "#16a34a",
              color: "#fff",
              border: "none",
              borderRadius: "4px",
              cursor: "pointer",
            }}
          >
            Approve
          </button>
          <button
            onClick={() => handle(false)}
            disabled={submitting || !rationale.trim()}
            style={{
              padding: "0.5rem 1rem",
              background: "#dc2626",
              color: "#fff",
              border: "none",
              borderRadius: "4px",
              cursor: "pointer",
            }}
          >
            Reject
          </button>
        </div>
      </div>
    </article>
  );
}
