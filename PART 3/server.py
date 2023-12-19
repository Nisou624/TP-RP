import socket
from _thread import *
import sys
from const import *
import random

server = "127.0.0.1"
port = 8921

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

try:
    s.bind((server, port))
except socket.error as e:
    print(str(e))

players = []

games = []
    
s.listen(2)
print("Waiting for a connection, Server Started")

def read_pos(str):
    str = str.split(",")
    return int(str[0]), int(str[1])

def make_pos(tup):
    return str(tup[0]) + "," + str(tup[1])

pos = [100, 1100]
map = random.choice([0, 1, 2])

def player_id(socket):
    return players.index(socket)

def broadcast(message, socket=None):
    for client_socket in players:
        if socket is None or client_socket != socket:
            try:
                client_socket.send(message.encode("utf-8"))
                print("broadcasted")
            except Exception as e:
                print(f"Error broadcasting message: {e}")



def listen_to_clients(socket, address):
    global map
    p1_done = False
    p2_done = False
    while True:
        if not p1_done and  not p2_done:
            if player_id(socket) == 0 and not p1_done:
                socket.send("player : 1.".encode("utf-8"))
                p1_pos = "pos : " + make_pos((pos[player_id(socket)], HEIGHT - 96 - TERRAIN_SIZES[map])) + "."
                socket.send(p1_pos.encode("utf-8"))
                print("sent p1 his pos")
            else:
                socket.send("player : 2 .".encode("utf-8"))
                p2_pos = "pos : " + make_pos((pos[player_id(socket)], HEIGHT - 96 - TERRAIN_SIZES[map])) + "."
                socket.send(p2_pos.encode("utf-8"))
                p1_pos = "last_pos : " + make_pos((pos[0], HEIGHT - 96 - TERRAIN_SIZES[map])) + "."
                print("will send the p1 pos to p2")
                socket.send(p1_pos.encode("utf-8"))
                print("sent the p1 pos to p2")
                p2_pos = "last_pos : " + make_pos((pos[player_id(socket)], HEIGHT - 96 - TERRAIN_SIZES[map])) + "."
                print("will send the p2 pos to p1")
                players[0].send(p2_pos.encode("utf-8"))
                print("sent the p2 pos to p1")

            message = socket.recv(4096).decode("utf-8").split(".")[0]
            if message.strip() == "received":
                if player_id(socket) == 0:
                    p1_done = True
                    print("received from 1")
                else:
                    p2_done = True
                    print("received from 2")
        else:
            #print("listening to moves")
            data = socket.recv(4096).decode("utf-8").split(".")[0]
            if data.split(":")[0].strip() == "move":
                print("received move infos")
                target = int(data.split(":")[1].strip()) - 1
                players[target].send(data.encode("utf-8"))
                print(f"sent move infos to  player {target}")



            




while True:
    conn, addr = s.accept()
    players.append(conn)
    start_new_thread(listen_to_clients, (conn, addr))



'''
def listen_to_clients(socket, address):
    global map
    received_hello = None
    ingame = False
    while True:
        if not ingame:
            
            if player_id(socket) == 0:
                if received_hello == None:
                    socket.send("welcome : Bienvenue".encode("utf-8"))
                    rec = socket.recv(1024).decode("utf-8")
                    if isinstance(rec, Multiplayer_state) or rec != "":
                        received_hello = rec
                else:
                    print("map : Requesting the map\n")
                    socket.send("map : Requesting the map".encode("utf-8"))
                    if str(map) == "-1":
                        map = socket.recv(1024).decode("utf-8")
                        if not ':' in str(map):
                            pass
                        else:
                            map = map.split(":")[1]
                    else:
                        socket.send(f"pos : pos 1 : {make_pos((pos[0], HEIGHT - 96 - TERRAIN_SIZES[int(map)]))}".encode("utf-8"))
            else:
                    print("player 2 connected")
                    p2_pos = "pos : pos 2 : " + make_pos((pos[1], HEIGHT - 96 - TERRAIN_SIZES[int(map)]))
                    p1_pos = "pos : pos 1 : " + make_pos((pos[0], HEIGHT - 96 - TERRAIN_SIZES[int(map)]))
                    print("will broadcast")
                    socket.send(p2_pos.encode("utf-8"))
                    players[0].send(p2_pos.encode("utf-8"))
                    print("sent pos of 2 to 2 and to 1 also")
                    socket.send(p1_pos.encode("utf-8"))
                    if socket.recv(1024).decode("utf-8").strip() == "received":
                      ingame = True
                      broadcast("start : starting Game".encode("utf-8"))
        else:

            try:
                data = socket.recv(2048).decode("utf-8")
                if data:
                    broadcast(data, socket)
                else:
                    print(f"Connection closed for {address}")
                    socket.close()
                    del players[player_id(socket)]
                    break
            except Exception as e:
                print(f"Error: {e}")
                break
'''
        
    #if mode == "create":
    #    socket.send("select a map".encode("utf-8"))
    #    map = socket.recv(1024).decode("utf-8")
    #    games.append(Info(address, None, int(map)))
    #    socket.send(make_pos((100, HEIGHT - 96 - TERRAIN_SIZES[int(map)])).encode("utf-8"))
    #elif mode == "join":

    

