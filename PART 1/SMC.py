"""
SMC = serveur multi clients :
    - Un serveur qui peut accepter plusieurs clients
    - Un client peut envoyer un message à tous les autres clients
    - Un client peut envoyer un message privé à un autre client
    - Un client peut quitter le chat
"""


import socket
import select
import threading

serveur = socket.socket(socket.AF_INET, socket.SOCK_STREAM) # initialisation du serveur avec le protocole TCP et l'adresse IPV4

host, port = "127.0.0.1", 8921 # host = adresse IP du serveur, port = port d'écoute du serveur

serveur.bind((host, port)) # le serveur écoute sur l'adresse IP et le port spécifié
serveur.listen(4) # le serveur peut accepter jusqu'à 4 clients

connected = True
socketLs = [serveur] # liste des sockets à écouter
clients = {} # dictionnaire des clients connectés


def listen_to_clients(client_socket, address):
    """
    Fonction qui écoute les messages envoyés par les clients

     Args:
            client_socket (socket): socket du client
            address (tuple): adresse IP et port du client
    """
    client_socket.send("Welcome to the chatroom! Please enter your username:".encode("utf-8")) # envoi d'un message au client
    nom = client_socket.recv(1024).decode("utf-8") # réception du nom du client

    print(f"New connection from {address}, username: {nom}\n") # affichage de l'adresse IP et du port du client
    broadcast(f"{nom} has joined the chat.\n", client_socket) # envoi d'un message à tous les clients pour indiquer qu'un nouveau client a rejoint le chat

    clients[nom] = client_socket # ajout du client dans le dictionnaire des clients connectés

    while True: # boucle infinie pour écouter les messages du client
        try:
            message = client_socket.recv(1024).decode("utf-8") # réception du message du client
            if message: # si le message n'est pas vide
                if message.lower() == 'quit': # si le message est 'quit', le client a quitté le chat
                    print(f"{nom} has exited the chat.\n") # affichage du message
                    client_socket.close() # fermeture de la connexion avec le client
                    del clients[nom] # suppression du client dans le dictionnaire des clients connectés
                    broadcast(f"{nom} has left the chat.\n") # envoi d'un message à tous les clients pour indiquer qu'un client a quitté le chat
                    break
                elif message.startswith('@'): # si le message commence par '@', le client veut envoyer un message privé à un autre client
                    recipient, private_msg = message[1:].split(':', 1)
                    if recipient in clients:
                        p2pMsg(f"{nom} (private): {private_msg}", clients[recipient])
                    else:
                        client_socket.send(f"User '{recipient}' not found or offline.".encode("utf-8"))
                else: # sinon, le client veut envoyer un message à tous les autres clients
                    broadcast(f"{nom} (groupChat): {message}", client_socket)

            else: # si le message est vide, le client a quitté le chat
                print(f"Connection closed for {address}, username: {nom}")
                client_socket.close()
                del clients[nom]
                broadcast(f"{nom} has left the chat.\n")
                break
        except Exception as e:
            print(f"Error: {e}")
            break


def broadcast(message, socket=None):
    """
    Fonction qui envoie un message à tous les clients connectés
    
     Args:
            message (str): message à envoyer
            socket (socket): socket du client qui a envoyé le message
    """
    for client_socket in clients.values(): # pour chaque client connecté
        if socket is None or client_socket != socket: # si le client n'est pas celui qui a envoyé le message
            try: # on essaye d'envoyer le message au client
                client_socket.send(message.encode("utf-8"))
            except Exception as e: # si on n'a pas pu envoyer le message, on affiche l'erreur
                print(f"Error broadcasting message: {e}")


def p2pMsg(message, receiver):
    """
    Fonction qui envoie un message privé à un client
    
     Args:
            message (str): message à envoyer
            receiver (socket): socket du client qui va recevoir le message
    """
    try: # on essaye d'envoyer le message au client
        receiver.send(message.encode("utf-8"))
    except Exception as e: # si on n'a pas pu envoyer le message, on affiche l'erreur
        print(f"Error sending the message: {e}")



while connected: # boucle infinie pour accepter les connexions des clients
    liste_lue, liste_acce_Ecrit, exception = select.select(socketLs, [], socketLs) # on écoute les sockets

    for socket_obj in liste_lue: # pour chaque socket à écouter
        if socket_obj is serveur: # si le socket est celui du serveur, on accepte la connexion du client
            client, adresse = serveur.accept()
            socketLs.append(client) # on ajoute le socket du client dans la liste des sockets à écouter

            client_thread = threading.Thread(target=listen_to_clients, args=(client, adresse)) # on crée un thread pour écouter les messages du client
            client_thread.start() # on démarre le thread

        else:
            pass
