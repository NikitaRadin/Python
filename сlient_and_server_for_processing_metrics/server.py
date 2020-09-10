import socket
import threading


server_data = {}


def correct_request(request):
    elements = request.split(' ')
    if elements[0] != "put" and elements[0] != "get":
        return False
    if elements[0] == "put" and len(elements) != 4 or elements[0] == "get" and len(elements) != 2:
        return False
    elements_ = elements[-1].split('\n')
    if len(elements_) != 2:
        return False
    if elements_[1] != "":
        return False
    elements[-1] = elements_[0]
    if elements[0] == "put":
        try:
            float(elements[2])
            int(elements[3])
        except ValueError:
            return False
    return True


def process_request(conn, server_data):
    with conn:
        while True:
            try:
                data = conn.recv(1024)
            except socket.timeout:
                break
            request = data.decode("utf8")
            if not correct_request(request):
                conn.send("error\nwrong command\n\n".encode("utf8"))
                continue
            elements = request.split(' ')
            elements_ = elements[-1].split('\n')
            elements[-1] = elements_[0]
            if elements[0] == "put":
                if elements[1] not in server_data:
                    server_data[elements[1]] = []
                i = 0
                server_list = server_data[elements[1]]
                for pair in server_list:
                    if pair[1] == int(elements[3]):
                        server_data[elements[1]][i] = (float(elements[2]), int(elements[3]))
                        break
                    i += 1
                if (float(elements[2]), int(elements[3])) not in server_data[elements[1]]:
                    server_data[elements[1]].append((float(elements[2]), int(elements[3])))
                conn.send("ok\n\n".encode("utf8"))
            elif elements[0] == "get" and elements[1] != "*":
                try:
                    response = "ok\n"
                    for pair in server_data[elements[1]]:
                        response += elements[1] + " " + str(pair[0]) + " " + str(pair[1]) + "\n"
                    response += "\n"
                    conn.send(response.encode("utf8"))
                except KeyError:
                    conn.send("ok\n\n".encode("utf8"))
            elif elements[0] == "get" and elements[1] == "*":
                response = "ok\n"
                for key in server_data:
                    for pair in server_data[key]:
                        response += key + " " + str(pair[0]) + " " + str(pair[1]) + "\n"
                response += "\n"
                conn.send(response.encode("utf8"))


def run_server(host, port):
    sock = socket.socket()
    sock.bind((host, port))
    sock.settimeout(10)
    sock.listen()
    while True:
        conn, addr = sock.accept()
        conn.settimeout(10)
        th = threading.Thread(target=process_request, args=(conn, server_data))
        th.start()
    sock.close()
