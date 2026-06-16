/**
 * HITL client facade.
 *
 * Wraps the generated OpenAPI `HitlApi` behind a small, UI-friendly interface and selects a mock
 * implementation when `NEXT_PUBLIC_HITL_MOCK=1` — so the operator console can run, be demoed, and be
 * E2E-tested with no backend (and no operator JWT). In non-mock mode it calls the real API; supplying
 * the operator bearer token is wired via Configuration.accessToken (a deployment concern, not set
 * here).
 */

import {
  Configuration,
  DecisionInDecisionEnum,
  HitlApi,
  type DecisionOut,
  type HITLRequestSummary,
  type HITLStatusResponse,
} from "@/lib/api";

import { createMockHitlClient } from "./mockClient";

export interface SubmitDecisionArgs {
  requestId: string;
  approved: boolean;
  rationale: string;
}

/** The subset of HITL operations the console needs. */
export interface HitlClient {
  listPendingRequests(): Promise<HITLRequestSummary[]>;
  submitDecision(args: SubmitDecisionArgs): Promise<DecisionOut>;
  hitlStatus(): Promise<HITLStatusResponse>;
}

/** True when the console is running against in-memory mock data (no backend). */
export function isMockMode(): boolean {
  return process.env.NEXT_PUBLIC_HITL_MOCK === "1";
}

function createRealHitlClient(): HitlClient {
  const api = new HitlApi(new Configuration({ basePath: process.env.NEXT_PUBLIC_API_BASE_URL }));
  return {
    listPendingRequests: () => api.listPendingRequests(),
    submitDecision: ({ requestId, approved, rationale }: SubmitDecisionArgs) =>
      api.submitDecision({
        requestId,
        decisionIn: {
          decision: approved ? DecisionInDecisionEnum.Approved : DecisionInDecisionEnum.Rejected,
          rationale,
        },
      }),
    hitlStatus: () => api.hitlStatus(),
  };
}

/** Returns the mock client in mock mode, otherwise the real API-backed client. */
export function getHitlClient(): HitlClient {
  return isMockMode() ? createMockHitlClient() : createRealHitlClient();
}
