import socket
from threading import Lock,Thread
from queue import Queue
from BaseClass import ProtocolObject
#from MEGANAUGHTSANDCROSSESmultiplayer import createGrids
import time
#from access_database import store, load

host = ""
port = 37575
storage_name = "data.json"
currentHosts = []
currentHostsByID = []
requestedGames = []
queue = Queue()
lockCurrentHosts = Lock()
lockStoreFile = Lock()
lockRequestedGames = Lock()
currentID = 0
maxID = 2147483647

class GameLink():
    def __init__(self):
        self.turn = 1
        #self.grid = createGrids()
        self.move = [0,0]
        self.marker = [0,0]
        self.finish = [0,0]
        

class ThreadedClient(ProtocolObject):
    def __init__(self, conn, ID, addr):
        super().__init__(conn,False)
        self.ip = addr[0]
        self.buffer = ""
        self.username = None
        self.hosting = False
        self.id = ID
        self.link = None

        initial = self.get_command()
        if initial != "1":
            print("Unexpected initialisation value received. "
                  "Closing connection.")
            self.conn.close()
            return

        self.send_command("9")
        while True:
            command = self.get_command()
            if not command:
                break
            if command and self.hosting:
                time.sleep(.5)
                position = currentHostsByID.index(self.id)
                if not requestedGames[position] == "":
                    self.link = requestedGames[position]
                    self.host("",False)
                    self.send_command("1")
                    self.game(1)
                if command == True:
                    command = ""
            
            # Split command into control byte and the rest of the information
            if len(command) > 1:
                control, command = command[0], command[1:]
            else:
                control = command

            # Do stuff with command
            if control == "2":
                self.logIn(command)
            elif control == "3":
                self.host(command,True)
            elif control == "4":
                self.host("",False)
            elif control == "5":
                self.requestHosts()
            elif control == "6":
                self.connect(command)
            elif control == "7":
                self.updateRecord(command)
            elif control == "8":
                self.refuseConnection(command)
        
        if self.hosting:
            queue.put([False,self.id])

    def game(self,myTurn):
        while True:
            if self.link.turn == myTurn:
                #print(str(myTurn)+": waiting")
                command = self.get_command()
                #print(str(myTurn)+": "+command)
                if not command:
                    self.link.finish = [myTurn,2]
                    break
                if command[0] == "!":
                    self.link.move = [command[1],command[2]]
                    if self.link.turn == 1:
                        self.link.turn = 2
                    else:
                        self.link.turn = 1
                else:
                    self.link.marker = [command[1],command[2]]
            else:
                #print(str(myTurn)+": doing")
                lastMove = self.link.move
                lastMarker = self.link.marker
                while lastMove == self.link.move:
                    if not lastMarker == self.link.marker:
                        lastMarker = self.link.marker
                        self.send_command("?"+str(lastMarker[0])+str(lastMarker[1]))
                    if self.link.finish[1] == 2:
                        self.send_command("."+str(self.link.finish[0])+str(self.link.finish[1]))
                        break
                    time.sleep(0.1)
                if self.link.finish[1] == 2:
                    break
                self.send_command("!"+str(self.link.move[0])+str(self.link.move[1]))
                

    def logIn(self,command):
        print("Unimplemented")

    def host(self,command,creating):
        if creating:
            #host properties
            #0 = IP; 1 = Name; 2 = Description;
            value = ""
            properties = []
            for letter in command:
                if letter == "|":
                    properties.append(value)
                    value = ""
                else:
                    value = value + letter
            queue.put([True,self.id]+properties)
            self.hosting = True
            self.setTimeout(0)
            while not self.id in currentHostsByID:
                time.sleep(0.5)
        else:
            if self.hosting:
                queue.put([False,self.id])
                self.hosting = False
                self.setTimeout(None)
        self.send_command("3")

    def requestHosts(self):
        lockCurrentHosts.acquire()
        toReturn = ""
        for i in range(0,len(currentHosts)):
            for Property in currentHosts[i]:
                toReturn = toReturn + str(Property) + "|"
            toReturn = toReturn[:-1] + "`"
        print(toReturn)
        self.send_command(toReturn)
        lockCurrentHosts.release()

    def connect(self,command):
        lockCurrentHosts.acquire()
        lockRequestedGames.acquire()
        position = currentHostsByID.index(int(command))
        self.link = GameLink()
        if requestedGames[position] == "":
            requestedGames[position] = self.link
            lockCurrentHosts.release()
            lockRequestedGames.release()
            self.game(2)
        else:
            lockCurrentHosts.release()
            lockRequestedGames.release()

    def updateRecord(self,command):
        print("Unimplemented")


def manageCurrentHosts(queue):
    while True:
        command = queue.get()
        print(command)
        lockCurrentHosts.acquire()
        if command[0]:
            if command[1] in currentHostsByID:
                position = currentHostsByID.index(command[1])
                for i in range(2,len(command)):
                    if command[i] != "":
                        currentHosts[position][i-1] = command[i]
            else:
                lockRequestedGames.acquire()
                currentHosts.append(command[1:])
                currentHostsByID.append(command[1])
                requestedGames.append("")
                lockRequestedGames.release()
        else:
            lockRequestedGames.acquire()
            position = currentHostsByID.index(command[1])
            del currentHosts[position]
            del currentHostsByID[position]
            del requestedGames[position]
            lockRequestedGames.release()
        lockCurrentHosts.release()

def create_threaded_client(conn, address, currentID):
    _ = ThreadedClient(conn,currentID,address)
    print("Lost connection with: " + address[0] + ":" + str(address[1]) + " (ID: "+str(currentID)+")")

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.bind((host, port))
s.listen(5)

currentHostsThread = Thread(target=manageCurrentHosts, args=(queue,))
currentHostsThread.daemon = True
currentHostsThread.start()

print("Waiting for connection...")
threads = []
while True:
    connection, addr = s.accept()
    print("Connected to: " + addr[0] + ":" + str(addr[1]) + " (ID: "+str(currentID)+")")
    t = Thread(target=create_threaded_client, args=(connection, addr, currentID))
    t.daemon = True
    t.start()
    if currentID == maxID:
        currentID = 0
    else:
        currentID += 1
