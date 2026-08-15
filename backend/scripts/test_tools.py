import os
import sys
import json
import logging
from pprint import pprint

# Ensure we can import app modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.tools import registry

# Configure logging to standard output for visibility
logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")

def main():
    print("FitMind Tool Developer CLI")
    print("--------------------------")
    print("Available tools:")
    for name in registry._tools.keys():
        print(f"  - {name}")
    print("\nType a JSON payload representing a Gemini function call.")
    print("Example: {\"name\": \"calculate_bmi\", \"args\": {\"weight_kg\": 70, \"height_cm\": 175}}")
    print("Press Ctrl+C to exit.\n")
    
    while True:
        try:
            user_input = input("Payload > ")
            if not user_input.strip():
                continue
                
            payload = json.loads(user_input)
            
            tool_name = payload.get("name")
            tool_args = payload.get("args", {})
            
            if not tool_name:
                print("Error: JSON must include a 'name' key.\n")
                continue
                
            print("\nExecuting...")
            result = registry.execute(name=tool_name, args=tool_args)
            
            print("\nResult Envelope:")
            print(json.dumps(result, indent=2))
            print("\n" + "="*40 + "\n")
            
        except KeyboardInterrupt:
            print("\nExiting.")
            break
        except json.JSONDecodeError:
            print("Error: Invalid JSON format.\n")
        except Exception as e:
            print(f"Unexpected error: {e}\n")

if __name__ == "__main__":
    main()
