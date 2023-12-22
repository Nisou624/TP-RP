import socket
import select
import threading

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

host, port = "127.0.0.1", 8921

server.bind((host, port))
server.listen(2)

continue_playing = True # flag de sortie du programme

p1_pass, p2_pass = False, False # flags pour vérifier si les joueurs ont entré un choix valide
connected = True # flag pour vérifier si les joueurs sont connectés
socket_list = [server] # liste des sockets à écouter
clients = {} # dictionnaire des clients connectés
player_choices = {} # dictionnaire des choix des joueurs

def send_to_player(player_num, message):
    """
    Fonction qui envoie un message à un joueur

     Args:
            player_num (int): numéro du joueur
            message (str): message à envoyer
    """
    player_socket = clients[f"Player{player_num}"] # récupération du socket du joueur
    try: # On essaie d'envoyer le message au joueur
        player_socket.send(message.encode("utf-8"))
    except Exception as e: # Si une erreur est levée, on quitte la boucle
        print(f"Error sending message to Player{player_num}: {e}")

def handle_game(player1, player2):
    """
    Fonction qui gère le jeu
    
     Args:
            player1 (socket): socket du joueur 1
            player2 (socket): socket du joueur 2
    """
    global continue_playing, p1_pass, p2_pass, p1_again, p2_again # On utilise les variables globales définies dans le programme principal
    choices = ["rock", "paper", "scissors"] # liste des choix possibles

    while continue_playing: # Boucle infinie pour gérer le jeu
        p1_pass, p2_pass = False, False  # On réinitialise les flags

        # On envoie un message à chaque joueur pour lui demander son choix
        send_to_player(1, "Welcome to the Rock-Paper-Scissors game! Please enter your choice (rock, paper, scissors, or quit):")
        send_to_player(2, "Waiting for Player 1 to make a choice...\n")
        while not p1_pass: # Boucle pour attendre que le joueur 1 entre un choix valide
            choice_player1 = player1.recv(1024).decode("utf-8") # On reçoit le choix du joueur 1
            player_choices["Player1"] = choice_player1 # On ajoute le choix du joueur 1 dans le dictionnaire des choix
            if choice_player1.lower() in choices: # Si le choix du joueur 1 est valide, on définit le flag à True
                p1_pass = True
            else: # Sinon, on lui demande de rentrer un choix valide
                send_to_player(1, "Invalid choice. Please enter your choice (rock, paper, scissors, or quit):\n")

        # On envoie un message à chaque joueur pour lui demander son choix
        send_to_player(2, "Welcome to the Rock-Paper-Scissors game! Please enter your choice (rock, paper, scissors, or quit):")
        send_to_player(1, "Waiting for Player 2 to make a choice...\n")
        while not p2_pass: # Boucle pour attendre que le joueur 2 entre un choix valide
            choice_player2 = player2.recv(1024).decode("utf-8") # On reçoit le choix du joueur 2
            player_choices["Player2"] = choice_player2 # On ajoute le choix du joueur 2 dans le dictionnaire des choix
            if choice_player2.lower() in choices: # Si le choix du joueur 2 est valide, on définit le flag à True
                p2_pass = True
            else: # Sinon, on lui demande de rentrer un choix valide
                send_to_player(2, "Invalid choice. Please enter your choice (rock, paper, scissors, or quit):\n")

        if "quit" in [choice_player1.lower(), choice_player2.lower()]: # Si l'un des joueurs a entré 'quit', on quitte le jeu
            break 

        # On envoie un message à chaque joueur pour lui indiquer le choix de l'autre joueur
        send_to_player(1, f"Player 1 chose: {choice_player1}\n")
        send_to_player(2, f"Player 2 chose: {choice_player2}\n")

        """
        On compare les choix des joueurs pour déterminer le gagnant
        
        Si les choix sont identiques, c'est une égalité
        
        Si le joueur 1 a choisi 'rock' et le joueur 2 a choisi 'scissors', le joueur 1 gagne
        
        Si le joueur 1 a choisi 'paper' et le joueur 2 a choisi 'rock', le joueur 1 gagne
        
        Si le joueur 1 a choisi 'scissors' et le joueur 2 a choisi 'paper', le joueur 1 gagne
        
        Sinon, le joueur 2 gagne
        
        On envoie un message à chaque joueur pour lui indiquer le gagnant
        """
        if choice_player1.lower() == choice_player2.lower():
            send_to_player(1, "It's a tie!")
            send_to_player(2, "It's a tie!")
        elif (choice_player1.lower() == "rock" and choice_player2.lower() == "scissors") or \
             (choice_player1.lower() == "paper" and choice_player2.lower() == "rock") or \
             (choice_player1.lower() == "scissors" and choice_player2.lower() == "paper"):
            send_to_player(1, "Player 1 wins!\n")
            send_to_player(2, "Player 1 wins!\n")
        else:
            send_to_player(1, "Player 2 wins!\n")
            send_to_player(2, "Player 2 wins!\n")

        send_to_player(1, "Game over. Thanks for playing!\n")
        send_to_player(2, "Game over. Thanks for playing!\n")
        

while connected: # Boucle infinie pour écouter les connexions des clients
    read_list, _, _ = select.select(socket_list, [], []) # On écoute les sockets
    for sock in read_list: # Pour chaque socket
        if sock == server: # Si le socket est celui du serveur, on accepte la connexion
            client, address = server.accept()
            socket_list.append(client) # On ajoute le socket du client dans la liste des sockets à écouter

            player_num = len(clients) + 1 # On définit le numéro du joueur
            clients[f"Player{player_num}"] = client # On ajoute le client dans le dictionnaire des clients connectés
            print(f"Player {player_num} connected from {address}\n") # On affiche l'adresse IP et le port du client

            if player_num == 1: # Si le joueur est le premier à se connecter, on lui envoie un message pour lui indiquer qu'il doit attendre le deuxième joueur
                print("Waiting for Player 2 to connect...\n")
            elif player_num == 2: # Si le joueur est le deuxième à se connecter, on lui envoie un message pour lui indiquer qu'il peut commencer le jeu
                print("Both players connected. Starting the game...\n")
                game_thread = threading.Thread(target=handle_game, args=(clients["Player1"], clients["Player2"])) # On crée un thread pour gérer le jeu
                game_thread.start() # On démarre le thread

        else:
            pass
