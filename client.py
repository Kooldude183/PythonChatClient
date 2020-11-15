# GitHub: https://github.com/Kooldude183/PythonChatClient

from datetime import time
import socket
from socket import error
import time
import threading
import errno
global s
import tkinter as tk
import requests
import os
HEADER_LENGTH = 10

version = "0.1.16"    # Build date: Nov. 13, 2020
protocolVersion = 12  # Do not change! Server and client protocol versions must be the same. - Colin

#AUTOUPDATER
def AutoUpdater():
    print("Running auto-updater...")
    file = os.path.basename(__file__)
    filename, ext = os.path.splitext(file)
    if ext == ".py":
        r = requests.get('https://raw.githubusercontent.com/Kooldude183/PythonChatClient/main/client.py')
        text_file = open(file, "w")
        text_file.write(r.text)
        text_file.close()
    elif ext == ".exe":
        r = requests.get('https://raw.githubusercontent.com/Kooldude183/PythonChatClient/main/dist/client.exe')
        text_file = open(file, "w")
        text_file.write(r.text)
        text_file.close()
    else:
        print("Unsupported file type. Unable to start program.")
        print("Program will terminate in 5 seconds...")
        time.sleep(5)
        exit()

AutoUpdater()

gui = tk.Tk()
gui.geometry("500x200")

print("Chat Client v" + str(version))

def setUsername():
    global username
    global username_header
    username = usernametext.get().encode("utf-8")
    username_header = f"{len(username):<{HEADER_LENGTH}}".encode("utf-8")

    gui.destroy()

serverselectlbl = tk.Label(gui, text = "Input Username", font = ("Calibri", 16, "bold"))
serverselectlbl.pack()
usernametext = tk.Entry()
usernametext.pack()
usernamebutton = tk.Button(gui, text="Login", command=setUsername, height = 1, width = 15)
usernamebutton.pack()

gui.mainloop()

try:
    username_header
except Exception as e:
    print("Username was not specified! Please enter a username.")
    print("Program will terminate in 5 seconds...")
    time.sleep(5)
    exit()

def setServerMain():
    global serverip
    serverip = "104.156.229.228"
    gui.destroy()

def connectToOtherServer(address):
    global serverip
    serverip = address
    gui.destroy()

def setOtherServer():
    global buttonClicked
    if buttonClicked == False:
        ipaddrfield = tk.Entry()
        ipaddrfield.pack()
        connectbutton = tk.Button(gui, text="Connect", command=lambda: connectToOtherServer(ipaddrfield.get()), height = 2, width = 15)
        connectbutton.pack()
        buttonClicked = True

gui = tk.Tk()
gui.geometry("500x200")

buttonClicked = False
serverselectlbl = tk.Label(gui, text = "Select Server", font = ("Calibri", 16, "bold"))
serverselectlbl.pack()
mainserverbutton = tk.Button(gui, text="Main Server", command=setServerMain, height = 1, width = 15)
mainserverbutton.pack()
otherserverbutton = tk.Button(gui, text="Enter IP Address", command=setOtherServer, height = 1, width = 15)
otherserverbutton.pack()

gui.mainloop()

print("----------------------------------------")
print("Connecting to the server...")

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

try:
    serverip
except Exception as e:
    print("Server IP address was not specified! Please enter an IP address.")
    print("Program will terminate in 5 seconds...")
    time.sleep(5)
    exit()

while True:
    try:
        s.connect((serverip, 25000))
        s.send(username_header + username)
        pvToString, serverID, cooldownToString = [str(i) for i in s.recv(1024).decode('utf-8').split('\n')]
        serverProtocolVersion = int(pvToString)
        if serverProtocolVersion == protocolVersion:
            print("Connected to the server with identification \"" + serverID + "\"")
            global cooldown
            cooldown = float(cooldownToString)
            if cooldown != 0:
                print("Cooldown for this server is " + str(cooldown) + " seconds")
            else:
                print("Cooldown for this server is disabled")
            break
        elif serverProtocolVersion > protocolVersion:
            print("Unable to connect to the specified server.")
            print("Your client is outdated! Using protocol version " + str(protocolVersion) + " instead of server protocol version " + str(serverProtocolVersion) + ". You can find the latest release here: https://github.com/Kooldude183/PythonChatClient/releases")
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
        msg = input("> ")
        if msg:
            msg = msg.encode("utf-8")
            msg_header = f"{len(msg):<{HEADER_LENGTH}}".encode("utf-8")
            s.send(msg_header + msg)
        time.sleep(cooldown)

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

                # normal message
                if(msg_length >= 0):
                    msg = s.recv(msg_length).decode("utf-8")
                    print(f"{usernamedecode}: {msg}")

                # leave / join message
                elif(msg_length == -1):
                    print(f"{usernamedecode} has connected.")
                
                elif(msg_length == -2):
                    print(f"{usernamedecode} has disconnected.")

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