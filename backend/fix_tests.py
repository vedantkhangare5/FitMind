import re
import glob

def fix_ask_calls():
    for f in glob.glob('tests/test_*.py'):
        with open(f, 'r') as file:
            content = file.read()
        
        # We want to replace agent.ask(...) or orchestrator.ask(...)
        # by inserting ', user_id=1' before the LAST closing parenthesis of the ask call.
        # But regex for nested parentheses is hard.
        # However, we know all ask calls look like:
        # agent.ask(AgentRequest(query="..."))
        # or orchestrator.ask(AgentRequest(...))
        # or chat_orchestrator.ask(chat_req)
        
        # A simpler way:
        new_content = re.sub(r'(\.ask\([^)]+\))(\))', r'\1, user_id=1\2', content)
        # Wait, if it's .ask(AgentRequest(...)), the first \) matches the end of AgentRequest.
        # So we want to replace `.ask(SOMETHING)` where SOMETHING doesn't contain `user_id=1`.
        
        lines = content.split('\n')
        new_lines = []
        for line in lines:
            if '.ask(' in line and 'user_id=1' not in line:
                # Find the last ')' in the line
                last_paren_idx = line.rfind(')')
                if last_paren_idx != -1:
                    line = line[:last_paren_idx] + ', user_id=1' + line[last_paren_idx:]
            new_lines.append(line)
            
        with open(f, 'w') as file:
            file.write('\n'.join(new_lines))

if __name__ == "__main__":
    fix_ask_calls()
