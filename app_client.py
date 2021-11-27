import argparse
import threading
from rpc.client import Client


def func(client, lock):
    a = client.sum(1.0, 2.0)
    b = client.upper("abc")
    c = client.lower("ABC")
    with lock:
        tid = threading.currentThread().ident
        print("In thread pid:", tid)
        print("client.sum(1.0, 2.0) = ", a)
        print("client.upper('abc') = ", b)
        print("client.lower('ABC') = ", c)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("--ip", type=str, default="127.0.0.1", help="IP address.")
    parser.add_argument("--port", type=int, default=6006, help="Listening port.")
    args = parser.parse_args()

    client = Client(args.ip, args.port)
    client.set_timeout(5)

    ts = []
    lock = threading.Lock()
    for i in range(12):
        t = threading.Thread(target=func, args=(client, lock))
        t.daemon = False
        ts.append(t)
        t.start()
