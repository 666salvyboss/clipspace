import sqlite3
import threading


import keyboard
from cryptography.fernet import Fernet

from PY_flow import hash_text, decrypt

key = b'62yvjjRaK0zdh_qg69vV6ULeNCXr-ieD1Z5P_7emj0M='
cipher = Fernet(key)




class GuiCore:
    @staticmethod
    def specific_paste(specific_input):
        conn_a = sqlite3.connect('data_base.db')
        crsr_a = conn_a.cursor()
        check = hash_text(specific_input)
        crsr_a.execute('''SELECT * FROM copy_data WHERE hash = ?''', (check,))
        found = crsr_a.rowcount
        if found > 0:
            print("gone")
        else:
            return f"{specific_input} not in database"
        conn_a.close()


    @staticmethod
    def specific_paste_pin(specific_input):

        conn_a = sqlite3.connect('data_base.db')
        crsr_a = conn_a.cursor()
        check = hash_text(specific_input)
        crsr_a.execute('''SELECT * FROM pin_data WHERE hash = ?''', (check,))
        found = crsr_a.rowcount
        conn_a.commit()
        if found > 0:
            print("gone")
        else:
            print(f"{specific_input} not in database")
        conn_a.close()

    @staticmethod
    def delete_copy(specific_input):

        conn_a = sqlite3.connect('data_base.db')
        crsr_a = conn_a.cursor()
        check = hash_text(specific_input)
        crsr_a.execute('''DELETE  FROM copy_data WHERE hash = ?''', (check,))
        found = crsr_a.rowcount
        conn_a.commit()
        if found > 0:
            print("gone")
        else:
            print(f"{specific_input} not in database")
        conn_a.close()



    @staticmethod
    def delete_specific_pin(specific_input):

        conn_a = sqlite3.connect('data_base.db')
        crsr_a = conn_a.cursor()
        check = hash_text(specific_input)
        crsr_a.execute('''DELETE  FROM pin_data WHERE hash = ?''', (check,))
        found = crsr_a.rowcount
        conn_a.commit()
        if found > 0:
            print("gone")
        else:
            print(f"{specific_input} not in database")
        conn_a.close()

    @staticmethod
    def show_copy_history():
        conn = sqlite3.connect('data_base.db')
        crsr = conn.cursor()
        crsr.execute('''SELECT copy, time_text FROM copy_data
                        ORDER BY time_text DESC LIMIT 100''')
        rows = crsr.fetchall()
        conn.close()
        return [f"{decrypt(row[0])} - {row[1]}" for row in rows]

    @staticmethod
    def pin_history():
        conn = sqlite3.connect('data_base.db')
        crsr = conn.cursor()
        crsr.execute('''SELECT pin, time_text FROM pin_data
                        ORDER BY time_text DESC LIMIT 100''')
        rows = crsr.fetchall()
        conn.close()
        return [f"{decrypt(row[0])} - {row[1]}" for row in rows]




def threaded_specific_paste():
    threading.Thread(target=GuiCore.specific_paste, daemon=True).start()

def threaded_specific_pin_paste():
    threading.Thread(target=GuiCore.specific_paste_pin, daemon=True).start()


def threaded_copy_history():
    threading.Thread(target=GuiCore.show_copy_history, daemon=True).start()

def threaded_pin_history():
    threading.Thread(target=GuiCore.pin_history, daemon=True).start()



if __name__ == '__main__':
    keyboard.add_hotkey('ctrl+alt+u', threaded_specific_paste)  # Paste specific copied content
    keyboard.add_hotkey('ctrl+alt+r', threaded_specific_pin_paste)  # Paste specific pinned content
