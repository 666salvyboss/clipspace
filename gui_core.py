import sqlite3
import threading
from datetime import datetime

import keyboard
from cryptography.fernet import Fernet

from PY_flow import hash_text

key = b'62yvjjRaK0zdh_qg69vV6ULeNCXr-ieD1Z5P_7emj0M='
cipher = Fernet(key)

def encrypt(data: str) -> bytes:
    return cipher.encrypt(data.encode())

def decrypt(token: bytes) -> str:
    return cipher.decrypt(token).decode()

def group_setup():
    conn = sqlite3.connect('''data_base.db''')
    crsr= conn.cursor()
    crsr.execute('''CREATE TABLE IF NOT EXIST foo(
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    hash TEXT UNIQUE,
                    data BLOB NOT NULL
                    time_text TEXT NOT NULL''')

class GuiCore:
    @staticmethod
    def specific_paste():
        specific_copy = input("specfic copy: ")
        conn_a = sqlite3.connect('data_base.db')
        crsr_a = conn_a.cursor()
        crsr_a.execute('''SELECT * FROM copy_data''')
        rows_a = crsr_a.fetchall()
        for row_a in rows_a:
            check = decrypt(row_a[1])
            if check == specific_copy:
                return "check"
            elif check != specific_copy:
                return f"{specific_copy} a not found in Data-Base"
            else:
                return "NULL"
    @staticmethod
    def specific_paste_pin():
        specific_copy = input("specfic copy: ")
        conn_a = sqlite3.connect('data_base.db')
        crsr_a = conn_a.cursor()
        crsr_a.execute('''SELECT * FROM pin_data''')
        rows_a = crsr_a.fetchall()
        for row_a in rows_a:
            check = decrypt(row_a[1])
            if check == specific_copy:
                 return "check"
            elif check != specific_copy:
                return f"{specific_copy} a not found in Data-Base"
            else:
                return "NULL"
    @staticmethod
    def delete_copy():
        specific_copy = input("specfic copy: ")
        conn_a = sqlite3.connect('data_base.db')
        crsr_a = conn_a.cursor()
        crsr_a.execute('''SELECT * FROM copy_data''')
        rows_a = crsr_a.fetchall()
        for row_a in rows_a:
            check = decrypt(row_a[1])
            if check == specific_copy:
                crsr_a.execute('''DELETE FROM copy_data WHERE copy = ?''', (check,))
                conn_a.commit()
            elif check != specific_copy:
                return f"{specific_copy} a not found in Data-Base"
            else:
                return "NULL"
    @staticmethod
    def delete_specific_pin():
        specific_copy = input("specfic copy: ")
        conn_a = sqlite3.connect('data_base.db')
        crsr_a = conn_a.cursor()
        crsr_a.execute('''SELECT * FROM pin_data''')
        rows_a = crsr_a.fetchall()
        for row_a in rows_a:
            check = decrypt(row_a[1])
            if check == specific_copy:
                return "check"
            elif check != specific_copy:
                return f"{specific_copy} a not found in Data-Base"
            else:
                return "NULL"
    @staticmethod
    def grouped_pins():
        group_setup()
        data = input('data: ')
        pin_hash = hash_text(data)
        encrypted = encrypt(data)
        now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        conn = sqlite3.connect('''data_base.db''')
        crsr = conn.cursor()
        crsr.execute('''INSERT INTO foo (hash, data, time_text)
                        VALUES ( ?,?,?) ON CONFLICT(hash) DO UPDATE SET 
                        pin = excluded.pin
                        time_text = excluded.time_text''', (pin_hash, encrypted, now))
        conn.commit()
    @staticmethod
    def show_copy_history():
        conn = sqlite3.connect('''data_base.db''')
        crsr = conn.cursor()
        crsr.execute('''SELECT copy, time_text FROM copy_data
                        ORDER BY time_text DESC LIMIT 100''')
        rows = crsr.fetchall()
        return [(row[1], row[2]) for row in rows]
    @staticmethod
    def pin_history():
        conn = sqlite3.connect('''data_base.db''')
        crsr = conn.cursor()
        crsr.execute('''SELECT pin, time_text FROM copy_data
                                ORDER BY time_text DESC LIMIT 100''')
        rows = crsr.fetchall()
        return [(row[1], row[2]) for row in rows]





def threaded_specific_paste():
    threading.Thread(target=GuiCore.specific_paste, daemon=True).start()

def threaded_specific_pin_paste():
    threading.Thread(target=GuiCore.specific_paste_pin, daemon=True).start()

def threaded_grouped_pins():
    threading.Thread(target=GuiCore.grouped_pins, daemon=True).start()

def threaded_copy_history():
    threading.Thread(target=GuiCore.show_copy_history, daemon=True).start()


if __name__ == '__main__':
    keyboard.add_hotkey('ctrl+alt+u', threaded_specific_paste)  # Paste specific copied content
    keyboard.add_hotkey('ctrl+alt+r', threaded_specific_paste)  # Paste specific pinned content