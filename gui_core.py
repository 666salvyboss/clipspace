import sqlite3
import threading
import keyboard
from cryptography.fernet import Fernet
from PY_flow import hash_text, decrypt

# === Encryption Key ===
key = b'62yvjjRaK0zdh_qg69vV6ULeNCXr-ieD1Z5P_7emj0M='
cipher = Fernet(key)


# === DB Utility ===
def query_db(query, params=(), fetch=True, commit=False):
    with sqlite3.connect('data_base.db') as conn:
        cursor = conn.cursor()
        cursor.execute(query, params)
        if commit:
            conn.commit()
        return cursor.fetchall() if fetch else cursor


# === CORE CLASS ===
class GuiCore:

    @staticmethod
    def check_exists(table, text):
        hashed = hash_text(text)
        rows = query_db(f"SELECT * FROM {table} WHERE hash = ?", (hashed,))
        return bool(rows)

    @staticmethod
    def delete_from_table(table, text):
        hashed = hash_text(text)
        query_db(f"DELETE FROM {table} WHERE hash = ?", (hashed,), fetch=False, commit=True)

    @staticmethod
    def show_history(table, label):
        col = 'copy' if table == 'copy_data' else 'pin'
        rows = query_db(f"SELECT {col}, time_text FROM {table} ORDER BY time_text DESC LIMIT 100")
        for content, time_text in rows:
            print(f"{label}{decrypt(content)} - {time_text}")


# === ACTIONS ===
def specific_paste():
    text = input("specific copy: ")
    exists = GuiCore.check_exists('copy_data', text)
    print("✔️ Found" if exists else f"❌ '{text}' not in database")

def specific_paste_pin():
    text = input("specific pin: ")
    exists = GuiCore.check_exists('pin_data', text)
    print("✔️ Found" if exists else f"❌ '{text}' not in database")

def delete_copy():
    text = input("delete this copy: ")
    GuiCore.delete_from_table('copy_data', text)
    print("✅ Copy deleted")

def delete_pin():
    text = input("delete this pin: ")
    GuiCore.delete_from_table('pin_data', text)
    print("✅ Pin deleted")

def show_copy_history():
    GuiCore.show_history('copy_data', 'COPY > ')

def show_pin_history():
    GuiCore.show_history('pin_data', 'PIN > ')


# === THREAD WRAPPER ===
def threaded(func):
    threading.Thread(target=func, daemon=True).start()


# === HOTKEYS ===
if __name__ == '__main__':
    keyboard.add_hotkey('ctrl+alt+u', lambda: threaded(specific_paste))          # Paste specific copy
    keyboard.add_hotkey('ctrl+alt+r', lambda: threaded(specific_paste_pin))      # Paste specific pin
    keyboard.add_hotkey('ctrl+alt+h', lambda: threaded(show_copy_history))       # Show copy history
    keyboard.add_hotkey('ctrl+alt+p', lambda: threaded(show_pin_history))        # Show pin history
    keyboard.add_hotkey('ctrl+alt+d', lambda: threaded(delete_copy))             # Delete specific copy
    keyboard.add_hotkey('ctrl+alt+f', lambda: threaded(delete_pin))              # Delete specific pin

    print("🔥 Clipboard Dominator running. Press CTRL+C to quit.")
    keyboard.wait()
