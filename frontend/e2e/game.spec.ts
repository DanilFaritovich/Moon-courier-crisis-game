import { expect, test, type Page } from "@playwright/test";

test.describe.configure({ mode: "serial" });

async function assignRoverToAlpha(page: Page): Promise<void> {
  const rover = page.getByTestId("rover-1");
  const destination = page.getByTestId("map-point-2");
  const dataTransfer = await page.evaluateHandle(() => new DataTransfer());

  await rover.dispatchEvent("dragstart", { dataTransfer });
  await expect(destination).toHaveClass(/valid/);
  await destination.dispatchEvent("dragover", { dataTransfer });
  await destination.dispatchEvent("drop", { dataTransfer });
  await expect(page.getByText("CONFIRM DEPLOYMENT")).toBeVisible();
  await page.getByTestId("confirm-delivery").click();
  await expect(rover).toContainText("delivering");
}

test("assigns, cancels, and completes rover deliveries", async ({ page }) => {
  await page.goto("/");
  await expect(page.getByText("LUNAR SECTOR 07")).toBeVisible();
  await expect(page.getByTestId("rover-1")).toContainText("idle");

  await assignRoverToAlpha(page);
  await page.getByTestId("rover-1").getByText("CANCEL DELIVERY").click();
  await expect(page.getByTestId("rover-1")).toContainText("idle");

  await assignRoverToAlpha(page);
  await page.getByTestId("next-turn").click();
  await expect(page.getByText("TURN 2")).toBeVisible();
  await expect(page.getByTestId("rover-1")).toContainText("idle");
});
