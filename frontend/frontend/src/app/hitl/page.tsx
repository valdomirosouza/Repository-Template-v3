"use client";

import { useCallback, useEffect, useState } from "react";

import { ApprovalCard } from "@/components/hitl/ApprovalCard";
import { getHitlClient, isMockMode } from "@/lib/hitl/client";
import type { HITLRequestSummary } from "@/lib/api";

const client = getHitlClient();
const mockMode = isMockMode();

export default function HITLQueuePage() {
  const [requests, setRequests] = useState<HITLRequestSummary[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const load = useCallback(async () => {
    // `loading` initialises to true for the first paint; we intentionally do NOT set it
    // synchronously here — that would trip react-hooks/set-state-in-effect and flash the
    // loading state on each 15s background poll.
    try {
      const data = await client.listPendingRequests();
      setRequests(data);
      setError(null);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to load requests");
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    // `load` is async: every setState runs after `await`, so there is no synchronous
    // cascading render the rule guards against — this is a standard fetch-on-mount + poll.
    // eslint-disable-next-line react-hooks/set-state-in-effect
    load();
    const interval = setInterval(load, 15_000);
    return () => clearInterval(interval);
  }, [load]);

  const handleDecision = async (id: string, approved: boolean, rationale: string) => {
    await client.submitDecision({ requestId: id, approved, rationale });
    setRequests((prev) => prev.filter((r) => r.requestId !== id));
  };

  if (loading && requests.length === 0) {
    return <p style={{ padding: "2rem" }}>Loading approval queue…</p>;
  }

  if (error) {
    return <p style={{ padding: "2rem", color: "red" }}>Error: {error}</p>;
  }

  return (
    <main style={{ padding: "2rem", maxWidth: "900px", margin: "0 auto" }}>
      <h1>HITL Approval Queue</h1>
      {mockMode && (
        <p
          role="status"
          style={{
            marginTop: "0.5rem",
            padding: "0.5rem 0.75rem",
            background: "#fef3c7",
            border: "1px solid #f59e0b",
            borderRadius: "4px",
            fontSize: "0.8rem",
            color: "#92400e",
          }}
        >
          Mock mode — showing synthetic data, no backend. Set NEXT_PUBLIC_HITL_MOCK=0 to use the
          live API.
        </p>
      )}
      <p style={{ color: "#6b7280", marginTop: "0.5rem" }}>
        {requests.length} pending request{requests.length !== 1 ? "s" : ""}
      </p>
      <div style={{ marginTop: "1.5rem", display: "flex", flexDirection: "column", gap: "1rem" }}>
        {requests.length === 0 ? (
          <p style={{ color: "#6b7280" }}>No pending requests.</p>
        ) : (
          requests.map((req) => (
            <ApprovalCard key={req.requestId} request={req} onDecision={handleDecision} />
          ))
        )}
      </div>
    </main>
  );
}
