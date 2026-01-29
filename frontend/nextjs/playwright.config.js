// Playwright config for simple login flow test
const { devices } = require('@playwright/test');

module.exports = {
  timeout: 30 * 1000,
  use: {
    headless: true,
    viewport: { width: 1280, height: 720 },
    baseURL: process.env.NEXT_PUBLIC_BASE_URL || 'http://localhost:3000'
  }
};
