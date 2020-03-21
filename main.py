from PodSixNet.Channel import Channel
from PodSixNet.Server import Server
from PodSixNet.Connection import ConnectionListener, connection
import sys, os
import pygame
from random import randint

class Player():
    def __init__(self, size, color, pos, pid):
        self.size = size
        self.color = color
        self.pos = pos
        self.speed = 0.2
        self.pid = pid

    def getKeys(self):
        """
        getkeys (): returns a list of all the keys currently being pressed
        """
        current_keys = {'a': 97, 'b': 98, 'c': 99, 'd': 100, 'e': 101, 'f': 102, 'g': 103, 'h': 104, 'i': 105, 'j': 106, 'k': 107, 'l': 108, 'm': 109,
        'n': 110, 'o': 111, 'p': 112, 'q': 113, 'r': 114, 's': 115, 't': 116, 'u': 117, 'v': 118, 'w': 119, 'x': 120, 'y': 121, 'z': 122, '[': 91, ']': 93, '\\': 92, '.': 46, '/': 47, ';': 59, "'": 39, 'backspace': 8, 'delete': 127, 'home': 278, 'end': 279, 'return': 13, 'insert': 277, 'page up': 280, 'right shift': 303, 'up': 273, 'page down': 281, 'right': 275, 'down': 274, 'left': 276,
        'right ctrl': 305, 'menu': 319, 'right alt': 307, 'space': 32, 'left alt': 308, 'left ctrl': 306, 'left shift': 304, 'caps lock': 301, 'tab': 301, '`': 301, '1': 301, '2': 301, '3': 301, '4':
        301, '5': 301, '6': 301, '7': 301, '8': 301, '9': 301, '0': 301, '-': 301, '=': 301, 'escape': 301, 'f1': 301, 'f2': 301, 'f3':
        301, 'f4': 301, 'f5': 301, 'f6': 287, 'f7': 301, 'f8': 301, 'f9': 301, 'f10': 301, 'f11': 301, 'f12': 301, '0': 48, '1': 49, '2': 50, '3': 51, '4': 52, '5': 53, '6': 54, '7': 55, '8': 56, '9': 57}
        
        if pygame.key.get_focused() == True:
            bools = pygame.key.get_pressed()
            out = []
            for i in range(0,len(bools)):
                if bools[i] == 1:
                    try:
                        out.append(list(current_keys.keys())[list(current_keys.values()).index(i)])
                    except(ValueError):
                        pass
            return out
        return []

    def move(self, dt):
        keys = self.getKeys()
        x,y = self.pos
        d = self.speed*dt
        if "d" in keys:
            x += d
        if "a" in keys:
            x -= d
        if "s" in keys:
            y += d
        if "w" in keys:
            y -= d
        
        self.pos = (x,y)

    def draw(self):
        s = pygame.Surface(self.size)
        s.fill(self.color)
        return s
    
    def dataOut(self):
        out = {
            "size": self.size,
            "color": self.color,
            "pos": self.pos,
            "pid": self.pid,
            }
        
        return out

#Client to Server Messages
class ClientChannel(Channel):

    def Network(self, data): #all messages
        print(data)

    def Network_input(self, data): #messages with "action" as input
        global players
        
        for p in players:
            if p.pid == data["pid"]:
                p.pos = data["pos"]

    def Network_close(self, data): #messages with "action" as input
        global players, clients
        
        for p in players:
            if p.pid == data["pid"]:
                players.remove(p)

                for c in clients:
                    if c[1] == p.pid:
                        c[0].Send({"action": "close"})
                        clients.remove(c)

class MyServer(Server): #server class

    channelClass = ClientChannel #use above channel

    def Connected(self, channel, addr): #when connected add player to list of players
        global players
        global clients
        global player


        pid = len(players)
        color = (randint(0,255), randint(0,255), randint(0,255))
        size = (50,50)
        pos = (0,0)

        clients.append([channel, pid])

        p = Player(size, color, pos, pid)
        players.append(p)
        
        data = p.dataOut()
        data["action"] = "init"

        channel.Send(data)

        data = player.dataOut()
        data["action"] = "addPlayer"

        channel.Send(data)


class MyNetworkListener(ConnectionListener): #Client listener

    def __init__(self, host, port):
        self.Connect((host, port))

    def Network(self, data):
        pass

    def Network_connected(self, data):
        pass

    def Network_error(self, data):
        print("error", data)
    def Network_disconnected(self, data):
        pass

    def Network_init(self, data):
        print("recieved")
        global player, players

        player = Player(data["size"], data["color"], data["pos"], data["pid"])
        players.append(player)

        print(players)

    def Network_addPlayer(self, data):
        print("recievedPlayer")
        global players

        p = Player(data["size"], data["color"], data["pos"], data["pid"])
        players.append(p)

        print(players)

    def Network_update(self, data):
            print("recievedUpdate")
            global players, player

            data = data["playerData"]

            for p in players:
                pid = p.pid

                if pid != player.pid:

                    p.pos = data[pid]
    
    def Network_close(self, data):
        print("recievedClose")
        sys.exit()



pygame.init()

size = (1200,720)

screen = pygame.display.set_mode(size)
display = pygame.Surface(size)
display.fill((22,22,22))
screen.blit(display,(0,0))
pygame.display.flip()


pygame.display.set_caption('Network')
clock = pygame.time.Clock()

args = list(sys.argv)[1::]
args.append("client")
server = False
if args[0] == "host":
    server = True


if server:

    player = Player((50,50), (80,80,200), (0,0), 0)
    players = [player]

    clients = []

    myserver = MyServer(localaddr=('192.168.2.11', 3737)) #start server on (address,port)
    while True:
        dt = clock.tick()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                sys.exit()
        
        for p in players:
            display.blit(p.draw(), p.pos)
        
        player.move(dt)

        screen.blit(display, (0,0))
        pygame.display.flip()
        display.fill((22,22,22))
        screen.fill((22,22,22))

        


        for k in clients: #for client send data and print users
            data = {}
            for p in players:
                data[p.pid] = p.pos
            k[0].Send({"action": "update", "playerData": data, "dt": dt})

        myserver.Pump() #update messages


else:
    player = None
    players = []

    serverDt = 0
    stream = MyNetworkListener("llibyddap.ddns.net", 3737) #load client listener
    while True:
        dt = clock.tick()

        if serverDt > dt:
            pygame.time.delay(serverDt-dt)
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                print("QUIT")
                stream.Send({"action": "close", "pid": player.pid})
                stream.Send({"action": "close", "pid": player.pid})
                #sys.exit()

        for p in players:
            display.blit(p.draw(), p.pos)
        
        if player:
            player.move(dt)
            stream.Send({"action": "input", "pid": player.pid, "pos": player.pos})

        screen.blit(display, (0,0))
        pygame.display.flip()
        display.fill((22,22,22))
        screen.fill((22,22,22))

        connection.Pump() #update client messages
        stream.Pump()



