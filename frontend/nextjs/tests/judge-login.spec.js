const { test, expect } = require('@playwright/test');

test('judge login and redirect', async ({ page, baseURL }) => {
  // Assumes backend running locally and Next.js dev server started
  // Configure environment before running: NEXT_PUBLIC_BACKEND_URL=http://127.0.0.1:8030

  // Navigate to a session page (will redirect to /judge-login)
  await page.goto('/session/test-session-redirect');
  // We expect to be on /judge-login
  await expect(page).toHaveURL(/\/judge-login/);

  // Fill credentials (the test environment should set JUDGE_USERS env)
  await page.fill('input[name="username"]', 'alice');
  await page.fill('input[type="password"]', 'password123');
  await page.click('button:has-text("Login")');

  // After login we should redirect back to /session/test-session-redirect
  await page.waitForURL('**/session/test-session-redirect', { timeout: 5000 });
  await expect(page).toHaveURL(/session\/test-session-redirect/);
});
