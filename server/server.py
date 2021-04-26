import socket
import sys
import time
import os
import struct

print("Use connect on client to connect to server")

# default socket values
Client_IP = "127.0.0.1" # default IP
Server_PORT = 9000 # unique port number to not conflict
BUFFER_SIZE = 1024
mySocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
mySocket.bind((Client_IP, Server_PORT))
mySocket.listen(1)
socket_connection, address = mySocket.accept()

print("Connected to: {}".format(address))


def readi(mySocket):
    msg = mySocket.recv(4)
    if not msg:
        return -1
    else:
        return struct.unpack("i", msg)[0]


def readh(mySocket):
    msg = mySocket.recv(2)
    if not msg:
        return -1
    else:
        return struct.unpack("h", msg)[0]


def reads(mySocket, stringSize):
    msg = mySocket.recv(stringSize)
    if not msg:
        return ""
    else:
        return msg.decode()


def put():
    # send ready
    socket_connection.send("1".encode())
    # get file name length
    file_name_length = readh(socket_connection)
    # get file name
    file_name = reads(socket_connection,file_name_length)
    # send ready
    socket_connection.send("1".encode())
    # get file size
    file_size = readi(socket_connection)
    # get file
    output_file = open(file_name, "wb")
    bytes_recieved = 0
    while bytes_recieved < file_size:
        output_file.write(socket_connection.recv(BUFFER_SIZE))
        bytes_recieved += BUFFER_SIZE
    output_file.close()
    print("got file: {}".format(file_name))
    return

def ls():
    print("Sending file list")
    # get the list
    files = os.listdir(os.getcwd())
    # send count
    socket_connection.send(struct.pack("i", len(files)))
    for f in files:
        print(f)
        # len of name
        socket_connection.send(struct.pack("i", sys.getsizeof(f)))
        # name
        socket_connection.send(f.encode())
        # file size
        socket_connection.send(struct.pack("i", os.path.getsize(f)))
    socket_connection.recv(BUFFER_SIZE)
    print("Sent list.")
    return


def get():
    socket_connection.send("1".encode())
    file_name_length = readh(socket_connection)
    file_name = reads(socket_connection, file_name_length)
    print(file_name)
    if os.path.isfile(file_name):
        socket_connection.send(struct.pack("i", os.path.getsize(file_name)))
    else:
        print("File doesn't exist, nothing sent")
        socket_connection.send(struct.pack("i", -1))
        return
    # Wait for ok to send file
    socket_connection.recv(BUFFER_SIZE)
    # send file
    print("Sending file...")
    content = open(file_name, "rb")
    buff = content.read(BUFFER_SIZE)
    while buff:
        socket_connection.send(buff)
        buff = content.read(BUFFER_SIZE)
    content.close()
    # wait for client to acknowledge
    socket_connection.recv(BUFFER_SIZE)
    return


def quit():
    # Send acknowledgement
    socket_connection.send("1".encode())
    socket_connection.close()
    mySocket.close()
    os.execl(sys.executable, sys.executable, *sys.argv)

while True:
    # Rest until client sends command
    print("\nResting")
    msg = reads(socket_connection, BUFFER_SIZE)
    print("Instruction: {}".format(msg))
    # run the command
    if msg == "PUT":
        put()
    elif msg == "LS":
        ls()
    elif msg == "GET":
        get()
    elif msg == "QUIT":
        quit()
    msg = None
