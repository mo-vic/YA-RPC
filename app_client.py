import argparse
from rpc.client import Client

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("--ip", type=str, default="127.0.0.1", help="IP address.")
    parser.add_argument("--port", type=int, default=6006, help="Listening port.")
    args = parser.parse_args()

    client = Client(args.ip, args.port)

    print("client.sum(1.0, 2.0) = ", client.sum(1.0, 2.0))
    print("client.upper('abc') = ", client.upper("abc"))
    print("client.lower('ABC') = ", client.lower("ABC"))
