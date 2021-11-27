import threading
from communication.connector import ListenerConnector


class Listener:
    def __init__(self, ip, port, backlog=None):
        self.ip = ip
        self.port = port

        self.rpcs = list()

        self.listener = ListenerConnector(ip, port)
        self.listener.listen(backlog)

        # save the active ServerConnector objects
        self.server_id = 0
        self.server_dict = dict()
        self.server_dict_lock = threading.Lock()

    def register_procedure(self, procedure):
        if callable(procedure):
            name = procedure.__name__
            self.rpcs.append({"name": name})
            setattr(self, procedure.__name__, procedure)
        else:
            print("Procedure is not callable.")

    def serving(self, conn, server_id):
        while True:
            try:
                msg = conn.receive()

                # connection closed normally
                if not msg:
                    break

                msg_id = msg["id"]
                msg_type = msg["type"]
                if msg_type == "retrieve":
                    conn.send({"id": msg_id, "type": "retrieve", "rpcs": self.rpcs})
                elif msg_type == "call":
                    name = msg["name"]
                    args = msg["args"]
                    kwargs = msg["kwargs"]
                    try:
                        func = getattr(self, name)
                        ret = func(*args, **kwargs)
                    except Exception as e:
                        conn.send({"id": msg_id, "ret": e})
                    else:
                        conn.send({"id": msg_id, "ret": ret})
            except Exception as e:
                print("In serving:", e)
                break
        # delete the active ServerConnector object from the server_dict, this will dereference to the ServerConnector
        # object and thus the connection object can be successfully garbage collected when the thread exit
        with self.server_dict_lock:
            self.server_dict.pop(server_id)

    def listen(self):
        while True:
            try:
                server = self.listener.accept()

                if not server:
                    continue

                server_id = self.server_id
                self.server_id += 1
                with self.server_dict_lock:
                    self.server_dict[server_id] = server
                t = threading.Thread(target=self.serving, args=(server, server_id))
                t.daemon = False
                t.start()

                # this is necessary, because before accepting the next connection, variable server still reference to
                # current ServerConnector object, deferring garbage collection
                server = None
            except KeyboardInterrupt as e:
                with self.server_dict_lock:
                    for v in self.server_dict.values():
                        # manually close the active ServerConnector object, the subsequent socket.recv() call will raise
                        # an exception to break the while loop
                        v.close()
                break
