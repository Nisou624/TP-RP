import socket
import threading

client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

host, port = '127.0.0.1', 8921
name = "";
exit_flag = False




try:
    client.connect((host, port))
except Exception as e:
    print(f"Error connecting to the server: {e}")
    exit()



def listen():
    global state, available, name, exit_flag
    client.settimeout(1)  # Set a timeout for the socket

    while not exit_flag:
        try:
            message = client.recv(1024).decode("utf-8")
            if not message:
                break
            print(message)
        except socket.timeout:
            pass
        except Exception as e:
            print(f"Error receiving message: {e}")
            break



try:
    receive_thread = threading.Thread(target=listen)
    receive_thread.start()

    while True:
        message = input()
        if message.lower() == "quit":
            print("Exiting...")
            exit_flag = True
            client.send("quit".encode("utf-8"))
            receive_thread.join()
            client.close()
            break
        else:
            client.send(message.encode("utf-8"))

except KeyboardInterrupt:
    print("Exiting...")
    exit_flag = True
    receive_thread.join()
    client.close()

