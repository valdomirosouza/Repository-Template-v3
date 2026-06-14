import { expect, test } from "@playwright/test";

/**
 * HITL operator approval journey — runs against MOCK MODE (NEXT_PUBLIC_HITL_MOCK=1), so no backend
 * or operator JWT is required. Start the app with mock mode, e.g.:
 *
 *   NEXT_PUBLIC_HITL_MOCK=1 pnpm dev      # then: pnpm e2e
 *
 * Skipped automatically unless E2E_HITL_MOCK=1 is set, so it never fails a default CI run that has
 * no mock-mode server.
 */
test.describe("HITL approval queue (mock mode)", () => {
  test.skip(
    process.env.E2E_HITL_MOCK !== "1",
    "set E2E_HITL_MOCK=1 with a mock-mode server running",
  );

  test("operator approves a request and it leaves the queue", async ({ page }) => {
    await page.goto("/hitl");

    await expect(page.getByRole("heading", { name: "HITL Approval Queue" })).toBeVisible();
    await expect(page.getByText("Mock mode", { exact: false })).toBeVisible();

    // The high-risk seeded action is present.
    const highRiskCard = page.locator("article", { hasText: "write_file" });
    await expect(highRiskCard).toBeVisible();
    await expect(highRiskCard.getByText(/High · risk/)).toBeVisible();

    // Approve requires a rationale.
    await highRiskCard.getByPlaceholder("Rationale (required)").fill("verified deploy config");
    await highRiskCard.getByRole("button", { name: "Approve" }).click();

    // The approved card leaves the queue.
    await expect(page.locator("article", { hasText: "write_file" })).toHaveCount(0);
  });
});
