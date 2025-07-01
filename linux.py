import socket

HOST = '0.0.0.0'   # Listen on all interfaces
PORT = 9999

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.bind((HOST, PORT))
    s.listen(1)
    print(f"Waiting for Windows VM to connect on port {PORT}...")

    conn, addr = s.accept()
    with conn:
        print(f"Connected by {addr}")

        while True:
            command = input("Command to run on Windows: ")
            if not command:
                break
            conn.sendall(command.encode())

            result = conn.recv(4096).decode()
            print(f"[Windows replied]:\n{result}")
