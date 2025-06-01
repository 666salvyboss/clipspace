import keyboard
from datetime import datetime
from cryptography.fernet import Fernet
import sqlite3
import pyperclip
import time
import gc
import threading

# === Encryption setup ===
key = b'62yvjjRaK0zdh_qg69vV6ULeNCXr-ieD1Z5P_7emj0M='  # Use your key here
cipher = Fernet(key)

def encrypt(data: str) -> bytes:
    return cipher.encrypt(data.encode())

def decrypt(token: bytes) -> str:
    return cipher.decrypt(token).decode()

# === Database setup ===
def setup_db():
    conn = sqlite3.connect('data_base.db')
    crsr = conn.cursor()
    crsr.execute('''CREATE TABLE IF NOT EXISTS copy_data(
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    copy BLOB NOT NULL,
                    time_text TEXT NOT NULL )''')
    crsr.execute('''CREATE TABLE IF NOT EXISTS pin_data(
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    pin BLOB NOT NULL,
                    time_text TEXT NOT NULL )''')
    conn.commit()
    conn.close()

setup_db()

# === Core logic ===
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
                    conn_1.commit()
                    conn_1.close()
                    print(f"[+] Copied and stored at {now}")
                    last = current
            except Exception as e:
                print("Error in copy:", e)
            time.sleep(0.5)

    @staticmethod
    def pin():
        try:
            keyboard.press_and_release('ctrl+c')
            timeout = 5  # seconds
            start = time.time()
            while time.time() - start < timeout:
                conn_3 = sqlite3.connect('data_base.db')
                crsr_3 = conn_3.cursor()
                now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                data_to_encrypt = pyperclip.paste()
                encrypted = encrypt(data_to_encrypt)
                crsr_3.execute('INSERT INTO pin_data (pin, time_text) VALUES (?, ?)', (encrypted, now))
                conn_3.commit()
                conn_3.close()
                print(f"[+] Pinned clipboard content at {now}")
                time.sleep(0.05)  # check every 50ms
                break
        except Exception as e:
            print("Error in pin:", e)

    @staticmethod
    def paste_pin():
        try:
            conn_4 = sqlite3.connect('data_base.db')
            crsr_4 = conn_4.cursor()
            crsr_4.execute('SELECT pin FROM pin_data ORDER BY time_text DESC LIMIT 1')
            row = crsr_4.fetchone()
            if row:
                decrypted = decrypt(row[0])
                pyperclip.copy(decrypted)
                #time.sleep(0.3)
                timeout = 5  # seconds
                start = time.time()
                while time.time() - start < timeout:
                    keyboard.press_and_release('ctrl+v')
                    del decrypted
                    gc.collect()
                    print("[+] Pasted pinned content")
                    time.sleep(0.05)  # check every 50ms
                    break
            else:
                print("No pinned content found.")
            conn_4.close()
        except Exception as e:
            print("Error in paste_pin:", e)

# === Main execution ===
# Hotkeys
# === Threaded Execution Wrappers ===
#import threading

def threaded_pin():
    threading.Thread(target=PYFLOW.pin, daemon=True).start()

def threaded_paste_pin():
    threading.Thread(target=PYFLOW.paste_pin, daemon=True).start()

# Hotkeys
keyboard.add_hotkey('ctrl+.', threaded_pin)        # Pin clipboard content
keyboard.add_hotkey('ctrl+/', threaded_paste_pin)  # Paste pinned content

print("🟢 PyFlow Module: Listening for hotkeys (Pin=Ctrl+. | PastePin=Ctrl+/)")
keyboard.wait()
