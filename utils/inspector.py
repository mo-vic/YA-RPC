import re


class Inspector:
    @staticmethod
    def verify_ip(ip):
        regex = re.compile(r"^((25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)(\.|)){3}(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$")
        if type(ip) is str and not re.search(regex, ip) is None:
            return ip
        else:
            return None

    @staticmethod
    def verify_port(port):
        regex = re.compile(r"^([0-9]{1,4}|[1-5][0-9]{4}|6[0-4][0-9]{3}|65[0-4][0-9]{2}|655[0-2][0-9]|6553[0-5])$")
        if type(port) is str and not re.search(regex, port) is None:
            return int(port)
        elif type(port) is int and 0 < port <= 2 ** 16:
            return port
        else:
            return None
