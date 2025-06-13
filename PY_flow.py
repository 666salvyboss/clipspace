import subprocess

import keyboard
from datetime import datetime
from cryptography.fernet import Fernet
import sqlite3
import pyperclip
import time
import threading
import hashlib
import os
import platform
from PIL import ImageGrab, Image
import io
import pyautogui
import gc
__version__ = '1.0.0'
# ======= MACHINE AUTH CHECK =======
def get_machine_hash():
    data = platform.node() + platform.machine() + platform.processor()
    return hashlib.sha256(data.encode()).hexdigest()

ALLOWED_HASH = get_machine_hash()

if get_machine_hash() != ALLOWED_HASH:
    print("❌ Unauthorized machine. Access denied.")
    exit()

# ======= ENCRYPTION SETUP =======
KEY = b'62yvjjRaK0zdh_qg69vV6ULeNCXr-ieD1Z5P_7emj0M='
cipher = Fernet(KEY)

def encrypt(data: bytes) -> bytes:
    return cipher.encrypt(data)

def decrypt(token: bytes) -> bytes:
    return cipher.decrypt(token)

def hash_text(text: str) -> str:
    # Hash only first 200 chars for performance, binary safe
    return hashlib.sha256(text.encode()).hexdigest()

# ======= DATABASE SETUP =======
DB_PATH = 'data_base.db'

def setup_db():
    with sqlite3.connect(DB_PATH) as conn:
        c = conn.cursor()
        c.execute('''
            CREATE TABLE IF NOT EXISTS copy_data(
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                hash TEXT UNIQUE,
                copy BLOB NOT NULL,
                time_text TEXT NOT NULL,
                is_image INTEGER DEFAULT 0
            )
        ''')
        c.execute('''
            CREATE TABLE IF NOT EXISTS pin_data(
                hash TEXT PRIMARY KEY,
                pin BLOB NOT NULL,
                time_text TEXT NOT NULL,
                is_image INTEGER DEFAULT 0
            )
        ''')
        conn.commit()

setup_db()

