import socket
import sys
import os
import struct

# set defaults for socket data
Server_IP = "127.0.0.1"  # Loop back address for local testing.
Server_PORT = 9000  # unique port number to not conflict
BUFFER_SIZE = 1024
mySocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)


def readi(mySocket):
    msg = mySocket.recv(4)
    if not msg:
        return -1
    else:
        return struct.unpack("i", msg)[0]


def reads(mySocket, stringSize):
    msg = mySocket.recv(stringSize)
    if not msg:
        return ""
    else:
        return msg.decode()


def Connect2Server():
    # Open a new connection
    print("Opening a connection to {}".format(Server_IP))
    try:
        mySocket.connect((Server_IP, Server_PORT))
        print("Connected!")
    except:
        print("Connection failed, verify the server is running.")


def put(file_name):
    # Upload a file
    print("\nUploading file: {}...".format(file_name))
    try:
        # verify the file exists before uploading
        content = open(file_name, "rb")
        # Make upload request
        mySocket.send("PUT".encode())
        # once the server creates a buffer it will send the buffer size
        mySocket.recv(BUFFER_SIZE)
        # tell the server the file name size
        mySocket.send(struct.pack("H", sys.getsizeof(file_name)))
        # tell the server the file name
        mySocket.send(file_name.encode())

        # once the server creates a buffer it will send the buffer size
        mySocket.recv(BUFFER_SIZE)
        # tell the server the size of the actual file
        mySocket.send(struct.pack("I", os.path.getsize(file_name)))
        # break the file into chunks of buffer_size and send it
        myBuffer = content.read(BUFFER_SIZE)
        print("\nSending file...")
        while myBuffer:
            mySocket.send(myBuffer)
            myBuffer = content.read(BUFFER_SIZE)
        content.close()
        print("File Sent!")
    except:
        print("Error sending file")
        return
    return


def ls():
    # list all files on server
    print("Getting file list.")
    try:
        # send request
        mySocket.send("LS".encode())
        # Server tells us how many files it has
        number_of_files = readi(mySocket)
        # get the names of those files (and the size of the files)
        for i in range(int(number_of_files)):
            file_name_size = readi(mySocket)
            file_name = reads(mySocket, file_name_size)
            file_size = readi(mySocket)
            print("\t{} - {}b".format(file_name, file_size))
        # tell server you are done receiving file names
        mySocket.send("1".encode())
        return
    except:
        print("Error getting file list.")
        return


def get(file_name):
    # Download requested file
    print("Downloading file: {}".format(file_name))
    try:
        # Send server request
        mySocket.send("GET".encode())
        # once the server creates a buffer it will send the buffer size
        mySocket.recv(BUFFER_SIZE)
        # tell the server the file name size
        mySocket.send(struct.pack("h", sys.getsizeof(file_name)))
        # tell the server the file name
        mySocket.send(file_name.encode())
        # Server tells us the size of the file it is sending
        file_size = readi(mySocket)
        if file_size == -1:
            # negative file size does not exist
            print("File does not exist. Use LS to get a list of files.")
            return
        # let the server know we are ready
        mySocket.send("1".encode())
        # file will be broken into chunks, reassemble them
        output_file = open(file_name, "wb")
        bytes_received = 0
        print("Getting File...")
        while bytes_received < file_size:
            msg = mySocket.recv(BUFFER_SIZE)
            output_file.write(msg)
            bytes_received += BUFFER_SIZE
        output_file.close()
        print("Downloaded {}".format(file_name))
        # let the server know we got it all
        mySocket.send("1".encode())
    except:
        print("Error downloading file")
        return
    return


def quit():
    mySocket.send("QUIT".encode())
    # server acknolages quit message
    mySocket.recv(BUFFER_SIZE)
    mySocket.close()
    print("Connection closed")
    return

print("\n\nSimplified FTP Client\n\nCommands (not case sensitive):\nConnect - Open a Connection to a server\nPut <file_path> - Upload a file from <file_path>\nLS - gets a list of all available files\nGet <file_path> - Download a file from the server\nQuit - Exit this application\n")
run = True
while run:
    # get command from user
    command = input("\nEnter a command: ")
    # Split command into command and arguments
    args = command.split(' ')
    if args[0].upper() == "CONNECT":
        if len(args) > 1:
            Server_IP = args[1]
        if len(args) > 2:
            Server_Port = args[2]
        Connect2Server()
    elif args[0].upper() == "PUT":
        if len(args) < 2:
            print("Put needs a file name.")
        else:
            put(args[1])
    elif args[0].upper() == "LS":
        ls()
    elif args[0].upper() == "GET":
        if len(args) < 2:
            print("Get needs a file name.")
        else:
            get(args[1])
    elif args[0].upper() == "QUIT":
        quit()
        run = False
    else:
        print("Invalid Input, please use a valid command.\n\nCommands (not case sensitive):\nConnect - Open a Connection to a server\nPut <file_path> - Upload a file from <file_path>\nLS - gets a list of all available files\nGet <file_path> - Download a file from the server\nQuit - Exit this application\n")
