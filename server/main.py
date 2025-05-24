import argparse
from server.core import PeerServer

def main():
    parser = argparse.ArgumentParser(description="Peer-to-Peer Server")
    parser.add_argument("-a", "--address", default="0.0.0.0", help="IP address to bind to")
    parser.add_argument("-p", "--port", type=int, default=12345, help="TCP port to listen on")
    args = parser.parse_args()

    server = PeerServer(args.address, args.port)
    server.start()

if __name__ == "__main__":
    main()