import socket
import threading

client = socket.socket(socket.AF_INET, socket.SOCK_STREAM) # initialisation du client avec le protocole TCP et l'adresse IPV4
host, port = '127.0.0.1', 8921 # host = adresse IP du serveur, port = port d'écoute du serveur
exit_flag = False # flag de sortie du programme

try: # On essaie de se connecter au serveur
    client.connect((host, port))
except Exception as e: # Si une erreur est levée, on quitte le programme
    print(f"Error connecting to the server: {e}")
    exit()

def receive():
    """
    Fonction qui écoute les messages envoyés par le serveur
    """
    global exit_flag # On utilise la variable globale définie dans le programme principal
    client.settimeout(1)  # On définit un timeout de 1 seconde pour éviter que le programme ne se bloque

    while not exit_flag: # Boucle infinie pour écouter les messages du serveur
        try: # On essaie de recevoir un message du serveur
            message = client.recv(1024).decode("utf-8")
            if not message: # Si le message est vide, le serveur a fermé la connexion
                break
            print(message) # On affiche le message
            if "Game over" in message: # Si le message contient "Game over", on quitte le chat
                exit_flag = True # On définit le flag de sortie à True
                break
        except socket.timeout: # Si le timeout est dépassé, on passe à la suite
            pass
        except Exception as e: # Si une autre erreur est levée, on quitte la boucle
            print(f"Error receiving message: {e}")
            break

try: # On essaie de se connecter au serveur
    receive_thread = threading.Thread(target=receive) # On crée un thread pour écouter les messages du serveur
    receive_thread.start() # On démarre le thread

    while True: # Boucle infinie pour envoyer des messages au serveur
        choice = input()
        client.send(choice.encode("utf-8")) # On envoie le choix au serveur

        if choice.lower() == "quit": # Si le choix est 'quit', on quitte le chat
            print("Exiting...")
            exit_flag = True
            receive_thread.join()
            client.close()
            break

except KeyboardInterrupt:
    print("Exiting...")
    exit_flag = True
    receive_thread.join()
    client.close()
