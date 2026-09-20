import socket
import time
import json
import threading
from copy import deepcopy

class server:
    def __init__(self):
        #ip.port needed for binding to socket
        #"" means all interfaces
        # the server will now accept connections from 
        # 192.168.1.64 or from 127.0.0.1
        #self.ip = ""
        try :
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            #connects to random dns (google), just to get lan ip
            s.connect(("8.8.8.8", 80))
            self.ip = s.getsockname()[0]
            s.close()
        except exception as e:
            print(f"error with trying to get the lan ip: {e}")
            self.ip="127.0.0.1"

        self.port = 0 #OS will assign a free port
        self.addr = (self.ip, self.port)

        #specified the protocol used, I will use TCP for reliability
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        #this allows socket to be reused within a short time frame
        #closing and opening the game should allow the player to play 
        #lan game again
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

        #current connections used for passing in the player number
        self.current_connections = 0
        #not allow more than 2 players to join
        self.max_connections = 2

        self.stage = None
        #player 1 and 2 necessary data 
        #player1/host should always jon first
        self.data = {"1": {"name": None, 
                           "position": (0,0),
                           "animation_state": "idle",
                           "frame": 0,
                           "facing_left": False,
                           "health": 100,
                           "selected": None,
                           "confirmed": None},

                     "2": {"name": None,
                           "position": (0,0),
                           "animation_state": "idle",
                           "frame": 0,
                           "facing_left": False,
                           "health": 100,
                           "selected": None,
                           "confirmed": None},
                     }

        self.wins = [0,0]
        self.start_time = 0
        self.time = 90

        self.running = True
        self.listening = True

    def shutdown(self):
        #exits the threads
        self.running = False 
        self.listening = False
        try:
            self.socket.close()
        except:
            pass

    def checkRound(self):
        round_reset = False
        # resets both players if one player is defeated
        # if player 1 is defeated
        if self.data["1"]["health"] <= 0:
            # player 2 wins incremented
            self.wins[1] += 1
            round_reset = True
        # if player 2 is defeated
        elif self.data["2"]["health"] <= 0:
            # player 1 wins are incremented
            self.wins[0] += 1
            round_reset = True
        # Check for time out 
        elif time.time() - self.start_time >= self.time:
            round_reset = True
            # player with the lowest health loses
            if self.data["1"]["health"] > self.data["2"]["health"]:
                self.wins[0] += 1
            elif self.data["2"]["health"] > self.data["1"]["health"]:
                self.wins[1] += 1
            # if healths are equal then no wins to either
            # round is restarted

        # best of 3 system
        # if one player wins twice, they win
        if 4 in self.wins:
            # ending banner should be switched to here
            return f"victory_{self.wins.index(4) + 1}"
            # if a player wins, then the scene is switched back to the joining menu
        #
        if round_reset:
            self.start_time = time.time()
            return "new_round"
        else:
            return "active"
        


    def start(self, stage):
        #this function is called for setting up the server
        #stage will be used in the joining menu
        #way to differentiate between diferent hosts
        self.stage = stage

        #bind here to be able to return a status when starting
        try:
            self.socket.bind(self.addr)
            #get sock name will get the ip and port picked
            #in socket address format
            self.addr = self.socket.getsockname()

            self.ip = self.addr[0]
            self.port = self.addr[1]
        except Exception as e:
            return ["Error"]

        #server will need to run on a seperate thread 
        #daemon means that this thread will end once main game is closed
        server = threading.Thread(target=self.accept_connections, args=(), daemon=True)
        server.start()

        listen = threading.Thread(target=self.listen, args=(), daemon=True)
        listen.start()

        return ["Success"]

    #this function will accept new connections from players
    def accept_connections(self):

        self.socket.listen(self.max_connections)
        print("Waiting for a connection, Server started")

        #will only accept a connection if the current_connections is under max_connections
        while True and self.current_connections < self.max_connections and self.running:
            conn, addr = self.socket.accept()
            #print console for confirmation of connection
            print(f"connected to{conn}:{addr}")

            self.current_connections += 1
            #current connection used to specifiy the player number
            client = threading.Thread(target=self.threaded_client, args=(conn, self.current_connections), daemon=True)
            client.start()

        #two players have joined, so no more game discovery requests
        self.listening = False

    def threaded_client(self,conn, n):
        try:
            
            while True:

                op = 1 if n == 2 else 2
                data = json.loads(conn.recv(1024).decode())
                response = None

                #the response will be the same for player 1/2 in the actual rounds
                if data[0] == "game":
                    #exchanges the data with the dictionary
                    #player data stored in the dictionary
                    self.data[f"{n}"]["position"] = data[1]
                    self.data[f"{n}"]["animation_state"] = data[2]
                    self.data[f"{n}"]["frame"] = data[3]
                    self.data[f"{n}"]["facing_left"] = data[4]
                    self.data[f"{n}"]["health"] = data[5]

                    #makes a deepcopy to avoid race conditions
                    otherPlayerData = deepcopy(self.data[f"{op}"])
                    #sends the status of the game back to the players
                    otherPlayerData["status"] = self.checkRound()
                    otherPlayerData["wins"] = self.wins
                    response = otherPlayerData 

                elif data[0] == "initH":
                    #if player 2 has joined then the server is ready
                    if self.current_connections == 2:
                        response = ["ready"]
                    else:
                        response = ["waiting"]

                elif data[0] == "request_op_character_selections":
                    self.data[f"{n}"]["selected"] = data[1]
                    self.data[f"{n}"]["confirmed"] = data[2]

                    response = [self.data[f"{op}"]["selected"], self.data[f"{op}"]["confirmed"]]

                elif data[0] == "request_character_status":
                    temp = [self.data[f"{n}"]["confirmed"], self.data[f"{op}"]["confirmed"]]

                    #if one player still hasn't picked
                    if None in temp:
                        response = ["ongoing"]
                    #else they both have picked their characters
                    else:
                        response = ["start"]

                elif data[0] == "request_stage":
                    response = [self.stage]

                elif data[0] == "request_all_character_selections":
                    #first index is always for the player requesting
                    temp = [self.data[f"{n}"]["confirmed"], self.data[f"{op}"]["confirmed"]]
                    self.data[f"{n}"]["name"] = self.data[f"{n}"]["confirmed"]
                    response = temp

                elif data[0] == "request_lan_status":
                    #if two players are in the game, response will be [True]
                    response = [self.current_connections==2]
                
                conn.send(json.dumps(response).encode())

        except Exception as e:
            print(e)

        finally:
            conn.close()
            self.current_connections -= 1

    def listen(self):
        #IPv4, UDP
        udp_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

        #recfrom will stop after 3 seconds, if no response
        #otherwise will run forever, despite the loop
        udp_sock.settimeout(3.0)

        try:
            #'' binds to all interfaces
            #9999 is the same as the discover_games
            udp_sock.bind(('', 9999))
        except Exception as e:
            print(Exception)

        while self.listening:
            #try block keeps the function from ending
            try:
                data,addr = udp_sock.recvfrom(1024)
                message = data.decode()

                if message == "game_discovery_request_mythbound":
                    #send the stage back
                    response = (self.stage+"."+str(self.port)).encode()
                    #addr is the address the request came from
                    udp_sock.sendto(response, addr)

            except Exception:
                pass #time out errors, shouldn't do anything
        
        #finally closes the socket
        udp_sock.close()




