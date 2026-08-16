import React from "react";
import { render, screen } from "@testing-library/react";
import "@testing-library/jest-dom";

// Mock next/link
jest.mock("next/link", () => {
  return function MockLink({
    children,
    href,
  }: {
    children: React.ReactNode;
    href: string;
  }) {
    return <a href={href}>{children}</a>;
  };
});

// Mock lucide-react icons
jest.mock("lucide-react", () => ({
  ArrowLeft: () => <span data-testid="arrow-left-icon" />,
  User: () => <span data-testid="user-icon" />,
  Save: () => <span data-testid="save-icon" />,
  Trash2: () => <span data-testid="trash-icon" />,
  Pencil: () => <span data-testid="pencil-icon" />,
  X: () => <span data-testid="x-icon" />,
  CheckCircle: () => <span data-testid="check-icon" />,
}));

// Mock fetch
const mockFetch = jest.fn();
global.fetch = mockFetch;

import ProfilePage from "@/app/profile/page";

describe("ProfilePage", () => {
  beforeEach(() => {
    mockFetch.mockReset();
  });

  it("renders empty state when no profile exists", async () => {
    mockFetch.mockResolvedValueOnce({
      status: 404,
      ok: false,
    });

    render(<ProfilePage />);

    // Should show loading first, then form
    expect(
      await screen.findByText("Create Your Profile")
    ).toBeInTheDocument();
  });

  it("renders profile data when profile exists", async () => {
    mockFetch.mockResolvedValueOnce({
      status: 200,
      ok: true,
      json: async () => ({
        profile: {
          age: 21,
          sex: "male",
          height_cm: 181,
          weight_kg: 92,
          activity_level: "moderately_active",
          goal: "lose_fat",
        },
        updated_at: "2024-01-01T00:00:00Z",
        derived_metrics: {
          bmi: 28.1,
          bmi_category: "Overweight",
          bmr: 1940,
          tdee: 3007,
          calorie_target: 2507,
          protein_target_min: 147,
          protein_target_max: 202,
        },
      }),
    });

    render(<ProfilePage />);

    // Should display profile values
    expect(await screen.findByText("21")).toBeInTheDocument();
    // CSS 'capitalize' class renders as "Male" visually, but DOM text is "male"
    expect(screen.getByText("male")).toBeInTheDocument();
    expect(screen.getByText("Edit Profile")).toBeInTheDocument();
  });

  it("shows calculated metrics from backend", async () => {
    mockFetch.mockResolvedValueOnce({
      status: 200,
      ok: true,
      json: async () => ({
        profile: {
          age: 21,
          sex: "male",
          height_cm: 181,
          weight_kg: 92,
          activity_level: "moderately_active",
          goal: "lose_fat",
        },
        updated_at: "2024-01-01T00:00:00Z",
        derived_metrics: {
          bmi: 28.1,
          bmi_category: "Overweight",
          bmr: 1940,
          tdee: 3007,
          calorie_target: 2507,
          protein_target_min: 147,
          protein_target_max: 202,
        },
      }),
    });

    render(<ProfilePage />);

    // Derived metrics should come from the API response
    expect(await screen.findByText("28.1")).toBeInTheDocument();
    expect(screen.getByText("Overweight")).toBeInTheDocument();
    expect(screen.getByText("Calculated for You")).toBeInTheDocument();
  });
});
