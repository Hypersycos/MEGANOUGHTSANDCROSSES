import pygame
import math

windowX = 0
windowY = 0
oldWindowX = 0
oldWindowY = 0

class Button:
    def __init__(self, text, textcolour, colour, width, height, absX, absY, font='Comic Sans MS'):
        self.text = Text(text, textcolour, font)
        self.text.scale(width, height)
        try:
            colour[3] == 0
        except:
            colour = (colour[0], colour[1], colour[2], 255)
        self.colour = colour
        self.renderColour = colour
        self.width = width
        self.height = height
        self.image = pygame.Surface((width, height), pygame.SRCALPHA)
        self.absX = absX
        self.absY = absY
        self.draw()

    def rescale(self, xScale, yScale):
        self.width = self.width * xScale
        self.height = self.height * yScale
        self.absX = self.absX * xScale
        self.absY = self.absY * yScale
        self.image = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        self.text.scale(self.width, self.height)
        self.draw()

    def draw(self):
        self.image.fill(self.renderColour)
        w, h = self.text.font.size(self.text.text)
        w, h = (self.width - w) // 2, (self.height - h) // 2
        self.image.blit(self.text.image, (w, h))

    def checkHighlight(self, mouseX, mouseY):
        h = .75
        if mouseX > self.absX and mouseX < self.absX + self.width and mouseY > self.absY and mouseY < self.absY + self.height:
            if self.renderColour == self.colour:
                self.renderColour = (self.colour[0] * h, self.colour[1] * h, self.colour[2] * h, self.colour[3])
                self.draw()
        else:
            if not self.renderColour == self.colour:
                self.renderColour = self.colour
                self.draw()


class TextBox(Button):
    def __init__(self, textcolour, colour, width, height, absX, absY,
                 validCharacters='abcdefghijklmnopqrstuvwxyz!?.,;:"/()£$%&*', charLimit=0, font='Comic Sans MS'):
        super().__init__("", textcolour, colour, width, height, absX, absY, font)
        self.charLimit = charLimit
        self.text = Text("", textcolour)
        self.validCharacters = list(validCharacters)
        self.selected = False
        h = 1.5
        s = .1
        self.highlightColour = (self.colour[0] * h, self.colour[1] * h, self.colour[2] * h, self.colour[3])
        self.selectColour = (self.colour[0] * s, self.colour[1] * s, self.colour[2] * s, self.colour[3])

    def click(self):
        if self.selected:
            self.selected = False
        else:
            self.selected = True

    def checkHighlight(self, mouseX, mouseY):
        if mouseX > self.absX and mouseX < self.absX + self.width and mouseY > self.absY and mouseY < self.absY + self.height:
            if self.renderColour in [self.colour, self.selectColour]:
                self.renderColour = self.highlightColour
                self.draw()
        else:
            if self.selected:
                self.renderColour = self.selectColour
            else:
                self.renderColour = self.colour
            self.draw()

    def typing(self, typed):
        if typed == "back":
            self.text.text = self.text.text[:-1]
        else:
            if (typed.lower() in self.validCharacters or self.validCharacters == []) and (
                    len(self.text.text) < self.charLimit or self.charLimit == 0):
                self.text.text = self.text.text + typed
        self.text.scale(self.width, self.height)
        self.draw()


