import { render, screen, waitFor } from '@testing-library/react';
import { DashboardBehavior } from '../src/components/dashboard/DashboardBehavior';
import { api } from '../src/lib/api';

jest.mock('../src/lib/api');

const mockedApi = api as jest.Mocked<typeof api>;

describe('DashboardBehavior', () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  it('renders loading state initially', () => {
    mockedApi.getBehaviorSummary.mockImplementation(() => new Promise(() => {}));
    const { container } = render(<DashboardBehavior />);
    expect(container.querySelector('.animate-spin')).toBeInTheDocument();
  });

  it('renders error state on API failure', async () => {
    mockedApi.getBehaviorSummary.mockRejectedValue(new Error('Failed to fetch'));
    render(<DashboardBehavior />);
    
    await waitFor(() => {
      expect(screen.getByText('Failed to fetch')).toBeInTheDocument();
    });
  });

  it('renders data correctly', async () => {
    mockedApi.getBehaviorSummary.mockResolvedValue({
      nutrition: {
        average_calories: 2000,
        average_protein: 150,
        adherence: 'High'
      },
      workouts: {
        total_minutes: 120,
        completed_workouts: 3
      },
      days_covered: 7
    });

    render(<DashboardBehavior />);
    
    await waitFor(() => {
      expect(screen.getByText('High')).toBeInTheDocument();
      expect(screen.getByText('2000')).toBeInTheDocument();
      expect(screen.getByText('150')).toBeInTheDocument();
      expect(screen.getByText('3')).toBeInTheDocument();
      expect(screen.getByText('120')).toBeInTheDocument();
    });
  });
});
