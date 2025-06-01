import keyboard
from datetime import datetime
from cryptography.fernet import Fernet
import sqlite3
import pyperclip
import time
import gc
import threading
import hashlib

# === Encryption Key Setup ===
key = b'62yvjjRaK0zdh_qg69vV6ULeNCXr-ieD1Z5P_7emj0M='  # Your consistent key
cipher = Fernet(key)

def encrypt(data: str) -> bytes:
    """Encrypt the clipboard content before storage."""
    return cipher.encrypt(data.encode())

def decrypt(token: bytes) -> str:
    """Decrypt stored content before pasting."""
    return cipher.decrypt(token).decode()

def hash_text(text: str) -> str:
    """Generate SHA-256 hash of clipboard data for uniqueness in pinning."""
    return hashlib.sha256(text.encode()).hexdigest()

# === Database Setup ===
def setup_db():
    conn = sqlite3.connect('data_base.db')
    crsr = conn.cursor()

    crsr.execute('''CREATE TABLE IF NOT EXISTS copy_data(
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    copy BLOB NOT NULL,
                    time_text TEXT NOT NULL )''')

    # Unique hash for deduplication logic
    crsr.execute('''CREATE TABLE IF NOT EXISTS pin_data(
                    hash TEXT PRIMARY KEY,
                    pin BLOB NOT NULL,
                    time_text TEXT NOT NULL )''')

    conn.commit()
    conn.close()

setup_db()

# === Core PyFlow Logic ===
class PYFLOW:

    @staticmethod
    def copy():
        """Continuously monitor clipboard and save new copied items."""
        last = ""
        while True:
            try:
                current = pyperclip.paste()
                if current and current != last:
                    conn = sqlite3.connect('data_base.db')
                    crsr = conn.cursor()
                    now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                    encrypted = encrypt(current)
                    crsr.execute('INSERT INTO copy_data (copy, time_text) VALUES (?, ?)', (encrypted, now))
                    conn.commit()
                    conn.close()
                    print(f"[+] Copied and stored at {now}")
                    last = current
            except Exception as e:
                print("Error in copy:", e)
            time.sleep(0.5)

    @staticmethod
    def pin():
        """Pin current clipboard content with conflict resolution."""
        try:
            keyboard.press_and_release('ctrl+c')
            time.sleep(0.2)  # Let clipboard update
            data = pyperclip.paste()

            if not data.strip():
                print("[!] Clipboard is empty or whitespace.")
                return

            pin_hash = hash_text(data)
            encrypted = encrypt(data)
            now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

            conn = sqlite3.connect('data_base.db')
            crsr = conn.cursor()

            # Insert or replace if already pinned (deduplication)
            crsr.execute("""
                INSERT INTO pin_data (hash, pin, time_text)
                VALUES (?, ?, ?)
                ON CONFLICT(hash) DO UPDATE SET
                    pin = excluded.pin,
                    time_text = excluded.time_text;
            """, (pin_hash, encrypted, now))

            conn.commit()
            conn.close()
            print(f"[+] Pinned (inserted/updated) clipboard content at {now}")

        except Exception as e:
            print("Error in pin:", e)

    @staticmethod
    def paste_pin():
        """Paste most recent pinned item from storage."""
        try:
            conn = sqlite3.connect('data_base.db')
            crsr = conn.cursor()
            crsr.execute('SELECT pin FROM pin_data ORDER BY time_text DESC LIMIT 1')
            row = crsr.fetchone()
            if row:
                decrypted = decrypt(row[0])
                pyperclip.copy(decrypted)
                timeout = 5
                start = time.time()
                while time.time() - start < timeout:
                    keyboard.press_and_release('ctrl+v')
                    del decrypted
                    gc.collect()
                    print("[+] Pasted pinned content")
                    time.sleep(0.05)
                    break
            else:
                print("[-] No pinned content found.")
            conn.close()
        except Exception as e:
            print("Error in paste_pin:", e)

# === Threaded Execution Wrappers ===
def threaded_pin():
    threading.Thread(target=PYFLOW.pin, daemon=True).start()

def threaded_paste_pin():
    threading.Thread(target=PYFLOW.paste_pin, daemon=True).start()

# === Hotkeys Setup ===
keyboard.add_hotkey('ctrl+.', threaded_pin)        # Pin clipboard content
keyboard.add_hotkey('ctrl+/', threaded_paste_pin)  # Paste pinned content

print("🟢 PyFlow Active: (Pin = Ctrl+.) | (PastePin = Ctrl+/)")
keyboard.wait()
