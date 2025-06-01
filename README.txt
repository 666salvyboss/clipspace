# PyFlow Clipboard Manager

🟢 Clipboard logging and pinning tool with encryption, hotkeys, and persistence.

## 🔥 Hotkeys
- **Ctrl + .** → Pin clipboard
- **Ctrl + Shift + /** → Paste latest pinned item

## 📦 Features
- Stores every copy automatically
- Lets you pin important snippets
- Encrypts stored data
- Saves pinned content to a local DB
- Runs at system startup (once first run is complete)

## 📁 Folder Structure (after build)
- `PyFlow.exe` — main executable
- `data_base.db` — local storage (auto-generated)
- `PyFlow_Build.zip` — packaged build
- `README.txt` — you’re reading this

## 💡 How to Use
1. Run `PyFlow.exe` once.
2. It adds itself to startup.
3. Use the hotkeys, forget the rest.

## ⚠️ Notes
- Requires admin rights **only on first run** if installing startup shortcut.
- Avoid sharing `data_base.db` if sensitive content is stored.

