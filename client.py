from datetime import time
import socket
from socket import error
import time
import threading
import errno
global s
import tkinter as tk
from functools import partial
gui = tk.Tk()

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
HEADER_LENGTH = 10

version = "0.1.11"
protocolVersion = 11  # Do not change! Server and client protocol versions must be the same. - Colin

print("Chat Client v" + str(version))



def setUsername():
    global username
    global username_header
    username = usernametext.get().encode("utf-8")
    username_header = f"{len(username):<{HEADER_LENGTH}}".encode("utf-8")

    gui.destroy()

usernametext = tk.Entry()
usernametext.pack()
usernamebutton = tk.Button(gui, text="Set", command= setUsername)
usernamebutton.pack()

gui.mainloop()

def setServerMain():
    global serverip
    serverip = "104.156.229.228"
    gui.destroy()

gui = tk.Tk()

serverbutton = tk.Button(gui, text="Main", command=setServerMain)
serverbutton.pack()

gui.mainloop()

print("Connecting to the server...")

while True:
    try:
        s.connect((serverip, 25000))
        s.send(username_header + username)
        pvToString, serverID, cooldownToString = [str(i) for i in s.recv(1024).decode('utf-8').split('\n')]
        serverProtocolVersion = int(pvToString)
        if serverProtocolVersion == protocolVersion:
            print("Connected to the server with identification \"" + serverID + "\"")
            global cooldown
            cooldown = int(cooldownToString)
            print("Cooldown for this server is " + str(cooldown) + " seconds")
            break
        elif serverProtocolVersion > protocolVersion:
            print("Unable to connect to the specified server.")
            print("Your client is outdated! Using protocol version " + str(protocolVersion) + " instead of server protocol version " + str(serverProtocolVersion) + ".")
            print("Program will terminate in 5 seconds...")
            time.sleep(5)
            exit()
        elif serverProtocolVersion < protocolVersion:
            print("Unable to connect to the specified server.")
            print("The server you tried to connect to is outdated! Using protocol version " + str(protocolVersion) + " while server is on server protocol version " + str(serverProtocolVersion) + ".")
            print("Program will terminate in 5 seconds...")
            time.sleep(5)
            exit()
    except Exception as err:
        print("Unable to connect to the specified server. The following exception has occurred: " + str(err))
        print("Program will terminate in 5 seconds...")
        time.sleep(5)
        exit()

print("----------------------------------------")
print("Type your message, then press 'Enter' to send.")

def SendMsg():
    while True:
        msg = input()
        if msg:
            msg = msg.encode("utf-8")
            msg_header = f"{len(msg):<{HEADER_LENGTH}}".encode("utf-8")
            s.send(msg_header + msg)

def ReceiveMsg():
    while True:
        try:
            while True:
                username_header = s.recv(HEADER_LENGTH)
                if not len(username_header):
                    print("The connection was closed by the server!")
                    print("Program will terminate in 5 seconds...")
                    time.sleep(5)
                    exit()
                username_length = int(username_header.decode("utf-8").strip())
                usernamedecode = s.recv(username_length).decode("utf-8")
                msg_header = s.recv(HEADER_LENGTH)
                msg_length = int(msg_header.decode("utf-8").strip())
                msg = s.recv(msg_length).decode("utf-8")
                print(f"{usernamedecode}: {msg}")
        except IOError as e:
            if errno != errno.EAGAIN and e.errno != errno.EWOULDBLOCK:
                print("The following IO exception has occurred: {}".format(str(e)))
                print("Program will terminate in 5 seconds...")
                time.sleep(5)
                exit()
            continue
        except Exception as e:
            print("The following exception has occurred: {}".format(str(e)))
            print("Program will terminate in 5 seconds...")
            time.sleep(5)
            exit()

sendmessage = threading.Thread(target=SendMsg)
sendmessage.start()
receivemessage = threading.Thread(target=ReceiveMsg)
receivemessage.start()
