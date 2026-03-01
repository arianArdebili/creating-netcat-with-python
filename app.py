import argparse
import socket
import shlex
import subprocess
import sys
import textwrap
import threading


def execute(cmd):
    cmd = cmd.strip()
    if not cmd:
        return ""
    try:
        # Use shell=True for better command compatibility in simple shells
        output = subprocess.check_output(shlex.split(cmd),
                                         stderr=subprocess.STDOUT)
        return output.decode()
    except Exception as e:
        return f"Failed to execute: {str(e)}\n"


class NetCat:
    def __init__(self, args, buffer=None):
        self.args = args
        self.buffer = buffer
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    def run(self):
        if self.args.listen:
            self.listen()
        else:
            self.send()

    def send(self):
        self.socket.connect((self.args.target, self.args.port))

        if self.buffer:
            self.socket.send(self.buffer)

        try:
            while True:
                recv_len = 1
                response = ""
                while recv_len:
                    data = self.socket.recv(4096)
                    recv_len = len(data)
                    response += data.decode()
                    if recv_len < 4096:
                        break

                if response:
                    print(response, end="")
                    # The prompt is now printed, so we wait for user input
                    buffer = input("")
                    buffer += "\n"
                    self.socket.send(buffer.encode())

        except KeyboardInterrupt:
            print("\nUser terminated.")
            self.socket.close()
            sys.exit()

    def listen(self):
        self.socket.bind((self.args.target, self.args.port))
        self.socket.listen(5)
        print(f"[*] Listening on {self.args.target}:{self.args.port}")

        while True:
            client_socket, _ = self.socket.accept()
            client_thread = threading.Thread(
                target=self.handle, args=(client_socket,)
            )
            client_thread.start()

    def handle(self, client_socket):
        if self.args.execute:
            output = execute(self.args.execute)
            client_socket.send(output.encode())

        elif self.args.upload:
            file_buffer = b""
            while True:
                data = client_socket.recv(4096)
                if data:
                    file_buffer += data
                else:
                    break
            with open(self.args.upload, "wb") as f:
                f.write(file_buffer)
            client_socket.send(f"Saved file {self.args.upload}".encode())

        elif self.args.command:
            # We send an initial prompt so the client's 'recv' finishes immediately
            client_socket.send(b"<BHP:#> ")
            while True:
                try:
                    cmd_buffer = b""
                    while b"\n" not in cmd_buffer:
                        cmd_buffer += client_socket.recv(64)

                    response = execute(cmd_buffer.decode())
                    if response:
                        # Add the prompt back to the end of the response
                        client_socket.send((response + "<BHP:#> ").encode())
                except Exception:
                    client_socket.close()
                    break


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="BHP Net Tool",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=textwrap.dedent("""Example:
            netcat.py -t 0.0.0.0 -p 5555 -l -c  # Server
            netcat.py -t 127.0.0.1 -p 5555      # Client
            """)
    )
    parser.add_argument("-c", "--command", action="store_true", help="command shell")
    parser.add_argument("-e", "--execute", help="execute specific command")
    parser.add_argument("-l", "--listen", action="store_true", help="listen mode")
    parser.add_argument("-p", "--port", type=int, default=5555, help="specified port")
    parser.add_argument("-t", "--target", default="127.0.0.1", help="target IP")
    parser.add_argument("-u", "--upload", help="upload file")

    args = parser.parse_args()
    if args.listen:
        buffer = b""
    else:
        # Check if there is data on stdin (like a pipe)
        if not sys.stdin.isatty():
            buffer = sys.stdin.read().encode()
        else:
            buffer = b""

    nc = NetCat(args, buffer)
    nc.run()