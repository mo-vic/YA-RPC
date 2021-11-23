import argparse
from rpc.listener import Listener


def sum(a, b):
    return a + b


def upper(string):
    return str.upper(string)


def lower(string):
    return str.lower(string)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("--ip", type=str, default="127.0.0.1", help="IP address.")
    parser.add_argument("--port", type=int, default=6006, help="Listening port.")
    parser.add_argument("--backlog", type=int, default=5, help="Queue size passed to `socket.listen()`")
    args = parser.parse_args()

    listener = Listener(args.ip, args.port, args.backlog)

    listener.register_procedure(sum)
    listener.register_procedure(upper)
    listener.register_procedure(lower)

    listener.listen()
