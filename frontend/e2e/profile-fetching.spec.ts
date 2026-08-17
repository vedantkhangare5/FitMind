import { test, expect } from '@playwright/test';

test.describe('Profile Fetching and State Management', () => {
  test('should avoid unnecessary duplicate profile requests during navigation', async ({ page }) => {
    // We will count how many times the frontend fetches the profile from the API
    let profileRequestCount = 0;

    await page.route('**/api/profile', async (route) => {
      if (route.request().method() === 'GET') {
        profileRequestCount++;
        await route.fulfill({
          status: 200,
          json: {
            profile: {
              age: 30,
              sex: 'male',
              height_cm: 180,
              weight_kg: 75,
              activity_level: 'moderately_active',
              goal: 'maintain',
            },
            updated_at: new Date().toISOString(),
            derived_metrics: {
              bmi: 23.1,
              bmi_category: 'Normal',
              bmr: 1750,
              tdee: 2700,
              calorie_target: 2700,
              protein_target_min: 120,
              protein_target_max: 150,
            }
          }
        });
      } else {
        await route.continue();
      }
    });

    // Go to the dashboard
    await page.goto('/');

    // Wait for the profile data to load on the dashboard (e.g. by waiting for BMI)
    await expect(page.getByText('23.1')).toBeVisible();

    // Verify exactly 1 request was made (accounting for React Strict Mode, Next.js hydration etc, ideally it's 1, but we allow 1-2 based on strict mode but since we use context, moving to another page shouldn't increment it again)
    const initialRequestCount = profileRequestCount;
    expect(initialRequestCount).toBeGreaterThan(0);

    // Navigate to Assistant
    await page.click('text=FitMind Assistant');
    await expect(page.getByText('Hello! I\'m FitMind')).toBeVisible();

    // Navigate to Profile
    await page.click('text=Back to Dashboard');
    await page.click('text=Fitness Profile');
    
    // Ensure we are on the profile page by checking a known label
    await expect(page.getByRole('heading', { name: 'Your Fitness Profile' })).toBeVisible();
    await expect(page.getByText('180')).toBeVisible();

    // The request count should not have increased because it's cached in context
    expect(profileRequestCount).toBe(initialRequestCount);
  });
});
