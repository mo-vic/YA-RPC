import socket
import pickle
import threading

from utils.inspector import Inspector


class Connector:
    def __init__(self, ip, port, conn=None):
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

        if conn:
            # use the socket object returned by socket.accept()
            self.socket = conn
        else:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    def __del__(self):
        # called when garbage collected
        self.close()

    def close(self):
        self.socket.close()
        print("Bye~~")


class ClientConnector(Connector):
    def __init__(self, ip, port, conn=None, timeout=5):
        super(ClientConnector, self).__init__(ip, port, conn)
        self.timeout = timeout

        """
        Buffer the received bytes.
        A single socket.recv() call might contain more than one message or
        incomplete message.
        """
        self.receive_bytes_buffer = []

        # ensure that there is at most one thread calling the socket.sendall() or socket.recv()
        self.send_lock = threading.Lock()
        self.receive_lock = threading.Lock()

    def set_timeout(self, timeout):
        self.timeout = timeout

    def connect(self):
        self.socket.connect((self.ip, self.port))

    def send(self, msg):
        # serialize an obj to bytes
        msg = pickle.dumps(msg, protocol=4)
        with self.send_lock:
            self.socket.sendall(msg)

    def receive(self, buffsize=None):
        with self.receive_lock:
            self.socket.settimeout(self.timeout)

            while True:
                """
                Before calling socket.recv, check if there is any complete message in the receive_bytes_buffer
                """
                buffered_bytes = b''.join(self.receive_bytes_buffer)

                # b'.' is the STOP opcode
                if b'.' in buffered_bytes:
                    # split the messages by STOP opcode
                    buffered_messages = buffered_bytes.split(b'.')
                    # get first element
                    buffered_message = buffered_messages.pop(0)

                    # append the STOP opcode, then de-serialize the buffered bytes to a Python object
                    msg = pickle.loads(buffered_message + b'.')
                    # clear the receive_bytes_buffer
                    self.receive_bytes_buffer.clear()
                    # put the remaining bytes back to the receive_bytes_buffer
                    self.receive_bytes_buffer.append(b'.'.join(buffered_messages))
                    break

                """
                No complete message found in the receive_bytes_buffer, try to receive bytes by calling socket.recv()
                """
                try:
                    msg = self.socket.recv(1024 if buffsize is None else buffsize)
                except socket.timeout:
                    # every receive() call is responsible for receiving a complete message, loop until there is one
                    continue
                # msg == b'' means that the other side closed the connection
                if len(msg):
                    self.receive_bytes_buffer.append(msg)
                else:
                    msg = None
                    break

        return msg


class ServerConnector(Connector):
    def __init__(self, ip, port, conn=None):
        super(ServerConnector, self).__init__(ip, port, conn)
        self.receive_bytes_buffer = []

        # ensure that there is at most one thread calling the socket.sendall() or socket.recv()
        self.send_lock = threading.Lock()
        self.receive_lock = threading.Lock()

    def connect(self):
        self.socket.connect((self.ip, self.port))

    def send(self, msg):
        # serialize an obj to bytes
        msg = pickle.dumps(msg, protocol=4)
        with self.send_lock:
            self.socket.sendall(msg)

    def receive(self, buffsize=None):
        with self.receive_lock:
            while True:
                """
                Before calling socket.recv, check if there is any complete message in the receive_bytes_buffer
                """
                buffered_bytes = b''.join(self.receive_bytes_buffer)

                # b'.' is the STOP opcode
                if b'.' in buffered_bytes:
                    # split the messages by STOP opcode
                    buffered_messages = buffered_bytes.split(b'.')
                    # get first element
                    buffered_message = buffered_messages.pop(0)

                    # append the STOP opcode, then de-serialize the buffered bytes to a Python object
                    msg = pickle.loads(buffered_message + b'.')
                    # clear the receive_bytes_buffer
                    self.receive_bytes_buffer.clear()
                    # put the remaining bytes back to the receive_bytes_buffer
                    self.receive_bytes_buffer.append(b'.'.join(buffered_messages))
                    break

                """
                No complete message found in the receive_bytes_buffer, try to receive bytes by calling socket.recv()
                """
                msg = self.socket.recv(1024 if buffsize is None else buffsize)
                # msg == b'' means that the other side closed the connection
                if len(msg):
                    self.receive_bytes_buffer.append(msg)
                else:
                    msg = None
                    break

        return msg


class ListenerConnector(Connector):
    def __init__(self, ip, port, timeout=2):
        self.timeout = timeout
        super(ListenerConnector, self).__init__(ip, port)

    def listen(self, backlog=None):
        self.socket.bind((self.ip, self.port))
        self.socket.listen(1 if backlog is None else backlog)

    def accept(self):
        # set timeout value to ensure checking KeyboardInterrupt periodically
        self.socket.settimeout(self.timeout)
        try:
            (conn, (ip, port)) = self.socket.accept()
            server = ServerConnector(ip, port, conn)
        except socket.timeout:
            server = None

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
