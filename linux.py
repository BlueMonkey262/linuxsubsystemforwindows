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
            print(result)

            # Extract new prompt from the result
            first_line = result.splitlines()[0] if result else ""
            if ">" in first_line:
                prompt = first_line.split(">")[0] + "> "
