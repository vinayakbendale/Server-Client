import datetime
import socket
import threading
import message_manipulation as mm


def client_connect(conn, addr):
    global DISCONNECT_MESSAGE
    connected = True

    print(f"[NEW CONNECTION] {ADDR} connected.")

    while connected:
        msg_length = conn.recv(HEADER).decode(FORMAT)
        if msg_length:
            msg_length = int(msg_length)
            msg = conn.recv(msg_length).decode(FORMAT)
            # print(f"[{addr}] {msg}")
            print(f"Request received from {addr}")
            if msg == DISCONNECT_MESSAGE:
                print(f"Disconnecting... {addr}")
                break

        rec_msg, msg_string, req_ids = mm.message_manipulation(msg)

        request_format = "<request><id></id><measurement></measurement></request>"

        code = 0

        if checksum(rec_msg) != int(req_ids[2]):
            code = 1
            print("Error: integrity check failure. The request has one or more bit errors.")

        if msg_string != request_format:
            code = 2
            print("Error: malformed request. The syntax of the request message is incorrect.")

        if int(req_ids[1]) not in idmapping:
            code = 3
            print("Error: non-existent measurement. The measurement with the requested Measurement ID does not exist.")

        if code == 0:
            response = "<response>\n<id>" + str(req_ids[0]) + "</id>\n<code>" + str(
                code) + "</code>\n<measurement>" + str(req_ids[1]) + "</measurement>\n<value>" + str(
                idmapping.get(int(req_ids[1]))) + "</value>\n</response>"
        else:
            response = "<response>\n<id>" + str(req_ids[0]) + "</id>\n<code>" + str(code) + "</code>\n</value>"

        response_trimmed = response.replace("\n", "").replace("\r", "").replace("\t", "").replace(" ", "")

        response = response + "\n" + str(checksum(response_trimmed))
        print(f"Sending response to {addr}\n")
        send(conn, response)
    conn.close()


def send(client, msg):
    message = msg.encode(FORMAT)
    msg_length = len(message)
    send_length = str(msg_length).encode(FORMAT)
    send_length += b' ' * (HEADER - len(send_length))
    client.send(send_length)
    client.send(message)


def start_server():
    server.listen()
    print(f"[Listening] Server is listening on {SERVER}")
    while True:
        conn, addr = server.accept()
        newthread = threading.Thread(target=client_connect, args=(conn, addr))
        newthread.start()
        print(f"\n[ACTIVE CONNECTIONS] {threading.activeCount() - 1}")


def checksum(req_msg):
    x = []

    if len(req_msg) % 2 == 0:
        for i in range(0, len(req_msg) - 1, 2):
            x.append((ord(req_msg[i]) << 8) + ord(req_msg[i + 1]))

    else:
        for i in range(0, len(req_msg) - 1, 2):
            x.append((ord(req_msg[i]) << 8) + ord(req_msg[i + 1]))

        x.append((ord(req_msg[-1]) << 8))

    s, c, d = 0, 7919, 65536
    for i in x:
        index = s ^ i
        s = (c * index) % d

    return s


idmapping = {}

try:
    with open("D:\Python Scripts\data.txt") as f:
        for line in f:
            (key, val) = line.split()
            idmapping[int(key)] = val
except Exception as E:
    print(E)

HEADER = 64
PORT = 5050
SERVER = socket.gethostbyname(socket.gethostname())
# SERVER = '192.16?8.1.230'
ADDR = (SERVER, PORT)
FORMAT = 'utf-8'
DISCONNECT_MESSAGE = "DISCONNECT"

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind(ADDR)

print("[Starting] server is starting...")
start_server()
