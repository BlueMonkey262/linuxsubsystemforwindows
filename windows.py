import socket
import subprocess
import os
import base64
import time
import traceback

HOST = '0.0.0.0'  # Listen on all available interfaces
PORT = 9999

mode = "ps"
cwd = os.path.expanduser("C:\\Users\\Admin")  # default directory


def encode_powershell_command(cmd: str) -> str:
    cmd_bytes = cmd.encode('utf-16le')
    return base64.b64encode(cmd_bytes).decode('ascii')


def run_powershell_command(command: str, cwd: str) -> str:
    ps_command = (
        "$ProgressPreference = 'SilentlyContinue';"
        "$OutputEncoding = [Console]::OutputEncoding = [Text.Encoding]::UTF8;"
        f"{command} | Out-String -Stream"
    )
    encoded_cmd = encode_powershell_command(ps_command)
    output = subprocess.check_output(
        ["powershell.exe", "-NoProfile", "-EncodedCommand", encoded_cmd],
        stderr=subprocess.STDOUT,
        text=True,
        cwd=cwd
    )
    return output.strip()


def get_prompt():
    global cwd
    if mode == "ps":
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


def handle_client(conn, addr):
    global mode, cwd

    print(f"Connected by {addr}")

    # Send initial prompt
    prompt = get_prompt()
    conn.sendall(prompt.encode())

    try:
        while True:
            try:
                # Set a timeout for receiving data
                conn.settimeout(1.0)
                data = conn.recv(4096)
                conn.settimeout(None)  # Reset timeout

                if not data:
                    print(f"Client {addr} disconnected")
                    break

                command = data.decode().strip()

                if command == 'lsw ps':
                    mode = "ps"
                    conn.sendall(f"{prompt}\n[LSW] Switched to PowerShell mode.".encode())
                    continue
                elif command == 'lsw cmd':
                    mode = "cmd"
                    conn.sendall(f"{prompt}\n[LSW] Switched to CMD mode.".encode())
                    continue

                try:
                    if command.lower().startswith("cd"):
                        parts = command.split(maxsplit=1)
                        if len(parts) == 2:
                            new_path = parts[1].strip('"').replace("/", "\\")
                            if new_path == "..":
                                cwd = os.path.dirname(cwd)
                            else:
                                combined = os.path.abspath(os.path.join(cwd, new_path))
                                if os.path.isdir(combined):
                                    cwd = combined
                                else:
                                    raise FileNotFoundError(f"The system cannot find the path specified: {combined}")
                        prompt = get_prompt()
                        conn.sendall(prompt.encode())
                        continue

                    if mode == "ps":
                        output = run_powershell_command(command, cwd)
                    else:
                        output = subprocess.check_output(
                            command,
                            shell=True,
                            stderr=subprocess.STDOUT,
                            text=True,
                            cwd=cwd
                        ).strip()

                    prompt = get_prompt()

                    # Remove duplicate prompt from output start, if present
                    if output.startswith(prompt):
                        output = output[len(prompt):].lstrip("\r\n")

                    # Send the prompt and output
                    full_output = f"{prompt}\n{output}"
                    conn.sendall(full_output.encode())

                except subprocess.CalledProcessError as e:
                    prompt = get_prompt()
                    err_output = e.output.strip()
                    # Also remove duplicate prompt from error output start, if present
                    if err_output.startswith(prompt):
                        err_output = err_output[len(prompt):].lstrip("\r\n")
                    full_output = f"{prompt}\n{err_output}"
                    conn.sendall(full_output.encode())
                except FileNotFoundError as e:
                    prompt = get_prompt()
                    full_output = f"{prompt}\n{str(e)}"
                    conn.sendall(full_output.encode())

            except socket.timeout:
                # Just a timeout, continue the loop
                continue
            except ConnectionResetError:
                print(f"Connection with {addr} was reset")
                break
            except BrokenPipeError:
                print(f"Connection with {addr} has broken pipe")
                break
            except Exception as e:
                print(f"Error handling client {addr}: {str(e)}")
                traceback.print_exc()
                break
    finally:
        conn.close()
        print(f"Connection with {addr} closed")


# Main server loop
with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_socket:
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_socket.bind((HOST, PORT))
    server_socket.listen(5)  # Allow up to 5 queued connections
    print(f"Server started on {HOST}:{PORT}")
    print(f"Waiting for Linux client to connect...")

    while True:
        try:
            # Accept new client connection
            conn, addr = server_socket.accept()

            # Handle the client in the same thread
            # You could spawn a new thread here for multiple clients
            handle_client(conn, addr)

        except KeyboardInterrupt:
            print("Server shutting down...")
            break
        except Exception as e:
            print(f"Error in main server loop: {str(e)}")
            traceback.print_exc()
            time.sleep(1)  # Prevent CPU spinning on repeated errors