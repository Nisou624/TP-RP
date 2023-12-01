import socket
import select
import threading

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

host, port = "127.0.0.1", 8921

server.bind((host, port))
server.listen(2)

continue_playing = True

p1_pass, p2_pass = False, False
connected = True
socket_list = [server]
clients = {}
player_choices = {}

def send_to_player(player_num, message):
    player_socket = clients[f"Player{player_num}"]
    try:
        player_socket.send(message.encode("utf-8"))
    except Exception as e:
        print(f"Error sending message to Player{player_num}: {e}")

def handle_game(player1, player2):
    global continue_playing, p1_pass, p2_pass
    choices = ["rock", "paper", "scissors"]

    while continue_playing:
        p1_pass, p2_pass = False, False  # Reset the pass flags for each round

        send_to_player(1, "Welcome to the Rock-Paper-Scissors game! Please enter your choice (rock, paper, scissors, or quit):")
        send_to_player(2, "Waiting for Player 1 to make a choice...\n")
        while not p1_pass:
            choice_player1 = player1.recv(1024).decode("utf-8")
            player_choices["Player1"] = choice_player1
            if choice_player1.lower() in choices:
                p1_pass = True
            else:
                send_to_player(1, "Invalid choice. Please enter your choice (rock, paper, scissors, or quit):\n")

        send_to_player(2, "Welcome to the Rock-Paper-Scissors game! Please enter your choice (rock, paper, scissors, or quit):")
        send_to_player(1, "Waiting for Player 2 to make a choice...\n")
        while not p2_pass:
            choice_player2 = player2.recv(1024).decode("utf-8")
            player_choices["Player2"] = choice_player2
            if choice_player2.lower() in choices:
                p2_pass = True
            else:
                send_to_player(2, "Invalid choice. Please enter your choice (rock, paper, scissors, or quit):\n")

        if "quit" in [choice_player1.lower(), choice_player2.lower()]:
            break

        send_to_player(1, f"Player 1 chose: {choice_player1}\n")
        send_to_player(2, f"Player 2 chose: {choice_player2}\n")

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

        send_to_player(1, "Game over. Thanks for playing! (if you want to play again enter 'again')\n")
        send_to_player(2, "Game over. Thanks for playing! (if you want to play again enter 'again')\n")
        p1_again = player1.recv(1024).decode("utf-8")
        p2_again = player2.recv(1024).decode("utf-8")
        if p1_again.lower() == "again" and p2_again.lower() == "again":
            continue_playing = True
        else:
            continue_playing = False

while connected:
    read_list, _, _ = select.select(socket_list, [], [])
    for sock in read_list:
        if sock == server:
            client, address = server.accept()
            socket_list.append(client)

            player_num = len(clients) + 1
            clients[f"Player{player_num}"] = client
            print(f"Player {player_num} connected from {address}\n")

            if player_num == 1:
                print("Waiting for Player 2 to connect...\n")
            elif player_num == 2:
                print("Both players connected. Starting the game...\n")
                game_thread = threading.Thread(target=handle_game, args=(clients["Player1"], clients["Player2"]))
                game_thread.start()

        else:
            pass