# ======= CORE PYFLOW CLASS =======
class PYFLOW:
    @staticmethod
    def copy():
        """Continuously monitor clipboard for new text or images, encrypt & save."""
        last = None
        while True:
            try:
                img = ImageGrab.grabclipboard()
                text = pyperclip.paste()

                is_image = isinstance(img, Image.Image)
                current = img if is_image else text

                if current and current != last:
                    now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                    data_hash = hash_text(str(current)[:200])
                    is_img_flag = 1 if is_image else 0

                    if is_image:
                        buf = io.BytesIO()
                        img.save(buf, format='PNG')
                        encrypted = encrypt(buf.getvalue())
                    else:
                        encrypted = encrypt(current.encode())

                    with sqlite3.connect(DB_PATH) as conn:
                        c = conn.cursor()
                        c.execute('''
                            INSERT INTO copy_data(hash, copy, time_text, is_image)
                            VALUES (?, ?, ?, ?)
                            ON CONFLICT(hash) DO UPDATE SET
                                copy=excluded.copy,
                                time_text=excluded.time_text,
                                is_image=excluded.is_image
                        ''', (data_hash, encrypted, now, is_img_flag))
                        conn.commit()

                    print(f"[+] Copied {'image' if is_image else 'text'} at {now}")
                    last = current

            except Exception as e:
                print(f"Error in copy: {e}")
            time.sleep(0.5)

    @staticmethod
    def pin():
        """Pin current clipboard content, encrypt & save with deduplication."""
        try:
            keyboard.press_and_release('ctrl+c')
            time.sleep(0.3)  # clipboard catch-up

            img = ImageGrab.grabclipboard()
            text = pyperclip.paste()

            is_image = isinstance(img, Image.Image)
            data = img if is_image else text

            if not data:
                print("[!] Clipboard empty, cannot pin.")
                return

            pin_hash = hash_text(str(data)[:200])
            now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            is_img_flag = 1 if is_image else 0

            if is_image:
                buf = io.BytesIO()
                img.save(buf, format='PNG')
                encrypted = encrypt(buf.getvalue())
            else:
                encrypted = encrypt(data.encode())

            with sqlite3.connect(DB_PATH) as conn:
                c = conn.cursor()
                c.execute('''
                    INSERT INTO pin_data(hash, pin, time_text, is_image)
                    VALUES (?, ?, ?, ?)
                    ON CONFLICT(hash) DO UPDATE SET
                        pin=excluded.pin,
                        time_text=excluded.time_text,
                        is_image=excluded.is_image
                ''', (pin_hash, encrypted, now, is_img_flag))
                conn.commit()

            print(f"[+] Pinned {'image' if is_image else 'text'} at {now}")

        except Exception as e:
            print(f"Error in pin: {e}")

    @staticmethod
    def paste_pin():
        """Paste latest pinned content: decrypt & paste, fallback on write."""
        try:
            with sqlite3.connect(DB_PATH) as conn:
                c = conn.cursor()
                c.execute('SELECT pin, is_image FROM pin_data ORDER BY time_text DESC LIMIT 1')
                row = c.fetchone()

            if not row:
                print("[-] No pinned content found.")
                return

            encrypted_data, is_image = row
            decrypted = decrypt(encrypted_data)

            if is_image:
                temp_path = "temp_clip.png"
                with open(temp_path, 'wb') as f:
                    f.write(decrypted)
                print("[*] Temp image saved.")

                # Open with default image viewer
                subprocess.Popen(['start', '', temp_path], shell=True)

                time.sleep(0.6)  # Give it time to open

                pyautogui.hotkey('ctrl', 'v')
                print("[+] Simulated Ctrl+V")

                time.sleep(0.5)  # Let it breathe before killing

                # Brutally close it — MVP style (Windows only)
                os.system('taskkill /f /im dllhost.exe >nul 2>&1')  # Most image viewers in Windows use dllhost


            else:
                text = decrypted.decode()
                pyperclip.copy(text)
                time.sleep(0.1)
                try:
                    keyboard.press_and_release('ctrl+v')
                    print("[+] Simulated Ctrl+V")
                    time.sleep(0.2)
                except Exception:
                    print("[!] Ctrl+V failed, fallback to keyboard.write()")
                    keyboard.write(text)
                del text
                gc.collect()

        except Exception as e:
            print(f"Error in paste_pin: {e}")
    @staticmethod
    def emergency_paste():
        content = pyperclip.paste()
        if not content:
            if keyboard.is_pressed('ctrl') and keyboard.is_pressed('v'):
                conn = sqlite3.connect("data_base.db")
                crsr = conn.cursor()
                crsr.execute('''SELECT copy FROM copy_data ORDER BY time_text DESC LIMIT 1''')
                row = crsr.fetchone()
                if row:
                   decrypted_text = decrypt(row[0])
                   pyperclip.copy(decrypted_text)




# ======= THREADS & HOTKEYS =======
def run_copy_thread():
    threading.Thread(target=PYFLOW.copy, daemon=True).start()

def run_pin_thread():
    threading.Thread(target=PYFLOW.pin, daemon=True).start()

def cooldown_decorator(func, cooldown=0.8):
    last_time = [0]

    def wrapper():
        now = time.time()
        if now - last_time[0] >= cooldown:
            last_time[0] = now
            threading.Thread(target=func, daemon=True).start()
        else:
            print("[!] Cooldown active — skipping call")
    return wrapper

if __name__ == '__main__':
    r = PYFLOW()
    r.emergency_paste()
    run_copy_thread()
    keyboard.add_hotkey('ctrl+.', run_pin_thread)
    keyboard.add_hotkey('ctrl+shift+/', cooldown_decorator(PYFLOW.paste_pin))

    def async_setup():
        from zipper import zip_exe
        from start_up import add_to_startup
        try:
            zip_exe()
            add_to_startup()
            print("\n📦 Zipped and startup shortcuts added.")
        except Exception as e:
            print(f"⚠️ Setup Error: {e}")

    threading.Thread(target=async_setup, daemon=True).start()

    print("🟢 PyFlow Loaded | (Pin = Ctrl+.) | (Paste = Ctrl+Shift+/)")
    keyboard.wait()
