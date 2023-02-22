text = False
try:
    import UI
except:
    text = True
import math
import socket
import time
import threading
import queue
import sys
from BaseClass import ProtocolObject

# 1-9 mapped to squares in grid
validNumbers = list("123456789")

# if one player owns any of these numbers, they have 3 in a row
victory = []
for i in range(0, 3):
    victory.append([i * 3, i * 3 + 1, i * 3 + 2])
for i in range(0, 3):
    victory.append([i, i + 3, i + 6])
victory.append([0, 4, 8])
victory.append([2, 4, 6])

# IP and port of MEGANAUGHTSANDCROSSESserver.py instance
port = 37575
# server = "meganaughtscrosses.ddns.net"
server = "127.0.0.1"

colours = {"text": (255, 255, 255), "button": (100, 150, 200, 180), "textbox": (50, 50, 50, 180)}

if not text:
    UI.pygame.init()
    UI.pygame.key.set_repeat(350, 50)
    infoObject = UI.pygame.display.Info()
    # sets window X and Y to 30% and 50% of current resolution
    windowX, UI.oldWindowX = math.ceil(infoObject.current_h * 0.3), math.ceil(infoObject.current_h * 0.3)
    windowY, UI.oldWindowY = math.ceil(infoObject.current_h * 0.5), math.ceil(infoObject.current_h * 0.5)
    screen = UI.pygame.display.set_mode((windowX, windowY), UI.pygame.RESIZABLE, 32)


def getIP():
    # try a bunch of different ways of getting a non-localhost IP
    try:
        ip = str(socket.gethostbyname_ex(socket.gethostname())[-1][0])
    except:
        ip = "127.0.0.1"
    if ip in ["127.0.0.1", "127.0.1.1"]:
        try:
            ip = str(socket.gethostbyname_ex(socket.getfqdn())[-1][0])
        except:
            ip = "127.0.0.1"
        if ip in ["127.0.0.1", "127.0.1.1"]:
            try:
                s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                s.connect(("8.8.8.8", 80))
                ip = s.getsockname()[0]
                s.close()
            except:
                ip = "127.0.0.1"
    return ip


def listenThread(queue, s):
    try:
        conn, addr = s.accept()
    except:
        return
    queue.put(conn)


def stopThread(queue, kill):
    input()
    if kill():
        return
    queue.put(True)


def createWindow(markers=None):
    if markers is None:
        markers = []
    for event in UI.pygame.event.get():
        if event.type == UI.pygame.QUIT:
            UI.pygame.quit()
    global turnMarker
    turnMarker = UI.Marker(turnMarker.Type, (240, 240, 240), windowX, windowY)
    screen.fill(colours["text"])
    screen.blit(turnMarker.image, (0, 0))
    for item in markers:
        screen.blit(item.image, (item.absX, item.absY))


def printGridText(grid):
    toPrint = ""
    for k in range(0, 3):
        for i in range(0, 3):
            for j in range(0, 3):
                for item in grid[j + k * 3][i]:
                    toPrint = toPrint + item
                toPrint = toPrint + "|"
            toPrint = toPrint[:-1] + "\n"
        toPrint = toPrint + "-" * 11 + "\n"
    print(toPrint[:-12])


def createGrids():
    toReturn = []
    for i in range(0, 9):
        toAdd = []
        for j in range(0, 3):
            toAdd.append([" "] * 3)
        toReturn.append(toAdd)
    return toReturn


def tabulateServerData(data, isLobbies=True):
    toReturn = [[]]
    item = 0
    currentData = ""
    for i in range(0, len(data)):
        if data[i] == "|" or data[i] == "`":
            toReturn[item].append(currentData)
            currentData = ""
            if data[i] == "`" and i < len(data) - 1:
                item += 1
                toReturn.append([])
        else:
            currentData = currentData + data[i]
    if not isLobbies:
        toReturn = toReturn[0]
    return toReturn


