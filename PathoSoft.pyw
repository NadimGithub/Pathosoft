import os
import webbrowser
import threading
import subprocess
import signal
import sys

def open_browser():
    webbrowser.open("http://127.0.0.1:8000")

def start_server():
    project_path = os.path.dirname(os.path.abspath(__file__))
    os.chdir(project_path)

    # path to venv python executable
    venv_python = os.path.join(project_path, "env", "Scripts", "python.exe")

    # Start server as a subprocess
    server_proc = subprocess.Popen(
        [venv_python, "manage.py", "runserver", "127.0.0.1:8000"],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        stdin=subprocess.DEVNULL,
        creationflags=subprocess.CREATE_NO_WINDOW  # Windows: hide console
    )
    return server_proc

if __name__ == "__main__":
    # Open browser shortly after starting
    threading.Timer(0.5, open_browser).start()

    # Start server
    server_process = start_server()

    try:
        # Keep the main script alive while the server runs
        server_process.wait()
    except KeyboardInterrupt:
        # Stop the server if user closes script (Ctrl+C)
        server_process.terminate()
        server_process.wait()
    finally:
        # Ensure server is killed when script ends
        if server_process.poll() is None:
            server_process.terminate()


# import os
# import webbrowser
# import threading
# import subprocess

# def open_browser():
#     webbrowser.open("http://127.0.0.1:8000")

# def start_server():
#     project_path = os.path.dirname(os.path.abspath(__file__))
#     os.chdir(project_path)

#     # path to venv python executable
#     venv_python = os.path.join(project_path, "env", "Scripts", "python.exe")

#     subprocess.Popen(
#         [venv_python, "manage.py", "runserver", "127.0.0.1:8000"],
#         stdout=subprocess.DEVNULL,
#         stderr=subprocess.DEVNULL,
#         stdin=subprocess.DEVNULL,
#         creationflags=subprocess.CREATE_NO_WINDOW  # Prevent console window
#     )

# if __name__ == "__main__":
#     threading.Timer(0.1, open_browser).start()
#     start_server()
