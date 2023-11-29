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

def receive():
    global exit_flag
    client.settimeout(1)  # Set a timeout for the socket

    while not exit_flag:
        try:
            message = client.recv(1024).decode("utf-8")
            if not message:
                break
            print(message)

            # If the message indicates the game is over, exit the loop
            if "Game over" in message:
                exit_flag = True
                break
        except socket.timeout:
            pass
        except Exception as e:
            print(f"Error receiving message: {e}")
            break

try:
    receive_thread = threading.Thread(target=receive)
    receive_thread.start()

    while True:
        choice = input()
        client.send(choice.encode("utf-8"))

        if choice.lower() == "quit":
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
