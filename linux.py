import socket
import subprocess

HOST = '192.168.122.218'  # IP address of the Windows machine
PORT = 9999



with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.connect((HOST, PORT))

    # Receive the initial prompt
    data = s.recv(4096)
    if data:
        prompt_line = data.decode().strip()
        print(f"Connected to Windows server: {prompt_line}")

    while True:
        # Get command from user with the current prompt
        command = input(prompt_line + " ")
        if not command:
            break

        # Send command to the Windows server
        s.sendall(command.encode())

        # Receive response
        result = s.recv(4096).decode()

        # Split lines
        lines = result.splitlines()

        # Extract prompt line and rest of output
        if lines:
            prompt_line = lines[0]
            output_lines = lines[1:]
        else:
            prompt_line = ""
            output_lines = []

        # Remove duplicate echoed command if present
        if output_lines and output_lines[0].strip().lower() == command.strip().lower():
            output_lines = output_lines[1:]

        # Print only the actual output, not the prompt again
        if output_lines:
            output = "\n".join(output_lines)
            print(output)