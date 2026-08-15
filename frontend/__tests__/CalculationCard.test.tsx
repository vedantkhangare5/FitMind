import { render, screen } from '@testing-library/react';
import { CalculationCard } from '@/components/assistant/CalculationCard';
import { ToolCallRecord } from '@/components/assistant/ToolActivity';

describe('CalculationCard', () => {
  it('renders nothing when there are no tool calls', () => {
    const { container } = render(<CalculationCard toolCalls={[]} />);
    expect(container).toBeEmptyDOMElement();
  });

  it('renders nothing when tool calls have no calculations', () => {
    const toolCalls: ToolCallRecord[] = [
      {
        tool_name: 'search_knowledge',
        status: 'success',
        result: { success: true, data: { message: 'Knowledge retrieved' } }
      }
    ];
    const { container } = render(<CalculationCard toolCalls={toolCalls} />);
    expect(container).toBeEmptyDOMElement();
  });

  it('renders BMR and TDEE correctly', () => {
    const toolCalls: ToolCallRecord[] = [
      {
        tool_name: 'calculate_tdee',
        status: 'success',
        result: {
          success: true,
          data: { bmr: 1800, tdee: 2500 }
        }
      }
    ];
    
    render(<CalculationCard toolCalls={toolCalls} />);
    
    expect(screen.getByText('BMR')).toBeInTheDocument();
    expect(screen.getByText('1800')).toBeInTheDocument();
    
    expect(screen.getByText('TDEE')).toBeInTheDocument();
    expect(screen.getByText('2500')).toBeInTheDocument();
  });

  it('renders protein targets correctly', () => {
    const toolCalls: ToolCallRecord[] = [
      {
        tool_name: 'calculate_protein_target',
        status: 'success',
        result: {
          success: true,
          data: { protein_target_min: 120, protein_target_max: 160 }
        }
      }
    ];
    
    render(<CalculationCard toolCalls={toolCalls} />);
    
    expect(screen.getByText('Protein Target')).toBeInTheDocument();
    expect(screen.getByText('120 - 160')).toBeInTheDocument();
  });

  it('renders safety warnings correctly', () => {
    const toolCalls: ToolCallRecord[] = [
      {
        tool_name: 'validate_calorie_target',
        status: 'success',
        result: {
          success: true,
          data: { warnings: ['Aggressive deficit warning', 'Low protein warning'] }
        }
      }
    ];
    
    render(<CalculationCard toolCalls={toolCalls} />);
    
    expect(screen.getByText('Safety Notice')).toBeInTheDocument();
    expect(screen.getByText('Aggressive deficit warning')).toBeInTheDocument();
    expect(screen.getByText('Low protein warning')).toBeInTheDocument();
  });
});
