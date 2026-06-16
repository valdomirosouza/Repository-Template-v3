import { expect, test } from "@playwright/test";

/**
 * HITL operator approval journey — runs against MOCK MODE, so no backend or operator JWT is
 * required. The Playwright webServer (playwright.config.ts) starts `pnpm dev` with
 * NEXT_PUBLIC_HITL_MOCK=1, so `pnpm e2e` works standalone in CI and locally.
 */
test.describe("HITL approval queue (mock mode)", () => {
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
