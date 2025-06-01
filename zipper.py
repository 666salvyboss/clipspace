import os
import zipfile

def zip_exe():
    dist_path = r'C:\Users\USER\PY_FLOW\dist'
    desktop_path = os.path.join(os.path.expanduser("~"), "Desktop", "PyFlow_Builds")
    os.makedirs(desktop_path, exist_ok=True)

    output_zip = os.path.join(desktop_path, 'PyFlow_Build.zip')

    if os.path.exists(output_zip):
        try:
            os.remove(output_zip)
        except PermissionError:
            print("🚫 File is locked or in use. Close it and try again.")
            return

    try:
        with zipfile.ZipFile(output_zip, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for file in os.listdir(dist_path):
                file_path = os.path.join(dist_path, file)
                if os.path.isfile(file_path):
                    zipf.write(file_path, arcname=file)
        print(f"[+] Zipped to {output_zip}")
    except Exception as e:
        print("❌ Failed to zip:", e)

if __name__ == '__main__':
    zip_exe()