class Text:
    def __init__(self, text, colour, fontName='Comic Sans MS', absX=0, absY=0):
        self.fontName = fontName
        self.text = text
        self.colour = colour
        self.textSize = 12
        self.absX = absX
        self.absY = absY
        self.Font()
        self.render()

    def getDimensions(self):
        return self.font.size(self.text)

    def pos(self, x, y):
        self.absX = x
        self.absY = y

    def scale(self, width, height):
        i = 1
        j = 0
        w = 0
        h = 0

        # find limits by doubling i until invalid
        while w < width and h < height:
            j = i
            i += i
            self.font = pygame.font.SysFont(self.fontName, i)
            w, h = self.font.size(self.text)
        # use binary search to find optimal text size within limits
        while i - j > 1:
            self.font = pygame.font.SysFont(self.fontName, (i + j) // 2)
            w, h = self.font.size(self.text)
            if w > width or h > height:
                i = (i + j) // 2
            else:
                j = (i + j) // 2
        self.textSize = j
        self.Font()
        self.render()

    def Font(self):
        self.font = pygame.font.SysFont(self.fontName, self.textSize)

    def setFontName(self, fontName):
        self.fontName = fontName
        self.Font()
        self.render()

    def setFontSize(self, size):
        self.textSize = size
        self.Font()
        self.render()

    def setFont(self, fontName, size):
        self.fontName = fontName
        self.size = size
        self.Font()
        self.render()

    def render(self):
        self.image = self.font.render(self.text, True, self.colour)

    def changeText(self, text):
        self.text = text
        self.render()

    def recolour(self, colour):
        self.colour = colour
        self.render()


class MultiLineTextBox(TextBox):
    def __init__(self, textcolour, colour, width, height, absX, absY,
                 validCharacters='abcdefghijklmnopqrstuvwxyz!?.,;:"/()£$%&*', lines=0, charLimit=80,
                 font='Comic Sans MS'):
        super().__init__(textcolour, colour, width, height, absX, absY, validCharacters, charLimit, font)
        self.text = TextWrapped("", textcolour, colour, width, height, font, lines)

    def rescale(self, xScale, yScale):
        self.width = self.width * xScale
        self.height = self.height * yScale
        self.text.width = self.width
        self.text.height = self.height
        self.absX = self.absX * xScale
        self.absY = self.absY * yScale
        self.image = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        self.text.resize()
        self.draw()

    def draw(self):
        self.image.fill(self.renderColour)
        self.image.blit(self.text.image, (0, 0))

    def typing(self, typed):
        if typed == "back":
            self.text.text = self.text.text[:-1]
        else:
            if (typed.lower() in self.validCharacters or self.validCharacters == []) and (len(self.text.text) < self.charLimit or self.charLimit == 0):
                self.text.text = self.text.text + typed
        self.text.fullscale()
        self.draw()


class TextWrapped:
    # This should probably inherit from Text, but I re-used the same function names to mean something else..
    def __init__(self, text, colour, backgroundColour, width, height, fontName='Comic Sans MS', lines=0, absX=0,
                 absY=0):
        if lines == 0:
            lines = 1
            self.autoWrap = True
        else:
            self.autoWrap = False
        self.fontName = fontName
        self.text = text
        self.texts = []
        self.colour = colour
        self.textSize = 12
        self.absX = absX
        self.absY = absY
        self.width = width
        self.height = height
        self.backgroundColour = backgroundColour
        self.lines = lines
        self.image = pygame.Surface((width, height), pygame.SRCALPHA)
        self.lastLen = 0
        for i in range(0, lines):
            self.texts.append(Text("", colour, fontName, 0, round(i * height / lines)))
        self.resize()
        self.Font()
        self.render()

    def resize(self):
        self.image = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        i = 1
        j = 0
        w = 0
        h = 0
        # same binary search as Text
        while h < self.height / self.lines:
            j = i
            i += i
            font = pygame.font.SysFont(self.fontName, i)
            w, h = font.size("ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789!")
        while i - j > 1:
            font = pygame.font.SysFont(self.fontName, (i + j) // 2)
            w, h = font.size("h")
            if h > self.height / self.lines:
                i = (i + j) // 2
            else:
                j = (i + j) // 2
        self.textSize = j
        for i in range(0, len(self.texts)):
            self.texts[i].textSize = self.textSize
            self.texts[i].Font()
            self.texts[i].render()
            self.texts[i].absY = round(i * self.height / self.lines)
        self.fullscale()

    def fullscale(self):
        font = pygame.font.SysFont(self.fontName, self.textSize)
        remaining = self.text
        for i in range(0, self.lines):
            self.texts[i].text = ""
            self.texts[i].render()
        for i in range(0, self.lines):
            currentText = ""
            w, h = (0, 0)
            # fill each line
            while w <= self.width:
                if remaining == "" or w > self.width:
                    break
                currentText = currentText + remaining[0]
                remaining = remaining[1:]
                w, h = font.size(currentText)
            # crop excess
            if w > self.width:
                remaining = currentText[-1] + remaining
                currentText = currentText[:-1]
                if i + 1 >= self.lines:
                    self.lines += 1
                    self.texts.append(Text("", self.colour, self.fontName, 0, round(i * self.height / self.lines)))
                    self.resize()
                    return
            self.texts[i].text = currentText
            self.texts[i].render()
            if remaining == "":
                break
        # if not all lines filled, and final filled line isn't close to full, then reduce line count
        if self.lines > 1 and w < self.width * (1 / (i + 2) - .15) and i < self.lines - 1:
            del self.texts[-1]
            self.lines -= 1
            self.resize()
        self.render()

    # unused function, and not entirely clear what it's supposed to do

    # def scale(self):
    #     if self.autoWrap:
    #         self.fullscale()
    #         self.lastLen = len(self.text)
    #         return
    #
    #     i = 0
    #     while i < len(self.texts) and self.texts[i].text != "":
    #         i += 1
    #
    #     if i > 0:
    #         i -= 1
    #     if self.lastLen > len(self.text):
    #         self.texts[i].text = self.texts[i].text[:-1]
    #     elif self.text != "":
    #         self.texts[i].text = self.texts[i].text + self.text[-1]
    #     font = pygame.font.SysFont(self.fontName, self.textSize)
    #     w, h = font.size(self.texts[i].text)
    #     if w > self.width:
    #         self.texts[i].text = self.texts[i].text[:-1]
    #         i += 1
    #         if i >= self.lines:
    #             return
    #         self.texts[i].text = self.text[-1]
    #     self.texts[i].render()
    #     self.render()
    #     self.lastLen = len(self.text)

    # below are copy and pasted from Text

    def Font(self):
        self.font = pygame.font.SysFont(self.fontName, self.textSize)

    def setFontName(self, fontName):
        self.fontName = fontName
        self.Font()
        self.render()

    def setFontSize(self, size):
        self.textSize = size
        self.Font()
        self.render()

    def setFont(self, fontName, size):
        self.fontName = fontName
        self.size = size
        self.Font()
        self.render()

    def render(self):
        self.image.fill((255, 255, 255, 0))
        for item in self.texts:
            self.image.blit(item.image, (0, item.absY))

    def changeText(self, text):
        self.text = text
        self.render()

    def recolour(self, colour):
        self.colour = colour
        self.render()


class ScrollWrapper(pygame.sprite.Sprite):
    # not implemented, mainly because the rest of the UI's API follows no rhyme or reason
    def __init__(self, colour, scrollColour, height, width, absX=0, absY=0):
        self.items = []
        self.itemHeight = 0
        self.background = pygame.Surface((width, height), pygame.SRCALPHA)
        self.foreground = pygame.Surface((width, height), pygame.SRCALPHA)
        self.image = pygame.Surface((width, height), pygame.SRCALPHA)
        self.width = width
        self.height = height
        self.absX = absX
        self.absY = absY
        self.colour = colour
        self.scrollColour = scrollColour

    def draw(self):
        self.image.fill(self.colour)
        backColour = (self.scrollColour[0] * 0.5, self.scrollColour[1] * 0.5, self.scrollColour[2] * 0.5)
        pygame.draw.rect(self.image, backColour, pygame.Rect(self.width * 0.9, 0, self.width * 0.1, self.height))


class Marker(pygame.sprite.Sprite):
    def __init__(self, Type, colour, width, height, absX=0, absY=0):
        self.Type = Type
        self.colour = colour
        self.width = width
        self.height = height
        self.image = pygame.Surface((width, height), pygame.SRCALPHA)
        self.absX = absX
        self.absY = absY
        self.draw()

    def rescale(self, xScale, yScale):
        self.width = self.width * xScale
        self.height = self.height * yScale
        self.absX = self.absX * xScale
        self.absY = self.absY * yScale
        self.image = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        self.draw()

    def draw(self):
        self.image.fill((255, 255, 255, 0))
        if self.Type == "Cross":
            pygame.draw.line(self.image, self.colour, (0, 0), (self.width, self.height),
                             int((self.width + self.height) / 10))
            pygame.draw.line(self.image, self.colour, (self.width, 0), (0, self.height),
                             int((self.width + self.height) / 10))
        else:
            if self.height > self.width:
                pygame.draw.circle(self.image, self.colour, (int(self.width / 2), int(self.height / 2)),
                                   int(self.width / 2))
                pygame.draw.circle(self.image, (255, 255, 255, 0), (int(self.width / 2), int(self.height / 2)),
                                   int(self.width / 2 - (self.width + self.height) / 10))
            else:
                pygame.draw.circle(self.image, self.colour, (int(self.width / 2), int(self.height / 2)),
                                   int(self.height / 2))
                pygame.draw.circle(self.image, (255, 255, 255, 0), (int(self.width / 2), int(self.height / 2)),
                                   int(self.height / 2 - (self.width + self.height) / 10))


class Box(pygame.sprite.Sprite):
    def __init__(self, colour, pos1, width, height):
        self.colour = colour
        self.absX = pos1[0]
        self.absY = pos1[1]
        self.width = width
        self.height = height
        self.image = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        self.draw()

    def rescale(self, xScale, yScale):
        self.width = self.width * xScale
        self.height = self.height * yScale
        self.absX = self.absX * xScale
        self.absY = self.absY * yScale
        self.image = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        self.draw()

    def draw(self):
        pygame.draw.rect(self.image, self.colour, pygame.Rect(0, 0, self.width, self.height))


class Line(pygame.sprite.Sprite):
    def __init__(self, colour, pos1, pos2, reverse=False):
        self.colour = colour
        if reverse:
            self.width = int((abs(pos2[0] - pos1[0]) + abs(pos2[1] - pos1[1])) / 15)
        else:
            self.width = int((pos2[0] - pos1[0] + pos2[1] - pos1[1]) / 15)
        self.pos1 = pos1
        self.pos2 = pos2
        if reverse:
            self.image = pygame.Surface(
                (abs(pos2[0] - pos1[0]) + self.width * 2, abs(pos2[1] - pos1[1]) + self.width * 2), pygame.SRCALPHA)
        else:
            self.image = pygame.Surface((pos2[0] - pos1[0] + self.width * 2, pos2[1] - pos1[1] + self.width * 2),
                                        pygame.SRCALPHA)
        self.absX = pos1[0] - self.width
        if reverse:
            self.absY = pos2[1] - self.width
        else:
            self.absY = pos1[1] - self.width
        self.draw(reverse)

    def draw(self, reverse):
        self.image.fill((255, 255, 255, 0))
        if reverse:
            pygame.draw.line(self.image, self.colour, (self.width, abs(self.pos2[1] - self.pos1[1]) + self.width),
                             (self.pos2[0] - self.pos1[0] + self.width, self.width), self.width)
        else:
            pygame.draw.line(self.image, self.colour, (self.width, self.width),
                             (self.pos2[0] - self.pos1[0] + self.width, self.pos2[1] - self.pos1[1] + self.width),
                             self.width)


def normalizeTextSize(boxes):
    if len(boxes) == 0:
        return
    size = boxes[0].text.textSize
    for item in boxes[1:]:
        if item.text.textSize < size:
            size = item.text.textSize
    for item in boxes:
        item.text.textSize = size
        item.text.Font()
        item.text.render()
        item.draw()


def rescale(items, newWindowX, newWindowY):
    # horrible global usage since was originally all in one file
    global oldWindowX
    global oldWindowY
    global windowX
    global windowY
    windowX = newWindowX
    windowY = newWindowY
    xScale = windowX / oldWindowX
    yScale = windowY / oldWindowY
    for item in items:
        item.rescale(xScale, yScale)
    oldWindowX = windowX
    oldWindowY = windowY


class Grid(pygame.sprite.Sprite):
    def __init__(self):
        self.absX = 0
        self.absY = 0
        self.redraw()

    def redraw(self):
        self.image = pygame.Surface((windowX, windowY), pygame.SRCALPHA)
        self.image.fill((255, 255, 255, 0))
        lineWidth = max(windowX / 125, 4)

        # draw small gridlines
        y = windowY * 0.05 - lineWidth / 8
        # vertical grid loop
        for i in range(0, 3):
            x = windowX * 0.05 - lineWidth / 8
            # horizontal grid loop
            for j in range(0, 3):
                # vertical lines
                dist = windowX * 0.1
                for k in range(1, 3):
                    pygame.draw.rect(self.image, (100, 100, 100),
                                     pygame.Rect(x + dist * k, y, lineWidth / 4, windowY * 0.3 + lineWidth / 4))

                # horizontal lines
                dist = windowY * 0.1
                for k in range(1, 3):
                    pygame.draw.rect(self.image, (100, 100, 100),
                                     pygame.Rect(x, y + dist * k, windowX * 0.3 + lineWidth / 4, lineWidth / 4))
                x += windowX * 0.3
            y += windowY * 0.3

        # draw big grid lines
        x = windowX * 0.05 - lineWidth / 4
        y = windowY * 0.05 - lineWidth / 4
        # vertical lines
        dist = windowX * 0.3
        for i in range(1, 3):
            pygame.draw.rect(self.image, (0, 0, 0),
                             pygame.Rect(x + dist * i, y, lineWidth / 2, windowY * 0.9 + lineWidth / 2))

        # horizontal lines
        dist = windowY * 0.3
        for i in range(1, 3):
            pygame.draw.rect(self.image, (0, 0, 0),
                             pygame.Rect(x, y + dist * i, windowX * 0.9 + lineWidth / 2, lineWidth / 2))

        # grid border
        x = math.ceil(windowX * 0.05 - lineWidth)
        y = math.ceil(windowY * 0.05 - lineWidth)
        pygame.draw.rect(self.image, (0, 0, 0), pygame.Rect(x, y, lineWidth, windowY * 0.9 + lineWidth))
        pygame.draw.rect(self.image, (0, 0, 0),
                         pygame.Rect(windowX - x - lineWidth, y, lineWidth, windowY * 0.9 + lineWidth))
        pygame.draw.rect(self.image, (0, 0, 0), pygame.Rect(x, y, windowX * 0.9 + lineWidth, lineWidth))
        pygame.draw.rect(self.image, (0, 0, 0),
                         pygame.Rect(x, windowY - y - lineWidth, windowX * 0.9 + lineWidth, lineWidth))
        pygame.draw.rect(self.image, (0, 0, 0),
                         pygame.Rect(windowX - x - lineWidth, windowY - y - lineWidth, lineWidth, lineWidth))