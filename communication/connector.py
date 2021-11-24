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
        msg = pickle.dumps(obj, protocol=4)
        self.socket.sendall(msg)

    def receive(self, buffsize=None):
        msg = self.socket.recv(1024 if buffsize is None else buffsize)
        if len(msg):
            obj = pickle.loads(msg)
        else:
            obj = None

        return obj


class ServerConnector(ClientConnector):
    def __init__(self, ip, port, conn):
        self.ip = ip
        self.port = port
        self.socket = conn


class ListenerConnector(Connector):
    def __init__(self, ip, port):
        super(ListenerConnector, self).__init__(ip, port)

    def listen(self, backlog=None):
        self.socket.bind((self.ip, self.port))
        self.socket.listen(1 if backlog is None else backlog)

    def accept(self):
        (conn, (ip, port)) = self.socket.accept()
        server = ServerConnector(ip, port, conn)

        return server


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
