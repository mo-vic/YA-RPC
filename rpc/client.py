import threading
from communication.connector import ClientConnector


class Client:
    def __init__(self, ip, port, timeout=5):
        self.rpcs = None

        self.connector = ClientConnector(ip, port, timeout=timeout)
        self.connector.connect()

        self.ip = ip
        self.port = port

        # maintain an incremental message id
        self.msg_id = 0
        self.msg_id_lock = threading.Lock()

        # buffer the received messages
        self.buffered_message_queue = dict()
        self.buffered_message_queue_lock = threading.Lock()

        # save the threading.Event objects, used to wake up a blocked thread
        self.wait_queue = dict()
        self.wait_queue_lock = threading.Lock()

        self.retrieve_rpcs()
        self.generate_stubs()

    def set_timeout(self, timeout):
        self.connector.set_timeout(timeout)

    def send_message(self, msg):
        self.connector.send(msg)

    def receive_message(self, msg_id):
        msg = self.connector.receive()

        # return if id matched
        if msg["id"] == msg_id:
            return msg
        else:
            # wake up the thread who sending message with id = msg["id"]
            with self.buffered_message_queue_lock:
                self.buffered_message_queue[msg["id"]] = msg

            with self.wait_queue_lock:
                if msg["id"] in self.wait_queue:
                    self.wait_queue[msg["id"]].set()

            # check whether the buffered_message_queue contains my message or not
            with self.buffered_message_queue_lock:
                if msg_id in self.buffered_message_queue:
                    return self.buffered_message_queue.pop(msg_id)

            # wait until someone else wake me up
            with self.wait_queue_lock:
                event = threading.Event()
                self.wait_queue[msg_id] = event
            event.wait()

            # waked, get my message from buffered_message_queue
            with self.buffered_message_queue_lock:
                msg = self.buffered_message_queue.pop(msg_id)
            with self.wait_queue_lock:
                self.wait_queue.pop(msg_id)

            return msg

    def retrieve_rpcs(self):
        with self.msg_id_lock:
            msg_id = self.msg_id
            self.msg_id += 1
        msg = {"id": msg_id, "type": "retrieve"}
        self.send_message(msg)
        msg = self.receive_message(msg_id)
        self.rpcs = msg["rpcs"]

    def generate_stubs(self):
        for rpc in self.rpcs:
            name = rpc["name"]

            def make_func(name):
                def func(*args, **kwargs):
                    with self.msg_id_lock:
                        msg_id = self.msg_id
                        self.msg_id += 1
                    msg = {"id": msg_id, "type": "call", "name": name, "args": args, "kwargs": kwargs}
                    self.send_message(msg)
                    msg = self.receive_message(msg_id)
                    ret = msg["ret"]

                    if isinstance(ret, Exception):
                        raise ret
                    else:
                        return ret

                return func

            setattr(self, name, make_func(name))
