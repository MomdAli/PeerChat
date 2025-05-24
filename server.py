import socket
import threading
import argparse
import peer_connection as pc
import sys

clients = {} # nickname: (ip, udp_port)
server_running = True

def handle_client(conn, addr):
    try:
        print(f"Connection from {addr}")
        data = pc.recv_message(conn)
        if not data:
            return
        # Expect: REGISTER nickname udp_port
        if data.startswith("REGISTER"):
            _, nickname, udp_port = data.strip().split()
            clients[nickname] = (addr[0], udp_port)
            print(f"Registered {nickname} with UDP port {udp_port}")

            # Later send peer updates to others
        else:
            print(f"Unknown command: {data}")
    except Exception as e:
        print(f"Error handling client {addr}: {e}")
    finally:
        conn.close()
        print(f"Connection closed for {addr}")

def input_thread():
    global server_running
    while True:
        if input().strip().lower() == 'q':
            print("Shutting down server...")
            server_running = False
            break

def start_server(HOST, PORT):
    global server_running
    print(f"Starting server on {HOST}:{PORT}")
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_socket:
        server_socket.bind((HOST, PORT))
        server_socket.listen()
        print("Server is listening for connections...")

        threading.Thread(target=input_thread, daemon=True).start()

        while server_running:
            try:
                server_socket.settimeout(1.0)
                conn, addr = server_socket.accept()
                threading.Thread(target=handle_client, args=(conn, addr)).start()
            except socket.timeout:
                continue
            except Exception as e:
                print(f"Server error: {e}")
                break

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Group Chat Server")
    parser.add_argument("-a", "--address", default="0.0.0.0", help="IP address to bind to")
    parser.add_argument("-p", "--port", type=int, default=12345, help="TCP port to listen on")
    args = parser.parse_args()

    start_server(args.address, args.port)