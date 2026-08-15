import os
import sys
import logging
from pprint import pprint

# Ensure we can import app modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.schemas.agent import AgentRequest
from app.agent.orchestrator import AgentOrchestrator

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")

def main():
    print("FitMind Agent CLI")
    print("-----------------")
    print("Type a natural language query for the agent.")
    print("Press Ctrl+C to exit.\n")
    
    # Initialize the orchestrator once
    # Ensure GEMINI_API_KEY is in your environment
    try:
        orchestrator = AgentOrchestrator()
    except Exception as e:
        print(f"Failed to initialize AgentOrchestrator: {e}")
        print("Make sure GEMINI_API_KEY is set in your environment.")
        return

    while True:
        try:
            query = input("User > ")
            if not query.strip():
                continue
                
            request = AgentRequest(query=query)
            print("\nThinking...")
            
            response = orchestrator.ask(request)
            
            print("\n=== AGENT RESPONSE ===")
            print(f"Answer: {response.answer}")
            print(f"Tool Calls: {len(response.tool_calls)}")
            for tc in response.tool_calls:
                print(f"  - {tc.tool_name} ({tc.status})")
            print(f"Citations: {len(response.citations)}")
            for c in response.citations:
                print(f"  - [{c.document_id}] {c.title}")
            print(f"Grounded: {response.grounded}")
            print(f"Insufficient Context: {response.insufficient_context}")
            print(f"Generation Error: {response.generation_error}")
            if response.error_code:
                print(f"Error Code: {response.error_code}")
            print("======================\n")
            
        except KeyboardInterrupt:
            print("\nExiting.")
            break
        except Exception as e:
            print(f"Unexpected error: {e}\n")

if __name__ == "__main__":
    main()
