import { render, screen } from '@testing-library/react';
import { CitationsList, Citation } from '@/components/assistant/CitationsList';

describe('CitationsList', () => {
  it('renders nothing when citations array is empty', () => {
    const { container } = render(<CitationsList citations={[]} />);
    expect(container).toBeEmptyDOMElement();
  });

  it('renders citations correctly', () => {
    const citations: Citation[] = [
      {
        document_id: '1',
        title: 'Protein Guidelines',
        source_name: 'NIH',
        text_type: 'guideline'
      }
    ];
    
    render(<CitationsList citations={citations} />);
    
    expect(screen.getByText('Verified Sources')).toBeInTheDocument();
    expect(screen.getByText('Protein Guidelines')).toBeInTheDocument();
    expect(screen.getByText('NIH')).toBeInTheDocument();
  });

  it('renders citation with URL as a link', () => {
    const citations: Citation[] = [
      {
        document_id: '1',
        title: 'Protein Guidelines',
        source_name: 'NIH',
        source_url: 'https://example.com/nih',
        text_type: 'guideline'
      }
    ];
    
    render(<CitationsList citations={citations} />);
    
    const link = screen.getByRole('link');
    expect(link).toHaveAttribute('href', 'https://example.com/nih');
  });

  it('renders citation section and page', () => {
    const citations: Citation[] = [
      {
        document_id: '1',
        title: 'Protein Guidelines',
        source_name: 'NIH',
        section: 'Dietary Intake',
        page: '42',
        text_type: 'guideline'
      }
    ];
    
    render(<CitationsList citations={citations} />);
    
    expect(screen.getByText(/Sec: Dietary Intake/)).toBeInTheDocument();
    expect(screen.getByText(/Pg: 42/)).toBeInTheDocument();
  });
});
