import socket

HOST = '0.0.0.0'
PORT = 9999

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.bind((HOST, PORT))
    s.listen(1)
    print(f"Waiting for Windows VM to connect on port {PORT}...")

    conn, addr = s.accept()
    with conn:
        print(f"Connected by {addr}")
        prompt = "LSW> "

        while True:
            command = input(prompt)
            if not command:
                break
            conn.sendall(command.encode())

            result = conn.recv(4096).decode()

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

            # Reassemble output without duplicate command echo
            output = "\n".join(output_lines)

            # Modified: Only print the output, not the prompt line again
            if output:
                print(output)

            # Update prompt to new prompt line (up to '> ')
            if ">" in prompt_line:
                prompt = prompt_line.split(">")[0] + "> "