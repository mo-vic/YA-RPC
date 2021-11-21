import socket
import pickle

from utils.inspector import Inspector


class Connector:
    def __init__(self, ip, port):
        ip = Inspector.verify_ip(ip)
        if ip is None:
            print("Invalid IP.")
            raise ValueError
        port = Inspector.verify_port(port)
        if port is None:
            print("Invalid port.")
            raise ValueError
        self.ip = ip
        self.port = port

        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    def __del__(self):
        self.socket.close()
        print("Bye~~")


class ClientConnector(Connector):
    def __init__(self, ip, port):
        super(ClientConnector, self).__init__(ip, port)

    def connect(self):
        self.socket.connect((self.ip, self.port))

    def send(self, obj):
        msg = pickle.dumps(obj)
        self.socket.sendall(msg)

    def receive(self, buffsize=None):
        msg = self.socket.recv(1024 if buffsize is None else buffsize)
        obj = pickle.loads(msg)

        return obj


class ListenerConnector(Connector):
    def __init__(self, ip, port):
        super(ListenerConnector, self).__init__(ip, port)

    def listen(self, backlog=None):
        self.socket.bind((self.ip, self.port))
        self.socket.listen(1 if backlog is None else backlog)

    def accept(self, buffsize=None):
        (conn, (ip, port)) = self.socket.accept()

        msg = conn.recv(1024 if buffsize is None else buffsize)
        conn.close()
        obj = pickle.loads(msg)
        print(obj)

        return obj


if __name__ == '__main__':
    import math

    choice = input()
    if choice == 'c':
        client = ClientConnector("127.0.0.1", 6006)
        client.connect()
        client.send({"Hello": math.pi, "World": math.e})
    else:
        listener = ListenerConnector("127.0.0.1", 6006)
        listener.listen()
        listener.accept()
