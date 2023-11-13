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
    broadcast(f"{nom} has joined the chat.")

    clients[nom] = client_socket

    while True:
        try:
            message = client_socket.recv(1024).decode("utf-8")
            if message:
                if message.lower() == 'quit':
                    print(f"{nom} has exited the chat.")
                    client_socket.close()
                    del clients[nom]
                    broadcast(f"{nom} has left the chat.")
                    break
                else:
                    broadcast(f"{nom}: {message}")
            else:
                print(f"Connection closed for {address}, username: {nom}")
                client_socket.close()
                del clients[nom]
                broadcast(f"{nom} has left the chat.")
                break
        except Exception as e:
            print(f"Error: {e}")
            break


def broadcast(message):
    for client in clients.values():
        try:
            client.send(message.encode("utf-8"))
        except Exception as e:
            print(f"Error broadcasting message: {e}")


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
