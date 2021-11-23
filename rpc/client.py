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
        for name, func in (self.make_func(rpc["name"]) for rpc in self.rpcs):
            setattr(self, name, func)

    def make_func(self, name):
        def func(*args, **kwargs):
            msg = {"type": "call", "name": name, "args": args, "kwargs": kwargs}
            self.connector.send(msg)
            obj = self.connector.receive()

            if isinstance(obj, Exception):
                raise obj
            else:
                return obj

        return name, func
