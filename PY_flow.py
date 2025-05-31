import keyboard
from datetime import datetime
from cryptography.fernet import Fernet
import sqlite3
import pyperclip
import time
import gc

# Generate or load your key (DON'T regenerate every time in production)
key = b'62yvjjRaK0zdh_qg69vV6ULeNCXr-ieD1Z5P_7emj0M='  # Replace with loading from file for real usage
cipher = Fernet(key)
print(key)
def encrypt(data: str) -> bytes:
    return cipher.encrypt(data.encode())

def decrypt(token: bytes) -> str:
    return cipher.decrypt(token).decode()

# Database setup
conn = sqlite3.connect('data_base.db')
crsr = conn.cursor()
crsr_2 = conn.cursor()
crsr.execute('''CREATE TABLE IF NOT EXISTS copy_data(
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                copy BLOB NOT NULL,
                time_text NOT NULL )''')
crsr_2.execute('''CREATE TABLE IF NOT EXISTS pin_data(
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                pin BLOB NOT NULL,
                time_text NOT NULL )''')
conn.commit()
conn.close()

# Core logic
class PYFLOW:
    @staticmethod
    def copy():
        last = ""
        while True:
            try:
                current = pyperclip.paste()
                if current and current != last:
                    conn_1 = sqlite3.connect('data_base.db')
                    crsr_1 = conn_1.cursor()
                    now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                    encrypted = encrypt(current)
                    crsr_1.execute('INSERT INTO copy_data (copy, time_text) VALUES (?, ?)', (encrypted, now))
                    conn.commit()
                    print(f"[+] Copied and stored at {now}")
                    last = current
                    conn_1.close()

            except Exception as e:
                print("Error:", e)
            time.sleep(0.5)  # Adjust for responsiveness vs performance


    @staticmethod
    def pin():
        conn_3= sqlite3.connect('data_base.db')
        crsr_3 = conn_3.cursor()
        now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        keyboard.press_and_release('ctrl+c')
        time.sleep(0.1)  # let clipboard update
        data_to_encrypt = pyperclip.paste()
        encrypted = encrypt(data_to_encrypt)
        crsr_3.execute('INSERT INTO pin_data (pin, time_text) VALUES (?, ?)', (encrypted, now))
        conn_3.commit()

    @staticmethod
    def paste_pin():  # ctrl + u
        conn_4 = sqlite3.connect('data_base.db')
        crsr_4 = conn_4.cursor()
        crsr_4.execute('SELECT pin FROM pin_data ORDER BY time_text DESC LIMIT 1')
        row = crsr_4.fetchone()
        if row:
            decrypted = decrypt(row[0])
            pyperclip.copy(decrypted)
            keyboard.press_and_release('ctrl+v')
            del decrypted
            gc.collect()
        conn_4.close()
# Hotkeys
keyboard.add_hotkey('ctrl+.', PYFLOW.pin)
keyboard.add_hotkey('alt+/', PYFLOW.paste_pin)
keyboard.wait()
print("🟢 PyFlow Module 1: Listening... (Copy=Ctrl+Shift+C | Pin=Ctrl+Shift+P | PastePin=Ctrl+Shift+U)")
keyboard.wait()
