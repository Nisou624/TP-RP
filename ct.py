import socket
import threading

#ct = client threaded

client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

host, port = '127.0.0.1', 8921

try:
    client.connect((host, port))
except Exception as e:
    print(f"Error connecting to the server: {e}")
    exit()

#nom = input("Enter your username: ")
#client.send(nom.encode("utf-8"))

def receive_messages():
    while True:
        try:
            message = client.recv(1024).decode("utf-8")
            if not message:
                break
            print(message)
        except Exception as e:
            print(f"Error receiving message: {e}")
            break

try:
    receive_thread = threading.Thread(target=receive_messages)
    receive_thread.start()

    while True:
        message = input()
        client.send(message.encode("utf-8"))

except KeyboardInterrupt:
    print("Exiting...")
finally:
    client.close()
    receive_thread.join()  # Wait for the receive thread to finish
