import threading
from communication.connector import ListenerConnector


class Listener:
    def __init__(self, ip, port, backlog=None):
        self.rpcs = list()
        self.listener = ListenerConnector(ip, port)
        self.listener.listen(backlog)
        self.ip = ip
        self.port = port

    def register_procedure(self, procedure):
        if callable(procedure):
            name = procedure.__name__
            self.rpcs.append({"name": name})
            setattr(self, procedure.__name__, procedure)
        else:
            print("Procedure is not callable.")

    def serving(self, conn):
        while True:
            try:
                msg = conn.receive()
                if not msg:
                    break
                msg_type = msg["type"]
                if msg_type == "retrieve":
                    conn.send({"type": "retrieve", "rpcs": self.rpcs})
                elif msg_type == "call":
                    name = msg["name"]
                    args = msg["args"]
                    kwargs = msg["kwargs"]
                    try:
                        func = getattr(self, name)
                        ret = func(*args, **kwargs)
                    except Exception as e:
                        conn.send(e)
                    else:
                        conn.send(ret)
            except Exception as e:
                print("In serving:", e)
                break

    def listen(self):
        while True:
            try:
                server = self.listener.accept()
                t = threading.Thread(target=self.serving, args=(server,))
                t.daemon = False
                t.start()
            except Exception as e:
                print("In listen:", e)
