import { render, screen } from '@testing-library/react';
import { ToolActivity, ToolCallRecord } from '@/components/assistant/ToolActivity';

describe('ToolActivity', () => {
  it('renders nothing when there are no tool calls', () => {
    const { container } = render(<ToolActivity toolCalls={[]} />);
    expect(container).toBeEmptyDOMElement();
  });

  it('renders search knowledge correctly', () => {
    const toolCalls: ToolCallRecord[] = [
      { tool_name: 'search_knowledge', status: 'success' }
    ];
    
    render(<ToolActivity toolCalls={toolCalls} />);
    expect(screen.getByText('✓ Knowledge search')).toBeInTheDocument();
  });

  it('renders calculation correctly', () => {
    const toolCalls: ToolCallRecord[] = [
      { tool_name: 'calculate_tdee', status: 'success' }
    ];
    
    render(<ToolActivity toolCalls={toolCalls} />);
    expect(screen.getByText('✓ Fitness calculation')).toBeInTheDocument();
  });

  it('renders validation correctly', () => {
    const toolCalls: ToolCallRecord[] = [
      { tool_name: 'validate_calorie_target', status: 'success' }
    ];
    
    render(<ToolActivity toolCalls={toolCalls} />);
    expect(screen.getByText('✓ Calorie safety check')).toBeInTheDocument();
  });

  it('renders error status correctly', () => {
    const toolCalls: ToolCallRecord[] = [
      { tool_name: 'calculate_tdee', status: 'error' }
    ];
    
    render(<ToolActivity toolCalls={toolCalls} />);
    expect(screen.getByText('✗ Fitness calculation')).toBeInTheDocument();
  });

  it('renders error if result object has success=false', () => {
    const toolCalls: ToolCallRecord[] = [
      { 
        tool_name: 'calculate_tdee', 
        status: 'success', // HTTP/agent layer might say success, but tool failed
        result: { success: false, error: 'invalid' } 
      }
    ];
    
    render(<ToolActivity toolCalls={toolCalls} />);
    expect(screen.getByText('✗ Fitness calculation')).toBeInTheDocument();
  });
});
