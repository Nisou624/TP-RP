import socket
import threading
import inquirer

client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

host, port = '127.0.0.1', 8921

available = ["group Chat", "quit"]
state = "disconnected"
selected_option = "";
name = "";
exit_flag = False

private_welcome_printed = False
cg_welcome_printed = False

def ask_message():
    global state, cg_welcome_printed, private_welcome_printed
    message = input()

    if message.lower() == "quit":
        state = "idle"
        private_welcome_printed = False
        cg_welcome_printed = False
    else:
        return message

try:
    client.connect((host, port))
except Exception as e:
    print(f"Error connecting to the server: {e}")
    exit()

def get_choices():
    global state, available
    if state == "idle":
        return available
    elif state == "private":
        return ["Quit Private Chat"] + available
    elif state == "cg":
        return ["Quit Group Chat"] + available


def receive_messages():
    global state, available, name, exit_flag
    client.settimeout(1)  # Set a timeout for the socket

    while not exit_flag:
        try:
            message = client.recv(1024).decode("utf-8")
            if not message:
                break
            print(message)
            if message.startswith("Connected clients:"):
                # Parse the user list into an array
                connected_users = message.split(":")[1].strip().split(", ")
                if name in connected_users:
                    connected_users.remove(name)
                available = connected_users + ["group chat", "quit"]
            elif message.startswith("Welcome"):
                name = ask_message()
                client.send(name.encode("utf-8"))
                state = "idle"
        except socket.timeout:
            pass
        except Exception as e:
            print(f"Error receiving message: {e}")
            break



try:
    receive_thread = threading.Thread(target=receive_messages)
    receive_thread.start()

    while True:
        if state == "idle":
            questions = [
                inquirer.List('choice',
                  message='Que voulez-vous faire',
                  choices=get_choices()),
            ]
            answers = inquirer.prompt(questions)
            selected_option = answers['choice']
            #print(f"selected option is {selected_option}")
            if selected_option.lower() == "quit":
                state = "quit"
            elif selected_option.lower() == "group chat":
                state = "cg"
            else:
                state = "private"

        elif state == "private":
            if not private_welcome_printed:
                print(f"you are in a private room with {selected_option}\n")
                private_welcome_printed = True
            message = ask_message()
            if message:
                message = f"@{selected_option}:" + message
                client.send(message.encode("utf-8"))
        elif state == "cg":  #cg = chatgroup
            if not cg_welcome_printed:
                print("welcome in the GroupChat\n")
                cg_welcome_printed = True
            message = ask_message()
            if message:
                client.send(message.encode("utf-8"))
        elif state == "quit":
            print("Exiting...")
            exit_flag = True
            client.send("quit".encode("utf-8"))
            receive_thread.join()
            client.close()
            break

except KeyboardInterrupt:
    print("Exiting...")
#finally:
#    client.close()
#    receive_thread.join()  # Wait for the receive thread to finish
