import socket
import select
import threading

serveur = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

host, port = "127.0.0.1", 8921

serveur.bind((host, port))
serveur.listen(4)

connected = True
socketLs = [serveur]
clients = {}


def handle_client(client_socket, address):
    client_socket.send("Welcome to the chatroom! Please enter your username:".encode("utf-8"))
    nom = client_socket.recv(1024).decode("utf-8")

    print(f"New connection from {address}, username: {nom}")
    broadcast(f"{nom} has joined the chat.", client_socket)

    clients[nom] = client_socket
    update_clients_list()

    while True:
        try:
            message = client_socket.recv(1024).decode("utf-8")
            if message:
                if message.lower() == 'quit':
                    print(f"{nom} has exited the chat.\n")
                    client_socket.close()
                    del clients[nom]
                    broadcast(f"{nom} has left the chat.\n")
                    update_clients_list()
                    break
                elif message.startswith('@'):
                    recipient, private_msg = message[1:].split(':', 1)
                    if recipient in clients:
                        p2pMsg(f"{nom} (private): {private_msg}", clients[recipient])
                    else:
                        client_socket.send(f"User '{recipient}' not found or offline.".encode("utf-8"))
                else:
                    broadcast(f"{nom} (groupChat): {message}", client_socket)

            else:
                print(f"Connection closed for {address}, username: {nom}")
                client_socket.close()
                del clients[nom]
                broadcast(f"{nom} has left the chat.\n")
                update_clients_list()
                break
        except Exception as e:
            print(f"Error: {e}")
            break


def broadcast(message, socket=None):
    for client_socket in clients.values():
        if socket is None or client_socket != socket:
            try:
                client_socket.send(message.encode("utf-8"))
            except Exception as e:
                print(f"Error broadcasting message: {e}")


def p2pMsg(message, receiver):
    try:
        receiver.send(message.encode("utf-8"))
    except Exception as e:
        print(f"Error sending the message: {e}")

def update_clients_list():
    client_list = ", ".join(clients.keys())
    broadcast(f"Connected clients: {client_list}")


while connected:
    liste_lue, liste_acce_Ecrit, exception = select.select(socketLs, [], socketLs)

    for socket_obj in liste_lue:
        if socket_obj is serveur:
            client, adresse = serveur.accept()
            socketLs.append(client)

            client_thread = threading.Thread(target=handle_client, args=(client, adresse))
            client_thread.start()

        else:
            # Existing clients are handled by the threads, so we don't need to do anything here.
            pass