class Launcher():
    def __init__(self, text=False):
        if text:
            while True:
                print("1: Local PvP")
                print("2: LAN")
                print("3: Online multiplayer")
                print("4: Quit")
                Input = input()
                while Input not in ["1", "2", "3", "4"]:
                    print("Invalid input \n")
                    Input = input()
                print()
                if Input == "1":
                    game = Game(True)
                elif Input == "2":
                    print("1: Host")
                    print("2: Join")
                    print("3: Main Menu")
                    Input = input()
                    while Input not in ["1", "2", "3"]:
                        Input = input()
                    if Input == "1":
                        print()
                        ip = getIP()
                        if ip == "127.0.0.1":
                            print("Unable to resolve your IP")
                        else:
                            print("Your IP is " + str(ip))
                        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                        s.bind(("", port))
                        s.listen(1)
                        print("Ready to recieve connection")
                        print("Press CTRL+C to escape")
                        inputQueue = queue.Queue()
                        socketThread = threading.Thread(target=listenThread, args=(inputQueue, s))
                        socketThread.daemon = True
                        socketThread.start()
                        try:
                            while inputQueue.empty():
                                time.sleep(0)
                        except KeyboardInterrupt:
                            pass
                        if not inputQueue.empty():
                            game = Game(True, inputQueue.get(), True)
                        s.close()
                        print('\n')
                    elif Input == "2":
                        print("\nWhat IP?")
                        Input = input()
                        try:
                            s = socket.socket()
                            s.connect((Input, port))
                            game = Game(True, s, False)
                        except Exception as e:
                            print(
                                "\nCould not connect to IP. Check you typed it correctly and that it is hosting a game")
                            print(e)
                            print()
                        s.close()
                elif Input == "3":
                    try:
                        s = socket.socket()
                        s.connect((server, port))
                    except Exception as e:
                        print("Unable to connect to server")
                        print(e)
                        print()
                        s.close()
                        continue
                    protocolObject = ProtocolObject(s, False)
                    protocolObject.send_command("1")
                    response = protocolObject.get_command()
                    if not response or not response == "9":
                        print("Unexpected response from server")
                        s.close()
                        continue
                    print("1: Host")
                    print("2: Join")
                    print("3: Main Menu")
                    Input = input()
                    while not Input in ["1", "2", "3"]:
                        Input = input()
                    if Input == "1":
                        print("Name of Lobby (30 Char Limit)")
                        Input = input()
                        name = ""
                        while len(Input) < 1 or len(Input) > 30 or "|" in Input:
                            if "|" in Input:
                                print("Please remove the invalid character |")
                            if len(Input) > 30:
                                print("\nOver char limit. Accept " + Input[:30] + "?")
                                print("1: Yes")
                                print("2: No")
                                name = Input[:30]
                                Input = input()
                                while not Input in ["1", "2"]:
                                    print("\nInvalid Input")
                                    Input = input()
                                if Input == "1":
                                    break
                                else:
                                    name = ""
                            else:
                                print("Name must be at least one character long")
                            Input = input()
                        if name == "":
                            name = Input

                        description = ""
                        print("Description of Lobby (80 Char Limit)")
                        Input = input()
                        while len(Input) < 1 or len(Input) > 80 or "|" in Input:
                            if "|" in Input:
                                print("Please remove the invalid character |")
                            elif len(Input) > 80:
                                print("\nOver char limit. Accept " + Input[:80] + "?")
                                print("1: Yes")
                                print("2: No")
                                description = Input[:80]
                                Input = input()
                                while not Input in ["1", "2"]:
                                    print("\nInvalid Input")
                                    Input = input()
                                if Input == "1":
                                    break
                                else:
                                    description = ""
                            else:
                                print("Description must be at least one character long")
                            Input = input()
                        if description == "":
                            description = Input
                        protocolObject.send_command("3" + name + "|" + description + "|")
                        received = protocolObject.get_command()
                        if not received == "3":
                            print("Error hosting game. Please try again\n")
                            continue
                        try:
                            loop = True
                            while loop:
                                received = protocolObject.get_command()
                                if not received:
                                    raise Exception
                                if received == "1":
                                    print("Attempting Connection")
                                    game = Game(True, s, True)
                                    loop = False
                        except KeyboardInterrupt:
                            print()
                        except Exception as e:
                            print("Lost connection to server")
                            print(e)
                    elif Input == "2":
                        protocolObject.send_command("5")
                        lobbies = tabulateServerData(protocolObject.get_command())
                        print()
                        for i in range(0, len(lobbies)):
                            print("ID: " + str(i + 1))
                            print("Lobby Name: " + lobbies[i][1])
                            print("Lobby Description: " + lobbies[i][2])
                            print()
                        print("Which lobby do you want to join? 0 to cancel.")
                        Input = input()
                        loop = True
                        while loop:
                            try:
                                Input = int(Input)
                                loop = False
                            except ValueError:
                                print("Invalid Input")
                                Input = input()
                        if Input in range(1, len(lobbies) + 1):
                            print("Attempting connection")
                            protocolObject.send_command("6" + lobbies[Input - 1][0])
                            game = Game(True, s, False)
                            s.close()
                else:
                    break
        else:
            self.defaultX = windowX
            self.defaultY = windowY
            self.buttons = []
            text = ["Local PvP", "LAN", "Online"]
            for i in range(0, len(text)):
                self.buttons.append(
                    UI.Button(text[i], colours["text"], colours["button"], windowX * 0.9, windowY * 0.28,
                              windowX * 0.05, windowY * (0.05 + i * (.9 / len(text)))))
            UI.normalizeTextSize(self.buttons)
            self.clock = UI.pygame.time.Clock()
            ticks = 301
            while True:
                i = self.eventCheck(self.buttons, infoObject.current_h * 0.3, infoObject.current_h * 0.5)
                if not i == []:
                    for item in i:
                        if item == 0:
                            # Local
                            launcherX = windowX
                            launcherY = windowY
                            game = Game()
                            self.applyResize(launcherX, launcherY)
                        elif item == 1:
                            # LAN
                            launcherX = windowX
                            launcherY = windowY
                            self.hostPrompt(True)
                            self.applyResize(launcherX, launcherY)
                        elif item == 2:
                            # Online
                            # UI isn't implemented, backend works fine - can play via text mode
                            self.buttons[2].text.changeText("Not Implemented")
                            self.buttons[2].rescale(1, 1)
                            self.buttons[2].draw()
                            ticks = 0
                            # try:
                            #     s = socket.socket()
                            #     s.settimeout(4)
                            #     s.connect((server, port))
                            #     worked = True
                            # except Exception as e:
                            #     print("Unable to connect to server")
                            #     print(e)
                            #     print()
                            #     s.close()
                            #     worked = False
                            # if worked:
                            #     self.protocolObject = ProtocolObject(s, False)
                            #     self.protocolObject.send_command("1")
                            #     response = self.protocolObject.get_command()
                            #     if not response or not response == "9":
                            #        print("Unexpected response from server")
                            #        s.close()
                            #        worked = False
                            # if worked:
                            #     launcherX = windowX
                            #     launcherY = windowY
                            #     self.hostPrompt(False)
                            #     self.applyResize(launcherX, launcherY)
                w, h = UI.pygame.mouse.get_pos()
                self.render(self.buttons, w, h)
                self.clock.tick(60)
                if ticks < 300:
                    ticks += 1
                elif ticks == 300:
                    self.buttons[2].text.changeText("Online")
                    self.buttons[2].rescale(1, 1)
                    UI.normalizeTextSize(self.buttons)
                    ticks = 301

    def eventCheck(self, buttons, defaultX, defaultY, otherButtons=[], textBox=None):
        toReturn = []
        combinedButtons = buttons + otherButtons
        for event in UI.pygame.event.get():
            if event.type == UI.pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    deselect = True
                    for i in range(0, len(combinedButtons)):
                        if combinedButtons[i].colour != combinedButtons[i].renderColour:
                            toReturn.append(i)
                            deselect = False
                    if deselect and textBox:
                        toReturn.append(-1)
            elif event.type == UI.pygame.VIDEORESIZE:
                self.applyResize(event.w, event.h, buttons, otherButtons)
            elif event.type == UI.pygame.KEYDOWN:
                if event.key == UI.pygame.K_r:
                    resize = True
                    if textBox:
                        for item in textBox:
                            if item.selected:
                                resize = False
                    if resize:
                        self.applyResize(defaultX, defaultY, buttons, otherButtons)
                if textBox:
                    if event.key == UI.pygame.K_BACKSPACE:
                        for item in textBox:
                            if item.selected:
                                item.typing("back")
                    elif event.key == UI.pygame.K_RETURN:
                        toReturn.append("textEnter")
                    else:
                        for item in textBox:
                            if item.selected:
                                if UI.pygame.key.get_mods() & UI.pygame.KMOD_SHIFT:
                                    item.typing(chr(event.key).upper())
                                else:
                                    item.typing(chr(event.key))
            elif event.type == UI.pygame.QUIT:
                UI.pygame.quit()
                sys.exit()()
        return toReturn

    def render(self, buttons, w, h, items=[]):
        screen.fill((200, 200, 255))
        for item in buttons:
            item.checkHighlight(w, h)
            screen.blit(item.image, (item.absX, item.absY))
        for item in items:
            screen.blit(item.image, (item.absX, item.absY))
        UI.pygame.display.flip()

    def hostPrompt(self, isLAN):
        self.applyResize(infoObject.current_h * 0.5, infoObject.current_h * 0.3)
        tempButtons = []
        text = ["Host", "Connect", "Competitive"]
        if isLAN:
            w = windowX * 0.45
            x = 0.5
            r = 2
        else:
            self.protocolObject.setTimeout(None)
            w = windowX * 0.3
            x = 0.33
            r = 3
        for i in range(0, r):
            tempButtons.append(
                UI.Button(text[i], colours["text"], colours["button"], w, windowY * 0.85, windowX * (0.025 + i * x),
                          windowY * 0.1))
        backButton = [
            UI.Button("back", colours["text"], colours["button"], windowX * 0.08, windowY * 0.08, windowX * 0.025,
                      windowY * 0.01)]
        while True:
            i = self.eventCheck(tempButtons, infoObject.current_h * 0.5, infoObject.current_h * 0.3, backButton)
            if not i == []:
                launcherX = windowX
                launcherY = windowY
                for item in i:
                    if item == 0:
                        if isLAN:
                            self.lanHost(backButton)
                        else:
                            self.wwwHost(backButton)
                    elif item == 1:
                        launcherX = windowX
                        launcherY = windowY
                        if isLAN:
                            self.lanConnect(backButton)
                        else:
                            self.wwwConnect(backButton)
                    elif item == 2 and not isLAN:
                        self.competitive(backButton)
                    else:
                        return
                xscale, yscale = 1, 1
                if not launcherX == windowX:
                    xscale = windowX / launcherX
                if not launcherY == windowY:
                    yscale = windowY / launcherY
                if not (xscale, yscale) == (1, 1):
                    for item in tempButtons:
                        item.rescale(xscale, yscale)
                    UI.normalizeTextSize(tempButtons)
            w, h = UI.pygame.mouse.get_pos()
            self.render(tempButtons + backButton, w, h)
            self.clock.tick(60)

    def wwwConnect(self, backButton):
        buttons = []
        scrollwrapper = UI.ScrollWrapper((50, 50, 50), (100, 100, 100), windowY * 0.9, windowX * 0.9, windowX * 0.05,
                                         windowY * 0.05)
        while True:
            self.render(buttons + backButton, 0, 0, [scrollwrapper])
            self.clock.tick(60)

    def wwwHost(self, backButton):
        buttons = []
        items = []
        sizeTest = (0, 0)
        items.append(UI.Text("Lobby name:", colours["text"]))
        items[0].pos(windowX * 0.05, windowY * 0.1)
        buttons.append(UI.TextBox(colours["text"], colours["textbox"], windowX * 0.9, windowY * 0.1, windowX * 0.05,
                                  windowY * 0.225, charLimit=30))
        items.append(UI.Text("Lobby description:", colours["text"]))
        items[1].pos(windowX * 0.05, windowY * 0.325)
        buttons.append(
            UI.MultiLineTextBox(colours["text"], colours["textbox"], windowX * 0.9, windowY * 0.3, windowX * 0.05,
                                windowY * 0.45, charLimit=80))
        buttons.append(
            UI.Button("Create", colours["text"], colours["button"], windowX * 0.4, windowY * 0.2, windowX * 0.3,
                      windowY * 0.775))
        tick = 0
        while True:
            if not sizeTest == (windowX, windowY):
                sizeTest = (windowX, windowY)
                items[0].scale(windowX * 0.9, windowY * 0.1)
                items[1].scale(windowX * 0.9, windowY * 0.1)
                items[0].pos(windowX * 0.05, windowY * 0.1)
                items[1].pos(windowX * 0.05, windowY * 0.325)
            i = self.eventCheck(backButton, infoObject.current_h * 0.5, infoObject.current_h * 0.3, buttons,
                                buttons[:2])
            if not i == []:
                for item in i:
                    if item == 1:
                        buttons[0].click()
                        if buttons[1].selected:
                            buttons[1].click()
                    elif item == 2:
                        buttons[1].click()
                        if buttons[0].selected:
                            buttons[0].click()
                    elif item == "textEnter":
                        if buttons[0].selected:
                            buttons[0].click()
                            buttons[1].click()
                        else:
                            buttons[1].click()
                            i.append(3)
                    elif item == 3:
                        if buttons[0].text.text == "":
                            items[0].text = "Empty Name!"
                            sizeTest = (0, 0)
                            tick = 1
                        elif buttons[1].text.text == "":
                            items[1].text = "Empty Description!"
                            sizeTest = (0, 0)
                            tick = 1
                        else:
                            self.protocolObject.send_command(
                                "3" + buttons[0].text.text + "|" + buttons[1].text.text + "|")
                            buttons[2].text.text = "Update"
                            buttons[2].rescale(1, 1)
                    elif item == 0:
                        self.protocolObject.send_command("4")
                        return
                    elif item == -1:
                        for i in range(0, 2):
                            if buttons[i].selected:
                                buttons[i].click()
            w, h = UI.pygame.mouse.get_pos()
            self.render(buttons + backButton, w, h, items)
            self.clock.tick(60)
            if tick > 0:
                tick += 1
            if tick > 180:
                items[0].text = "Lobby name:"
                items[1].text = "Lobby description:"
                sizeTest = (0, 0)

    def lanHost(self, backButton):
        try:
            ip = "Your IP is " + getIP()
        except:
            ip = "Unable to resolve your IP"
        texts = []
        texts.append(UI.Text(ip, colours["text"]))
        texts.append(UI.Text("Waiting for connection", colours["text"]))
        sizeTest = (0, 0)
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            s.bind(("", port))
            s.listen(0)
            inputQueue = queue.Queue()
            socketThread = threading.Thread(target=listenThread, args=(inputQueue, s))
            socketThread.daemon = True
            socketThread.start()
            while True:
                if not sizeTest == (windowX, windowY):
                    sizeTest = (windowX, windowY)
                    texts[0].scale(windowX * 0.9, windowY * 0.4)
                    texts[0].absX = (windowX - texts[0].font.size(texts[0].text)[0]) // 2
                    texts[0].absY = windowY * 0.1
                    texts[1].scale(windowX * 0.9, windowY * 0.4)
                    texts[1].absX = (windowX - texts[0].font.size(texts[0].text)[0]) // 2
                    texts[1].absY = windowY * 0.15 + texts[0].font.size(texts[0].text)[1]
                i = self.eventCheck(backButton, infoObject.current_h * 0.5, infoObject.current_h * 0.3)
                if not i == []:
                    break
                w, h = UI.pygame.mouse.get_pos()
                self.render(backButton, w, h, texts)
                if not inputQueue.empty():
                    oldX, oldY = windowX, windowY
                    game = Game(False, inputQueue.get(), True)
                    self.applyResize(oldX, oldY)
                    s.close()
                    return
                self.clock.tick(60)
        except:
            s.close()

    def lanConnect(self, backButton):
        connectButton = UI.Button("Connect", colours["text"], colours["button"], windowX * 0.5, windowY * 0.15,
                                  windowX * 0.25, windowY * 0.8)
        texts = [UI.Text("Input IP", colours["text"])]
        textBox = UI.TextBox(colours["text"], colours["textbox"], windowX * 0.9, windowY * 0.3, windowX * 0.05,
                             windowY * 0.45, "1234567890.localhost", 15)
        sizeTest = (0, 0)
        tick = 0
        textChanged = False
        textEnterDebounce = 0
        while True:
            if tick == 120:
                texts[0].text = "Input IP"
                textChanged = True
            elif tick > 0:
                tick += 1
            i = self.eventCheck(backButton, infoObject.current_h * 0.5, infoObject.current_h * 0.3,
                                [textBox, connectButton], [textBox])
            if not i == []:
                for item in i:
                    if item == 0:
                        return
                    elif item == 1:
                        textBox.click()
                    elif item == -1:
                        if textBox.selected:
                            textBox.click()
                    elif textEnterDebounce == 2 or not item == "textEnter":
                        if item == "textEnter":
                            textEnterDebounce = 0
                        try:
                            texts[0].text = "Attempting connection, do not close"
                            texts[0].scale(windowX * 0.9, windowY * 0.3)
                            texts[0].absX = (windowX - texts[0].font.size(texts[0].text)[0]) // 2
                            texts[0].absY = windowY * 0.1
                            w, h = UI.pygame.mouse.get_pos()
                            self.render(backButton + [textBox, connectButton], w, h, texts)
                            s = socket.socket()
                            s.connect((textBox.text.text, port))
                            succeeded = True
                        except Exception as e:
                            print(e)
                            texts[0].text = "Could not connect to IP!"
                            textChanged = True
                            succeeded = False
                            tick = 1
                        if succeeded:
                            oldX, oldY = windowX, windowY
                            game = Game(False, s, False)
                            self.applyResize(oldX, oldY)
                            s.close()
                            return

            if textEnterDebounce < 2:
                textEnterDebounce += 1

            if not sizeTest == (windowX, windowY) or textChanged:
                textChanged = False
                sizeTest = (windowX, windowY)
                texts[0].scale(windowX * 0.9, windowY * 0.3)
                texts[0].absX = (windowX - texts[0].font.size(texts[0].text)[0]) // 2
                texts[0].absY = windowY * 0.1
            w, h = UI.pygame.mouse.get_pos()
            self.render(backButton + [textBox, connectButton], w, h, texts)
            self.clock.tick(60)

    def applyResize(self, w, h, objects=[], otherObjects=[]):
        global windowX
        global windowY
        global screen
        windowX = math.ceil(w)
        windowY = math.ceil(h)
        if windowX < 100:
            windowX = 100
        if windowY < 300:
            windowY = 300
        screen = UI.pygame.display.set_mode((windowX, windowY), UI.pygame.RESIZABLE, 32)
        UI.rescale(objects + otherObjects, windowX, windowY)
        UI.normalizeTextSize(objects)


