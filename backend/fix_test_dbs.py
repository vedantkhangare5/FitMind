import glob
import re

def fix():
    for f in glob.glob('tests/test_*.py'):
        with open(f, 'r') as file:
            content = file.read()
        
        # Replace conn.execute(CREATE_PROFILE_TABLE) etc. with init_db(db_path)
        # and insert user 1
        new_content = re.sub(
            r'conn = get_connection\([^)]*\)\s*conn\.execute\(CREATE_PROFILE_TABLE\)\s*conn\.execute\(CREATE_PROGRESS_TABLE\)\s*conn\.commit\(\)\s*conn\.close\(\)',
            r'''from app.database import init_db
        init_db(db_path)
        conn = get_connection(db_path)
        conn.execute("INSERT OR IGNORE INTO users (id, email, hashed_password, created_at) VALUES (1, 'test', '!', 'now')")
        conn.commit()
        conn.close()''',
            content
        )
        
        with open(f, 'w') as file:
            file.write(new_content)

if __name__ == '__main__':
    fix()
