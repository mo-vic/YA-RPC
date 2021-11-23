from communication.connector import ClientConnector


class Client:
    def __init__(self, ip, port):
        self.rpcs = None
        self.connector = ClientConnector(ip, port)
        self.connector.connect()
        self.ip = ip
        self.port = port

        self.retrieve_rpcs()
        self.generate_stubs()

    def retrieve_rpcs(self):
        msg = {"type": "retrieve"}
        self.connector.send(msg)
        ret = self.connector.receive()
        self.rpcs = ret["rpcs"]

    def generate_stubs(self):
        for rpc in self.rpcs:
            name = rpc["name"]

            # borrow keyword `this` from C++
            def func(*args, this=name, **kwargs):
                msg = {"type": "call", "name": this, "args": args, "kwargs": kwargs}
                self.connector.send(msg)
                obj = self.connector.receive()

                if isinstance(obj, Exception):
                    raise obj
                else:
                    return obj

            setattr(self, name, func)