class network:
    def __init__(self):
        #inits the socket as TCP, to match the server
        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        self.discovered = []
        self.discovering = False

    def update(self):
        #to be updated
        pass

    def connect(self, addr):
        try:
            if hasattr(self, "client"):
                self.reset()
            self.client.connect(addr)
        except Exception as e:
            print("Connection error:", e)
            return False

    def reset(self):
        try:
            self.client.close()
        except Exception: 
            pass
        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    def send(self,data):
        try:
            self.client.send(json.dumps(data).encode())
            return json.loads(self.client.recv(1024).decode())
        except Exception as e:
            #in a list as all server responses are in a list
            #less likely to produce an error as I usually check the first
            #index in server response handling
            self.reset()
            return ["Error"]


    def discover_games(self):
        self.dicovering = True
        #Ipv4 and UDP
        udp_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        #Allows broadcasting
        udp_sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)

        #3 second timeout 
        #otherwise it will try to receive forever
        udp_sock.settimeout(3.0)
        #'' means all interfaces
        #0 means any free port
        udp_sock.bind(('', 0))

        message = "game_discovery_request_mythbound"
        discovered = []

        try:
            udp_sock.sendto(message.encode(), ('<broadcast>', 9999))
        except:
            return []

        start = time.time()
        while time.time() - start < 3:
            try:
                #receives the stage and the address
                #from the server
                stage, addr = udp_sock.recvfrom(1024)

                #appends to a list, to return
                discovered.append((stage.decode(), addr))
            except:
                pass

        udp_sock.close()

        self.discovered = discovered
        self.discovering = False


                

