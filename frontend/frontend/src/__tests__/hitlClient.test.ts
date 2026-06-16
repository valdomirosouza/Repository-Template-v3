import { getHitlClient, isMockMode } from "@/lib/hitl/client";

const ORIGINAL = process.env.NEXT_PUBLIC_HITL_MOCK;

afterEach(() => {
  if (ORIGINAL === undefined) delete process.env.NEXT_PUBLIC_HITL_MOCK;
  else process.env.NEXT_PUBLIC_HITL_MOCK = ORIGINAL;
});

describe("getHitlClient / isMockMode", () => {
  it("isMockMode is true only when NEXT_PUBLIC_HITL_MOCK=1", () => {
    process.env.NEXT_PUBLIC_HITL_MOCK = "1";
    expect(isMockMode()).toBe(true);
    process.env.NEXT_PUBLIC_HITL_MOCK = "0";
    expect(isMockMode()).toBe(false);
    delete process.env.NEXT_PUBLIC_HITL_MOCK;
    expect(isMockMode()).toBe(false);
  });

  it("returns the in-memory mock client in mock mode", async () => {
    process.env.NEXT_PUBLIC_HITL_MOCK = "1";
    const client = getHitlClient();
    const pending = await client.listPendingRequests();
    expect(pending).toHaveLength(3); // seeded mock data, no backend
  });

  it("returns an API-backed client (with the full surface) when not in mock mode", () => {
    process.env.NEXT_PUBLIC_HITL_MOCK = "0";
    const client = getHitlClient();
    expect(typeof client.listPendingRequests).toBe("function");
    expect(typeof client.submitDecision).toBe("function");
    expect(typeof client.hitlStatus).toBe("function");
  });
});
