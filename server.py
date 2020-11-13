# GitHub: https://github.com/Kooldude183/PythonChatClient

import socket
import select
HEADER_LENGTH = 10

IP = "0.0.0.0"
PORT = 25000
version = "0.1.13"                    # Build date: Nov. 13, 2020
protocolVersion = 12                  # Server and client protocol version must match

serverID = "server"     # The server ID shows on clients when connecting to the server
cooldown = 0                         # Cooldown in seconds up to 3 digits. Set to 0 to disable. This cooldown is used for all clients connected to this server.

# initialzie socket, set socket options to reuse address if necessary
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

# bind to port and begin listening
s.bind((IP, PORT))
s.listen()

# list of all sockets, including server
sockets_list = [s]

# all connected clients
clients = {}

# initialization messages
print(f"Server running on port {PORT}")

# handles recieving messages
def receive_msg(client_socket):
    try:
        msg_header = client_socket.recv(HEADER_LENGTH)

        if not len(msg_header):
            return False

        message_length = int(msg_header.decode("utf-8").strip())

        return {"header": msg_header, "data": client_socket.recv(message_length)}
    except:
        return False

while True:
    # lists all sockets that have been notified
    # if a client socket is notified, that means a new message has been detected
    # if a server socket is notified, that means a new client has connected.
    read_sockets, _, exception_sockets = select.select(sockets_list, [], sockets_list)

    for notified_socket in read_sockets:

        # if notified socket is server
        if notified_socket == s:

            # accept connection
            client_socket, client_address = s.accept()
            user = receive_msg(client_socket)

            if user is False:
                continue
            
            sockets_list.append(client_socket)
            clients[client_socket] = user
            client_socket.send(str.encode("\n".join([str(protocolVersion), serverID, str(cooldown)])))
            userconnected = user["data"].decode("utf-8")

            # server notification message
            print("Connected to {} on IP {}".format(userconnected, client_address))

            # send join notification to all clients
            user = clients[client_socket]
            for client_socket_2 in clients:
                if client_socket_2 != client_socket:
                    client_socket_2.send(user["header"] + user["data"] + f"{-1:<{HEADER_LENGTH}}".encode("utf-8"))

        # if notified socket is client
        else:
            msg = receive_msg(notified_socket)
            if msg is False:
                print("Connection closed on {}".format(clients[notified_socket]["data"].decode('utf-8')))

                # send leave notification to all clients
                user = clients[notified_socket]
                for client_socket_2 in clients:
                    if client_socket_2 != notified_socket:
                        client_socket_2.send(user["header"] + user["data"] + f"{-2:<{HEADER_LENGTH}}".encode("utf-8"))

                sockets_list.remove(notified_socket)
                del clients[notified_socket]
                continue
            
            user = clients[notified_socket]
            print(f'Received message from {user["data"].decode("utf-8")}: {msg["data"].decode("utf-8")}')
            for client_socket in clients:
                if client_socket != notified_socket:
                    client_socket.send(user["header"] + user["data"] + msg["header"] + msg["data"])

    # if notified socket errors
    for notified_socket in exception_sockets:
        sockets_list.remove(notified_socket)
        del clients[notified_socket]