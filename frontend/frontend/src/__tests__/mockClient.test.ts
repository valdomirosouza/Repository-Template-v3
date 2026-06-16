import { createMockHitlClient, mockSeedRequests } from "@/lib/hitl/mockClient";

describe("mock HITL client", () => {
  it("seeds synthetic requests across the risk bands", async () => {
    const client = createMockHitlClient();
    const pending = await client.listPendingRequests();
    expect(pending).toHaveLength(3);
    expect(pending.map((r) => r.requestId)).toContain("mock-req-high");
    // Synthetic + PII-free: any PII-shaped value must already be masked.
    expect(
      pending.every(
        (r) => !/@.+\..+/.test(r.contextSummary) || r.contextSummary.includes("[EMAIL]"),
      ),
    ).toBe(true);
  });

  it("removes a request when a decision is submitted (no re-run of side effects)", async () => {
    const client = createMockHitlClient();
    const before = await client.listPendingRequests();
    const target = before[0].requestId;

    const out = await client.submitDecision({ requestId: target, approved: true, rationale: "ok" });
    expect(out.decision).toBe("APPROVED");
    expect(out.requestId).toBe(target);

    const after = await client.listPendingRequests();
    expect(after.map((r) => r.requestId)).not.toContain(target);
    expect(after).toHaveLength(before.length - 1);
  });

  it("reports pending count via status", async () => {
    const client = createMockHitlClient(mockSeedRequests());
    const status = await client.hitlStatus();
    expect(status.pendingCount).toBe(3);
    expect(status.status).toBe("operational");
  });

  it("isolates state per instance", async () => {
    const a = createMockHitlClient();
    await a.submitDecision({ requestId: "mock-req-low", approved: false, rationale: "no" });
    const b = createMockHitlClient();
    expect(await b.listPendingRequests()).toHaveLength(3); // fresh instance unaffected
  });
});
