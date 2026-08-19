import { render, screen, waitFor } from '@testing-library/react';
import { DashboardProgress } from '../src/components/dashboard/DashboardProgress';
import { api } from '../src/lib/api';

jest.mock('../src/lib/api');

const mockedApi = api as jest.Mocked<typeof api>;

describe('DashboardProgress', () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  it('renders loading state initially', () => {
    mockedApi.getProgressSummary.mockImplementation(() => new Promise(() => {}));
    const { container } = render(<DashboardProgress />);
    expect(container.querySelector('.animate-spin')).toBeInTheDocument();
  });

  it('renders error state on API failure', async () => {
    mockedApi.getProgressSummary.mockRejectedValue(new Error('Failed to fetch'));
    render(<DashboardProgress />);
    
    await waitFor(() => {
      expect(screen.getByText('Failed to fetch')).toBeInTheDocument();
    });
  });

  it('renders data correctly', async () => {
    mockedApi.getProgressSummary.mockResolvedValue({
      current_weight: 80,
      starting_weight: 82,
      total_change_kg: -2,
      percentage_change: -2.4,
      trend: 'losing_weight',
      entries_count: 5,
      note: 'Good job'
    });

    render(<DashboardProgress />);
    
    await waitFor(() => {
      expect(screen.getByText('losing weight')).toBeInTheDocument();
      expect(screen.getByText('80')).toBeInTheDocument();
      expect(screen.getByText('-2')).toBeInTheDocument();
      expect(screen.getByText('Good job')).toBeInTheDocument();
    });
  });
});
