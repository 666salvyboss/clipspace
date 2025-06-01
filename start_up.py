import os
import sys
import win32com.client

def add_to_startup():
    startup = os.path.join(os.getenv("APPDATA"), "Microsoft\\Windows\\Start Menu\\Programs\\Startup")
    shortcut_path = os.path.join(startup, "PyFlow.lnk")

    # Avoid recreating every time
    if os.path.exists(shortcut_path):
        print("[*] Startup shortcut already exists.")
        return

    shell = win32com.client.Dispatch("WScript.Shell")
    shortcut = shell.CreateShortCut(shortcut_path)
    shortcut.Targetpath = os.path.abspath(sys.executable)  # This works after PyInstaller
    shortcut.WorkingDirectory = os.path.dirname(shortcut.Targetpath)
    shortcut.IconLocation = shortcut.Targetpath
    shortcut.save()

    print(f"[+] Shortcut created at startup: {shortcut_path}")
