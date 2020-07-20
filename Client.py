import random
import socket
import threading
import message_manipulation as mm
import datetime

HEADER = 64
PORT = 5050
SERVER = socket.gethostbyname(socket.gethostname())
# SERVER = '192.168.1.230'
ADDR = (SERVER, PORT)
FORMAT = 'utf-8'

client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect(ADDR)


def send(msg):
    message = msg.encode(FORMAT)
    msg_length = len(message)
    send_length = str(msg_length).encode(FORMAT)
    send_length += b' ' * (HEADER - len(send_length))
    client.send(send_length)
    client.send(message)


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

continue_flag = True


while continue_flag:
    measurement_id = input("Enter the Measurement ID: \n")
    resend_flag = True

    while resend_flag:

        req_id = random.randint(0, 65535)

        req_msg = "<request>\n<id>" + str(req_id) + "</id>\n<measurement>" + measurement_id + "</measurement>\n</request>"
        req_msg_trimmed = req_msg.replace("\n", "").replace("\r", "").replace("\t", "").replace(" ", "")
        to_send = req_msg + str(checksum(req_msg_trimmed))

        send(to_send)

        i = 1

        while i < 9:
            client.settimeout(i)
            try:
                msg_length = client.recv(HEADER).decode(FORMAT)

                if msg_length:
                    msg_length = int(msg_length)
                    msg = client.recv(msg_length).decode(FORMAT)
                break

            except socket.timeout as e:
                print(e)

            i = i * 2
            if i > 8:
                send("DISCONNECT")
                print("No response received! Program exiting.")
                exit(0)

        resp_msg, msg_string, resp_ids = mm.message_manipulation(msg)
        recv_code = int(resp_ids[1])
        recv_crc = int(resp_ids[-1])

        if checksum(resp_msg) == int(resp_ids[-1]):
            if recv_code == 0:
                print("Temperature measurement: " + resp_ids[3])
                resend_flag = False

            elif recv_code == 1:
                print("Error: integrity check failure. The request has one or more bit errors.")
                resend_input = input("Do you want to resend the request? (Y/N)")
                if resend_input == 'Y' or resend_input == 'y':
                    resend_flag = True
                else:
                    resend_flag = False

            elif recv_code == 2:
                print("Error: malformed request. The syntax of the request message is not correct.")
                resend_flag = False

            elif recv_code == 3:
                print("Error: non-existent measurement. The measurement with the requested measurement ID does not exist.")
                resend_flag = False
        else: 
            print("Error: integrity check failure of response message. The reponse has one or more bit errors.")
            resend_flag = False


    continue_input = input("Do you want to re-enter the Measurement ID and resend the message? (Y/N)")
    if continue_input == 'Y' or continue_input == 'y':
        continue_flag = True
    else:
        continue_flag = False

send("DISCONNECT")
print("Disconnecting connection with server. Thank you!")