import socket
import select

serveur = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

host, port = "127.0.0.1", 8921

serveur.bind((host, port))
serveur.listen(4)

connected = True
socketLs = [serveur]


print("Welcome to Summonners rift")


while connected:
    liste_lue, liste_acce_Ecrit, exception = select.select(socketLs, [], socketLs)

    for socket_obj in liste_lue:

        if socket_obj is serveur:
            client, adresse = serveur.accept()
            socketLs.append(client)

        else:
            donnees_recus = socket_obj.recv(128).decode("utf-8")
            if donnees_recus:
                print(donnees_recus)

            else:
                socketLs.remove(socket_obj)
                print("Un participant est deconnecte")
                print(f"{len(socketLs) - 1} participants restants")