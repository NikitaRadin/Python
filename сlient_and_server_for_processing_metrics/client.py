import socket
import time


def correct_response(response):
    pairs = response.split('\n')
    if len(pairs) < 3:
        return False
    if pairs[0] != "ok" and pairs[0] != "error":
        return False
    del pairs[0]
    if pairs[-1] != "" or pairs[-2] != "":
        return False
    del pairs[-1]
    del pairs[-1]
    for pair in pairs:
        elements = pair.split(' ')
        if len(elements) != 3:
            return False
        try:
            float(elements[1])
            int(elements[2])
        except ValueError:
            return False
    return True


class ClientError(Exception):
    pass


class Client:
    def __init__(self, host, port, timeout=None):
        self.sock = socket.create_connection((host, port), timeout)

    def put(self, key, value, timestamp=None):
        self.sock.sendall(("put " + key + " " + str(value) + " " + str(timestamp or int(time.time())) + "\n").encode("utf8"))
        response = self.sock.recv(1024).decode("utf8")
        if not correct_response(response):
            raise ClientError
        status = response.split('\n')[0]
        if status == "error":
            raise ClientError
        return None

    def get(self, key):
        self.sock.sendall(("get " + key + "\n").encode("utf8"))
        response = self.sock.recv(1024).decode("utf8")
        if not correct_response(response):
            raise ClientError
        pairs = response.split('\n')
        status = pairs[0]
        if status == "error":
            raise ClientError
        del pairs[0]
        del pairs[-1]
        del pairs[-1]
        result = {}
        def sort_key(source):
            return source[0]
        for pair in pairs:
            elements = pair.split(' ')
            result[elements[0]] = []
        for pair in pairs:
            elements = pair.split(' ')
            result[elements[0]].append((int(elements[2]), float(elements[1])))
        for key in result:
            result[key].sort(key=sort_key)
        return result

    def __del__(self):
        self.sock.close()
