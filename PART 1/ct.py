"""
ct = client threaded
"""

import socket
import threading

client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

host, port = '127.0.0.1', 8921
exit_flag = False




try:
    client.connect((host, port))
except Exception as e:
    print(f"Error connecting to the server: {e}")
    exit()



def listen():
    """
    Fonction qui écoute les messages envoyés par le serveur
    """
    global state, available, name, exit_flag # On utilise les variables globales définies dans le programme principal
    client.settimeout(1) # On définit un timeout de 1 seconde pour éviter que le programme ne se bloque

    while not exit_flag: # Boucle infinie pour écouter les messages du serveur
        try: # On essaie de recevoir un message du serveur
            message = client.recv(1024).decode("utf-8") # On reçoit le message du serveur
            if not message: # Si le message est vide, le serveur a fermé la connexion
                break
            print(message) # On affiche le message
        except socket.timeout: # Si le timeout est dépassé, on passe à la suite
            pass
        except Exception as e: # Si une autre erreur est levée, on quitte la boucle
            print(f"Error receiving message: {e}")
            break



try: # On essaie de se connecter au serveur
    receive_thread = threading.Thread(target=listen) # On crée un thread pour écouter les messages du serveur
    receive_thread.start() # On démarre le thread

    while True: # Boucle infinie pour envoyer des messages au serveur
        message = input() # On demande à l'utilisateur d'entrer un message
        if message.lower() == "quit": # Si le message est 'quit', on quitte le chat
            print("Exiting...") # On affiche un message
            exit_flag = True # On définit le flag de sortie à True
            client.send("quit".encode("utf-8")) # On envoie un message au serveur pour lui indiquer que l'on quitte le chat
            receive_thread.join() # On attend que le thread se termine
            client.close() # On ferme la connexion avec le serveur
            break
        else: # Sinon, on envoie le message au serveur
            client.send(message.encode("utf-8"))
            
except KeyboardInterrupt:
    print("Exiting...")
    exit_flag = True
    receive_thread.join()
    client.close()

