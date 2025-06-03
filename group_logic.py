from datetime import datetime

from PY_flow import hash_text, encrypt


import sqlite3
import hashlib
import re



def safe_table_name(raw_input: str) -> str:
    """
    Converts raw input into a sanitized, unique table name.
    """
    cleaned = raw_input.lower().strip()
    cleaned = re.sub(r'\W+', '_', cleaned)
    hash_suffix = hashlib.sha1(cleaned.encode()).hexdigest()[:8]
    return f"user_table_{cleaned}_{hash_suffix}"

def group_setup(user_input: str) -> str:
    """
    Safely creates a table based on user input without exposing to SQL injection.
    """
    table_name = safe_table_name(user_input)

    conn = sqlite3.connect('data_base.db')
    crsr = conn.cursor()
    crsr.execute(f'''DELETE FROM foo ''')
    crsr.execute(f"DELETE FROM sqlite_sequence WHERE name= 'foo'")

    #crsr.execute(f'''
     #   CREATE TABLE IF NOT EXISTS {table_name} (
      #      hash TEXT PRIMARY KEY,
       #     data BLOB NOT NULL,
        #    time_text TEXT NOT NULL
        #)
    #''')

    conn.commit()
    conn.close()

    return table_name

def grouped_pins():
    data = input('data: ')
    #print(group_setup(data))
    pin_hash = hash_text(data)
    encrypted = encrypt(data)
    now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    conn = sqlite3.connect('''data_base.db''')
    crsr = conn.cursor()
    crsr.execute("""
                    INSERT INTO pin_data (hash, pin, time_text)
                    VALUES (?, ?, ?)
                    ON CONFLICT(hash) DO UPDATE SET
                        pin = excluded.pin,
                        time_text = excluded.time_text;
                """, (pin_hash, encrypted, now))
    conn.commit()

if __name__ == '__main__':
    pass
   # grouped_pins()