class Game(ProtocolObject):
    def __init__(self, text=False, conn=False, host=False):
        if conn != False:
            if text:
                super().__init__(conn, False)
            else:
                super().__init__(conn, True)
        self.text = text
        self.boxes = []
        self.grid = createGrids()
        self.turn = 1
        self.currentGrid = 9
        self.invalidGrids = [9]
        self.running = True
        self.xGridWins = []
        self.oGridWins = []
        self.click_debounce = True
        if text:
            self.textRun(conn != False, host)
        else:
            self.shadowMarker = UI.Marker("Cross", (255, 0, 0, 128), windowX * .08, windowY * .08)
            self.markers = [
                UI.Button("back", colours["text"], colours["button"], windowX * 0.09, windowY * 0.03, windowX * 0.005,
                          windowY * 0.005)]
            w, h = infoObject.current_w, infoObject.current_h
            w = min(w, h)
            h = w
            self.defaultSize = math.ceil(w * 0.9) - 50
            self.applyResize(self.defaultSize, self.defaultSize)
            self.displayGrid = UI.Grid()
            if self.run(conn != False, host):
                self.clock = UI.pygame.time.Clock()
                # displays victory grid
                while True:
                    UI.pygame.display.flip()
                    mouseX, mouseY = UI.pygame.mouse.get_pos()
                    self.markers[0].checkHighlight(mouseX, mouseY)
                    createWindow([self.displayGrid] + self.markers)
                    for event in UI.pygame.event.get():
                        if event.type == UI.pygame.MOUSEBUTTONDOWN:
                            if event.button == 1 and (self.markers[0].colour != self.markers[0].renderColour):
                                return
                        elif event.type == UI.pygame.VIDEORESIZE:
                            self.applyResize(event.w, event.h)
                            self.displayGrid.redraw()
                        elif event.type == UI.pygame.KEYDOWN:
                            if event.key == UI.pygame.K_r:
                                self.applyResize(self.defaultSize, self.defaultSize)
                                self.displayGrid.redraw()
                        elif event.type == UI.pygame.QUIT:
                            UI.pygame.quit()
                            sys.exit()()
                    self.clock.tick(60)

    def run(self, isMultiplayer, isHost):
        global turnMarker
        turnMarker = UI.Marker("Cross", (0, 0, 0), 10, 10)
        if isMultiplayer and not isHost:
            start = 2
        else:
            start = 1
        while self.running:
            if self.getTurn(self.turn == start, isMultiplayer):
                # if back button pressed, return and indicate to original caller
                return False
            self.actOnTurn()
            if self.invalidGrids == [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]:
                break
            if self.turn == 1:
                turnMarker.Type = "Cross"
                self.shadowMarker.Type = "Cross"
                self.shadowMarker.draw()
                turnMarker.draw()
            else:
                turnMarker.Type = "Nought"
                self.shadowMarker.Type = "Nought"
                self.shadowMarker.draw()
                turnMarker.draw()
        if self.invalidGrids == [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]:
            victoryText = UI.Text("Draw!", (0, 0, 0))
        elif self.turn == 1:
            victoryText = UI.Text("O Wins!", (0, 0, 0))
        else:
            victoryText = UI.Text("X Wins!", (0, 0, 0))
        victoryText.scale(windowX * 0.9, windowY * 0.05)
        w, h = victoryText.getDimensions()
        victoryText.pos((windowX - w) // 2, (windowY * 0.04 - h) // 2)
        self.markers.append(victoryText)
        return True

    def textRun(self, isMultiplayer, isHost):
        if not isHost and isMultiplayer:
            printGridText(self.grid)
            if self.waitForTurn() == False:
                return
            self.actOnTurn()
        while self.running:
            printGridText(self.grid)
            self.getTurnText(isMultiplayer)
            self.actOnTurn()
            if isMultiplayer and self.running:
                printGridText(self.grid)
                if self.waitForTurn() == False:
                    return
                self.actOnTurn()
            if self.invalidGrids == [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]:
                print("It's a tie!")
                return
        if self.turn == 1:
            print("O wins!")
        else:
            print("X wins!")

    def validSquares(self, grid):
        toReturn = []
        grid = self.grid[grid]
        for i in range(0, 3):
            for j in range(0, 3):
                if grid[i][j] == " ":
                    toReturn.append(i * 3 + j + self.text)
        return toReturn

    def victoryLine(self, i):
        if i < 3:
            offsetX = windowX * 0.1
            offsetY = windowY * (0.2 + math.floor(victory[i][0] / 3) * 0.3)
            newLine = UI.Line((230, 0, 0, 200), (offsetX, offsetY), (windowX * .9, offsetY))
        elif i < 6:
            offsetX = windowX * (0.2 + math.floor(victory[i][0] % 3) * 0.3)
            offsetY = windowY * 0.1
            newLine = UI.Line((230, 0, 0, 200), (offsetX, offsetY), (offsetX, windowY * .9))
        elif i == 6:
            offsetX = windowX * 0.15
            offsetY = windowY * 0.15
            newLine = UI.Line((230, 0, 0, 200), (offsetX, offsetY), (windowX * .85, windowY * .85))
        else:
            offsetX = windowX * 0.15
            offsetY = windowY * 0.15
            newLine = UI.Line((230, 0, 0, 200), (offsetX, windowY * .85), (windowX * .85, offsetY), True)
        self.markers.append(newLine)
        createWindow([self.displayGrid] + self.markers)
        UI.pygame.display.flip()

    def checkForVictory(self):
        if self.turn == 1:
            gridWins = self.oGridWins
        else:
            gridWins = self.xGridWins
        for i in range(0, len(victory)):
            if set(gridWins).intersection(set(victory[i])) == set(victory[i]):
                if not self.text:
                    self.victoryLine(i)
                self.running = False

    def checkForGridVictory(self):
        if self.turn == 1:
            marker = "O"
        else:
            marker = "X"
        for i in range(0, 3):
            if self.grid[self.currentGrid][i][0] == marker and self.grid[self.currentGrid][i][1] == marker \
                    and self.grid[self.currentGrid][i][2] == marker:
                self.invalidGrids.append(self.currentGrid)
                if not self.text:
                    offsetX = windowX * (0.05 + (self.currentGrid % 3) * 0.3)
                    offsetY = windowY * (0.1 + math.floor(self.currentGrid / 3) * 0.3 + i * 0.1)
                    newLine = UI.Line((230, 0, 0, 200), (windowX * 0.01 + offsetX, offsetY),
                                      (windowX * 0.29 + offsetX, offsetY))
                    self.markers.append(newLine)
                return True
        for i in range(0, 3):
            if self.grid[self.currentGrid][0][i] == marker and self.grid[self.currentGrid][1][i] == marker \
                    and self.grid[self.currentGrid][2][i] == marker:
                self.invalidGrids.append(self.currentGrid)
                if not self.text:
                    offsetX = windowX * (0.1 + (self.currentGrid % 3) * 0.3 + i * 0.1)
                    offsetY = windowY * (0.05 + math.floor(self.currentGrid / 3) * 0.3)
                    newLine = UI.Line((230, 0, 0, 200), (offsetX, offsetY + windowY * 0.01),
                                      (offsetX, offsetY + windowY * 0.29))
                    self.markers.append(newLine)
                return True
        if self.grid[self.currentGrid][0][0] == marker and self.grid[self.currentGrid][1][1] == marker \
                and self.grid[self.currentGrid][2][2] == marker:
            self.invalidGrids.append(self.currentGrid)
            if not self.text:
                offsetX = windowX * (0.05 + (self.currentGrid % 3) * 0.3)
                offsetY = windowY * (0.05 + math.floor(self.currentGrid / 3) * 0.3)
                newLine = UI.Line((230, 0, 0, 200), (offsetX + windowX * 0.03, offsetY + windowY * 0.03),
                                  (windowX * 0.27 + offsetX, offsetY + windowY * 0.27))
                self.markers.append(newLine)
            return True
        if self.grid[self.currentGrid][0][2] == marker and self.grid[self.currentGrid][1][1] == marker \
                and self.grid[self.currentGrid][2][0] == marker:
            self.invalidGrids.append(self.currentGrid)
            if not self.text:
                offsetX = windowX * (0.05 + (self.currentGrid % 3) * 0.3)
                offsetY = windowY * (0.05 + math.floor(self.currentGrid / 3) * 0.3)
                newLine = UI.Line((230, 0, 0, 200), (offsetX + windowX * 0.03, offsetY + windowY * 0.27),
                                  (windowX * 0.27 + offsetX, offsetY + windowY * 0.03), True)
                self.markers.append(newLine)
            return True
        return False

    def getMouseGrid(self, mouseX, mouseY):
        if mouseX < windowX * .05 or mouseX > windowX * .95 or mouseY < windowY * .05 or mouseY > windowY * .95:
            return 9, 9, 9
        mouseX = math.floor((mouseX - windowX * .05) / (windowX * .3))
        mouseY = math.floor((mouseY - windowY * .05) / (windowY * .3))
        grid = mouseX + mouseY * 3
        return grid, mouseX, mouseY

    def getMouseSquare(self, grid, mouseX, mouseY):
        mouseX = mouseX - windowX * .05 - (grid % 3) * windowX * .3
        mouseY = mouseY - windowY * .05 - (math.floor(grid / 3)) * windowY * .3
        mouseX = math.floor(mouseX / (windowX * .1))
        mouseY = math.floor(mouseY / (windowY * .1))
        grid = mouseX + mouseY * 3
        return grid, mouseX, mouseY

    def applyResize(self, w, h):
        global windowX
        global windowY
        global screen
        if w == UI.oldWindowX:
            windowY = h
            windowX = h
        elif h == UI.oldWindowY:
            windowX = w
            windowY = w
        else:
            windowX = math.floor((w + h) / 2)
            windowY = windowX
        if windowX < 400:
            windowX = 400
            windowY = 400
        screen = UI.pygame.display.set_mode((windowX, windowY), UI.pygame.RESIZABLE, 32)
        self.shadowMarker = UI.Marker(self.shadowMarker.Type, (255, 0, 0, 128), windowX * .08, windowY * .08)
        UI.rescale(self.boxes + self.markers, windowX, windowY)

    def getTurn(self, myTurn, isMultiplayer):
        global screen
        if not isMultiplayer:
            myTurn = True
        self.clock = UI.pygame.time.Clock()
        self.boxes = []
        validGrids = []
        changingGrid = self.currentGrid in self.invalidGrids
        if changingGrid:
            # display all available grids if current grid isn't playable
            for i in range(0, 9):
                if not i in self.invalidGrids:
                    self.boxes.append(UI.Box((0, 100, 200, 50), (
                        windowX * (0.05 + (i % 3) * 0.3), windowY * (0.05 + math.floor(i / 3) * 0.3)),
                                             windowX * 0.3 + 1,
                                             windowY * 0.3 + 1))
                    validGrids.append(i)
        else:
            self.boxes.append(UI.Box((0, 100, 200, 50), (
                windowX * (0.05 + (self.currentGrid % 3) * 0.3),
                windowY * (0.05 + math.floor(self.currentGrid / 3) * 0.3)),
                                     windowX * 0.3 + 1, windowY * 0.3 + 1))
            validGrids.append(self.currentGrid)
            validSquares = self.validSquares(self.currentGrid)
        grid, square = 9, 9
        squareX = 0
        squareY = 0
        lastSent = (9, 9)
        while True:
            mouseX, mouseY = UI.pygame.mouse.get_pos()
            self.markers[0].checkHighlight(mouseX, mouseY)
            if myTurn:
                grid, gridX, gridY = self.getMouseGrid(mouseX, mouseY)
                if grid < 9 and grid in validGrids:
                    square, squareX, squareY = self.getMouseSquare(grid, mouseX, mouseY)
                else:
                    square = 9
            else:
                received = self.get_command()
                if not received:
                    return
                if received != True:
                    if received[0] == "!":
                        # opponent turn taken
                        self.currentGrid = int(received[1])
                        self.currentSquare = int(received[2])
                        self.squareX = self.currentSquare % 3
                        self.squareY = math.floor(self.currentSquare / 3)
                        break
                    else:
                        received = received[1:]
                    # create ghost marker
                    grid = int(received[0])
                    square = int(received[1])
                    squareX = square % 3
                    squareY = math.floor(square / 3)
                    gridX = grid % 3
                    gridY = math.floor(grid / 3)

            if square != 9 and -1 < grid < 9:
                if changingGrid:
                    validSquares = self.validSquares(grid)
                if square in validSquares:
                    self.shadowMarker.absX = windowX * (.06 + gridX * .3 + squareX * .1)
                    self.shadowMarker.absY = windowY * (.06 + gridY * .3 + squareY * .1)
                    createWindow([self.displayGrid] + self.markers + self.boxes + [self.shadowMarker])
                else:
                    createWindow([self.displayGrid] + self.markers + self.boxes)
            else:
                createWindow([self.displayGrid] + self.markers + self.boxes)

            if myTurn and isMultiplayer:
                if not (grid, square) == lastSent:
                    # only send ghost when needed
                    self.send_command("?" + str(grid) + str(square))
                    lastSent = (grid, square)

            UI.pygame.display.flip()
            clicked = False
            for event in UI.pygame.event.get():
                if event.type == UI.pygame.MOUSEBUTTONDOWN:
                    clicked = True
                    if square != 9 and square in validSquares and myTurn and event.button == 1:
                        self.currentGrid = grid
                        self.currentSquare = square
                        self.squareX = squareX
                        self.squareY = squareY
                        if isMultiplayer:
                            self.send_command("!" + str(grid) + str(square))
                        self.click_debounce = True
                        return False
                    else:
                        # back button
                        if event.button == 1 and (self.markers[0].colour != self.markers[0].renderColour):
                            return True
                elif event.type == UI.pygame.VIDEORESIZE:
                    self.applyResize(event.w, event.h)
                    self.displayGrid.redraw()
                elif event.type == UI.pygame.KEYDOWN:
                    if event.key == UI.pygame.K_r:
                        self.applyResize(self.defaultSize, self.defaultSize)
                        self.displayGrid.redraw()
                elif event.type == UI.pygame.QUIT:
                    UI.pygame.quit()
                    sys.exit()()

            # I think this was to improve responsiveness
            # debounce avoids accidental turns from the same button press
            if not clicked and not self.click_debounce and UI.pygame.mouse.get_pressed()[0]:
                if square != 9 and square in validSquares and myTurn:
                    self.currentGrid = grid
                    self.currentSquare = square
                    self.squareX = squareX
                    self.squareY = squareY
                    if isMultiplayer:
                        self.send_command("!" + str(grid) + str(square))
                    self.click_debounce = True
                    return False
                else:
                    if (self.markers[0].colour != self.markers[0].renderColour):
                        return True
            elif not UI.pygame.mouse.get_pressed()[0]:
                self.click_debounce = False
            self.clock.tick(60)

    def getTurnText(self, isMultiplayer):
        if self.currentGrid in self.invalidGrids:
            print("What grid do you want to play in?")
            self.currentGrid = input()
            while self.currentGrid not in validNumbers or int(self.currentGrid) - 1 in self.invalidGrids:
                print("Invalid grid, please try again")
                self.currentGrid = input()
            self.currentGrid = int(self.currentGrid) - 1
        print("You are in grid " + str(self.currentGrid + 1))
        print("Which square do you want to play in?")
        self.currentSquare = input()
        validSquares = self.validSquares(self.currentGrid)
        while self.currentSquare not in validNumbers or int(self.currentSquare) not in validSquares:
            print("Invalid square, please try again")
            self.currentSquare = input()
        self.currentSquare = int(self.currentSquare) - 1
        self.squareY = (self.currentSquare // 3)
        self.squareX = self.currentSquare % 3
        if isMultiplayer:
            self.send_command("!" + str(self.currentGrid) + str(self.currentSquare))

    def waitForTurn(self):
        print("Waiting for opponent's turn")
        recieved = self.get_command()
        if not recieved:
            return False
        while recieved[0] == "?":
            recieved = self.get_command()
            if not recieved:
                return False
        if recieved[0] == ".":
            print("Opponent disconnected")
            return False
        print("Your opponent went in grid " + str(1 + int(recieved[1])) + ", square " + str(1 + int(recieved[2])))
        print()
        self.currentGrid = int(recieved[1])
        self.currentSquare = int(recieved[2])
        self.squareY = (self.currentSquare // 3)
        self.squareX = self.currentSquare % 3

    def actOnTurn(self):
        if self.turn == 1:
            marker, marker_long, new_turn = "X", "Cross", 2
        else:
            marker, marker_long, new_turn = "O", "Nought", 1

        if not self.text:
            gridX = self.currentGrid % 3
            gridY = math.floor(self.currentGrid / 3)
            newMarker = UI.Marker(marker_long, (0, 0, 0), windowX * .08, windowY * .08)
            newMarker.absX = windowX * (.06 + gridX * .3 + self.squareX * .1)
            newMarker.absY = windowY * (.06 + gridY * .3 + self.squareY * .1)
            self.markers.append(newMarker)
        self.grid[self.currentGrid][self.squareY][self.squareX] = marker
        self.turn = new_turn

        if self.checkForGridVictory():
            if self.turn == 1:
                self.oGridWins.append(self.currentGrid)
            else:
                self.xGridWins.append(self.currentGrid)
            self.checkForVictory()
        elif len(self.validSquares(self.currentGrid)) == 0:
            self.invalidGrids.append(self.currentGrid)
        self.currentGrid = self.currentSquare


if __name__ == "__main__":
    game = Launcher(text)
