import keyboard
from datetime import datetime
from cryptography.fernet import Fernet
import sqlite3
import pyperclip
import time
import gc
import threading
import hashlib
import os


# === Encryption Key Setup ===
key = b'62yvjjRaK0zdh_qg69vV6ULeNCXr-ieD1Z5P_7emj0M='
cipher = Fernet(key)

def encrypt(data: str) -> bytes:
    return cipher.encrypt(data.encode())

def decrypt(token: bytes) -> str:
    return cipher.decrypt(token).decode()

def hash_text(text: str) -> str:
    return hashlib.sha256(text.encode()).hexdigest()

# === Database Setup ===
def setup_db():
    conn = sqlite3.connect('data_base.db')
    crsr = conn.cursor()

    crsr.execute('''CREATE TABLE IF NOT EXISTS copy_data(
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    copy BLOB NOT NULL,
                    time_text TEXT NOT NULL )''')

    crsr.execute('''CREATE TABLE IF NOT EXISTS pin_data(
                    hash TEXT PRIMARY KEY,
                    pin BLOB NOT NULL,
                    time_text TEXT NOT NULL )''')

    conn.commit()
    conn.close()

setup_db()

# === Core Class ===
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
        """Pin clipboard content with deduplication and file-path resolution."""
        try:
            keyboard.press_and_release('ctrl+c')
            time.sleep(0.3)  # let clipboard catch up

            data = pyperclip.paste()
            if not data.strip():
                print("[!] Clipboard is empty.")
                return

            # 🧠 Check if PyCharm gave us a file path
            if os.path.exists(data) and os.path.isfile(data):
                print("[*] Clipboard contains file path, reading file contents.")
                with open(data, 'r', encoding='utf-8', errors='ignore') as f:
                    data = f.read()

            print(f"[DEBUG] Pinning data:\n{data[:100]}..." + ("..." if len(data) > 100 else ""))

            pin_hash = hash_text(data)
            encrypted = encrypt(data)
            now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

            conn = sqlite3.connect('data_base.db')
            crsr = conn.cursor()
            crsr.execute("""
                INSERT INTO pin_data (hash, pin, time_text)
                VALUES (?, ?, ?)
                ON CONFLICT(hash) DO UPDATE SET
                    pin = excluded.pin,
                    time_text = excluded.time_text;
            """, (pin_hash, encrypted, now))

            conn.commit()
            conn.close()
            print(f"[+] Pinned clipboard content at {now}")

        except Exception as e:
            print("Error in pin:", e)

    @staticmethod
    def paste_pin():
        """Paste most recent pinned content, fallback to keyboard.write() if Ctrl+V fails."""
        try:
            conn = sqlite3.connect('data_base.db')
            crsr = conn.cursor()
            crsr.execute('SELECT pin FROM pin_data ORDER BY time_text DESC LIMIT 1')
            row = crsr.fetchone()
            conn.close()

            if row:
                decrypted = decrypt(row[0])
                print(f"[DEBUG] Pasting pinned content:\n{decrypted[:100]}..." + ("..." if len(decrypted) > 100 else ""))

                pyperclip.copy(decrypted)
                time.sleep(0.1)

                try:
                    keyboard.press_and_release('ctrl+v')
                    print("[+] Simulated Ctrl+V")
                except:
                    print("[!] Ctrl+V failed, using keyboard.write()")
                    keyboard.write(decrypted)

                del decrypted
                gc.collect()
            else:
                print("[-] No pinned content found.")

        except Exception as e:
            print("Error in paste_pin:", e)

# === Threads ===
def threaded_pin():
    threading.Thread(target=PYFLOW.pin, daemon=True).start()

def threaded_paste_pin():
    threading.Thread(target=PYFLOW.paste_pin, daemon=True).start()

# === HOTKEYS (normal user-friendly combos) ===
keyboard.add_hotkey('ctrl+.', threaded_pin)        # Pin clipboard content
keyboard.add_hotkey('ctrl+shift+/', threaded_paste_pin)  # Paste pinned content
from zipper import zip_exe
zip_exe()
from start_up import add_to_startup
add_to_startup()


print("🟢 PyFlow Loaded | (Pin = Ctrl+.) | (Paste = Ctrl+shift+/)")
keyboard.wait()
