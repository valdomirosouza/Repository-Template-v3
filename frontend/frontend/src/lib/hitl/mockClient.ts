/**
 * In-memory mock HITL client for demos, local dev, and E2E (no backend / no operator JWT).
 * Enabled via NEXT_PUBLIC_HITL_MOCK=1 (see ./client). State lives for the lifetime of the instance,
 * so approving/rejecting removes the card just like the real flow. All data is obviously synthetic
 * and PII-free (CLAUDE.md §3.1).
 */

import {
  HITLRequestSummaryStatusEnum,
  type DecisionOut,
  type HITLRequestSummary,
  type HITLStatusResponse,
} from "@/lib/api";

import type { HitlClient, SubmitDecisionArgs } from "./client";

/** Three synthetic pending requests spanning the low/medium/high risk bands. */
export function mockSeedRequests(): HITLRequestSummary[] {
  const base = Date.parse("2026-06-14T12:00:00Z");
  const iso = (offsetMs: number) => new Date(base + offsetMs).toISOString();
  return [
    {
      requestId: "mock-req-low",
      agentId: "agent-research",
      actionType: "summarise_document",
      contextSummary: "Summarise the Q2 report for [EMAIL]. Read-only; no external calls.",
      riskScore: 0.2,
      status: HITLRequestSummaryStatusEnum.Pending,
      createdAt: iso(0),
      expiresAt: iso(60 * 60 * 1000),
    },
    {
      requestId: "mock-req-medium",
      agentId: "agent-ops",
      actionType: "update_ticket",
      contextSummary: "Move ticket OPS-1234 to 'in progress' and assign to [TOKEN].",
      riskScore: 0.55,
      status: HITLRequestSummaryStatusEnum.Pending,
      createdAt: iso(60_000),
      expiresAt: iso(60 * 60 * 1000),
    },
    {
      requestId: "mock-req-high",
      agentId: "agent-infra",
      actionType: "write_file",
      contextSummary: "Write deploy config to /etc/app/config.yaml (replaces current values).",
      riskScore: 0.82,
      status: HITLRequestSummaryStatusEnum.Pending,
      createdAt: iso(120_000),
      expiresAt: iso(60 * 60 * 1000),
    },
  ];
}

export function createMockHitlClient(seed: HITLRequestSummary[] = mockSeedRequests()): HitlClient {
  let queue: HITLRequestSummary[] = [...seed];

  return {
    async listPendingRequests(): Promise<HITLRequestSummary[]> {
      return [...queue];
    },

    async submitDecision({ requestId, approved }: SubmitDecisionArgs): Promise<DecisionOut> {
      queue = queue.filter((r) => r.requestId !== requestId);
      return {
        requestId,
        decision: approved ? "APPROVED" : "REJECTED",
        message: `Decision recorded (mock) for ${requestId}.`,
      };
    },

    async hitlStatus(): Promise<HITLStatusResponse> {
      return {
        status: "operational",
        pendingCount: queue.length,
        message: "Mock HITL gateway (NEXT_PUBLIC_HITL_MOCK=1).",
      };
    },
  };
}
