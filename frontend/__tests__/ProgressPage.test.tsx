import { render, screen, waitFor } from "@testing-library/react";
import ProgressPage from "@/app/progress/page";

// Mock fetch
global.fetch = jest.fn();

describe("ProgressPage", () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  it("renders loading state initially", () => {
    (global.fetch as jest.Mock).mockImplementation(() => new Promise(() => {}));
    render(<ProgressPage />);
    // The spinner should be there
    expect(screen.getByRole("main")).toBeInTheDocument();
  });

  it("renders empty state correctly", async () => {
    (global.fetch as jest.Mock).mockResolvedValueOnce({
      ok: true,
      headers: { get: () => 'application/json' },
      json: async () => ({
        entries: [],
        summary: {
          current_weight: null,
          starting_weight: null,
          total_change_kg: null,
          percentage_change: null,
          trend: "insufficient_data",
          entries_count: 0,
          note: null
        }
      })
    });

    render(<ProgressPage />);

    await waitFor(() => {
      expect(screen.getByText("No entries recorded yet.")).toBeInTheDocument();
    });

    // Check if chart displays the empty state message
    expect(screen.getByText("No progress data yet. Add an entry below to see your trend.")).toBeInTheDocument();
  });

  it("renders history and summary", async () => {
    (global.fetch as jest.Mock).mockResolvedValueOnce({
      ok: true,
      headers: { get: () => 'application/json' },
      json: async () => ({
        entries: [
          { id: 1, weight_kg: 90.0, recorded_at: "2026-08-01T00:00:00Z" },
          { id: 2, weight_kg: 85.0, recorded_at: "2026-08-15T00:00:00Z" }
        ],
        summary: {
          current_weight: 85.0,
          starting_weight: 90.0,
          total_change_kg: -5.0,
          percentage_change: -5.5,
          trend: "losing",
          entries_count: 2,
          note: "A note"
        }
      })
    });

    render(<ProgressPage />);

    await waitFor(() => {
      expect(screen.getByText("85 kg")).toBeInTheDocument(); // in list
      expect(screen.getByText("Trending Down")).toBeInTheDocument(); // trend label
      expect(screen.getByText("A note")).toBeInTheDocument();
    });

    // Check chart (SVG) is present by checking aria-label
    expect(screen.getByLabelText("Weight Progress Chart")).toBeInTheDocument();
  });
});
