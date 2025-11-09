import os
import webbrowser
import threading
import subprocess
import sys

def open_browser():
    webbrowser.open("http://127.0.0.1:8000")

def start_server():
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    # Hide command prompt window
    startupinfo = subprocess.STARTUPINFO()
    startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
    subprocess.Popen(
        [sys.executable, "manage.py", "runserver", "127.0.0.1:8000"],
        startupinfo=startupinfo,
        creationflags=subprocess.CREATE_NO_WINDOW
    )

if __name__ == "__main__":
    threading.Timer(2, open_browser).start()
    start_server()
