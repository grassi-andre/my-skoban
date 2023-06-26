import os
import threading
import json

from tkinter import *

from pynput.keyboard import Listener, Key

from lib.database import Database



Screen_width = 576
Screen_height = 648
BoardWidth = 576
BoardHeight = 576
BlockSize = 64

Level = 1
MaxLevel = 1
Couche1 = []
Couche2 = []
BoxPosition = {}
isPlayer = None
Boxes = []
placedBoxes = []

def precLevel():
    if Level > 1:
        createLevel(Level - 1)
        

def nextLevel():
    if Level < 6:
        if Level + 1 > MaxLevel :
            isLoaded = True
            for boxe in Boxes:
                if not boxe.isPlaced:
                    return
        
        createLevel(Level + 1)
       
def restartLevel():
    createLevel(Level)

cCouche1 = []
cCouche2 = []
cBoxPosition = []
cPlayer = None

Screen = Tk()
Screen.title("Sokoban")
Screen.geometry(str(Screen_width) + "x" + str(Screen_height))
Screen.resizable(False, False)

Screen.iconbitmap(os.getcwd() + "//assets//playerFace.ico")

tableau = Canvas(Screen, width=BoardWidth, height=BoardHeight)
tableau.pack()

btnLevelPrec = Button(text="Level précédent", width=14, height=2, font=("Segoe UI", 12), command=precLevel)
btnLevelPrec.place(x=5, y=583)

btnLevelPrec = Button(text="Level Suivant", width=14, height=2, font=("Segoe UI", 12), command=nextLevel)
btnLevelPrec.place(x=145, y=583)

btnLevelPrec = Button(text="Recommencer", width=18, height=2, font=("Segoe UI", 12), command=restartLevel)
btnLevelPrec.place(x=397, y=583)


labelLevel = Label(text="Level : " + str(Level), font=("Segoe UI", 14), width=9, height=2, borderwidth=2, relief="ridge", justify="center")
labelLevel.place(x=286, y=584)

ground = []
for i in range(6):
    ground.append(PhotoImage(file=os.getcwd() + "//assets//Default Size//Ground//" + str(i) + ".png"))

crates = []
for i in range(2):
    crates.append(PhotoImage(file=os.getcwd() + "//assets//Default Size//Crates//crate_" + str(i) + ".png"))

block = PhotoImage(file=os.getcwd() + "//assets//Default Size//Blocks//block_05.png")
player = PhotoImage(file=os.getcwd() + "//assets//Default Size//Player//player_05.png")

def getLevelProg():
    global Level, MaxLevel

    connexion = Database()
    getConnexion = connexion.get()

    Level = getConnexion[0]
    MaxLevel = getConnexion[1]

def render():

    global cCouche1, cCouche2, cBoxPosition, cPlayer

    for i in cCouche1:
        tableau.delete(i)
    cCouche1 = []

    for i in cCouche2:
        tableau.delete(i)
    cCouche2 = []
    
    for i in cBoxPosition:
        tableau.delete(i)
    cBoxPosition = []

    tableau.delete(cPlayer)

    cPlayer = None

    for i in range(len(Couche1)):
        for j in range(len(Couche1[i])):
            cCouche1.append(
                tableau.create_image(j * BlockSize + 32, i * BlockSize + 32, image=ground[Couche1[i][j]])
            )

    for i in range(len(Couche2)):
        for j in range(len(Couche2[i])):
            if Couche2[i][j] != 0 :
                cCouche2.append(
                    tableau.create_image(j * BlockSize + 32, i * BlockSize + 32, image=block)
                )

    

    for placedBox in placedBoxes:
        placedBox.render()
    Player.render(self=isPlayer)
    for boxe in Boxes:
        boxe.render()


def createLevel(index):
    global Level, MaxLevel, Couche1, Couche2, BoxPosition,  isPlayer, Boxes, placedBoxes, labelLevel

    Couche1 = []
    Couche2 = []
    BoxPosition = {}

    isPlayer = None
    Boxes = []
    placedBoxes = []

    with open(os.getcwd() + "//levels.json", "r") as file:
        createdFile = json.loads(file.read())["level{}".format(index)]

        Couche1 = createdFile["layer1"]
        Couche2 = createdFile["layer2"]
        BoxPosition = createdFile["crates"]

        Level = index

        if Level > MaxLevel:
            MaxLevel = Level

        isPlayer = Player(createdFile["playerPos"]["x"], createdFile["playerPos"]["y"])

        for element in createdFile["cratesAreas"]:
            placedBoxes.append(PlacedBox(element["x"], element["y"], element["sprite"]))

        for element in createdFile["crates"]: 
            Boxes.append(Box(element["x"], element["y"]))

        labelLevel.config(text="Level : " + str(Level))

        getConnexion = Database()
        getConnexion.save(Level, MaxLevel)
        
        render()


class Player:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.image = tableau.create_image(self.x * BlockSize + 32, self.y * BlockSize + 32, image=player)
    
    def render(self):
        tableau.delete(self.image)
        self.image = tableau.create_image(self.x * BlockSize + 32, self.y * BlockSize + 32, image=player)

    def mouvement(self, posX, posY):
        possibleMoove = True

        self.x += posX
        self.y += posY

        if Couche2[self.y][self.x] != 0:
            possibleMoove = False

        for boxe in Boxes:
            if boxe.x == self.x and boxe.y == self.y:
                possibleMoove = boxe.mouvement(posX, posY)

        if not possibleMoove:
            self.x -= posX
            self.y -= posY

class Box:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.image = None

        self.isPlaced = False
        for boxe in placedBoxes:
            if boxe.x == self.x and boxe.y == self.y:
                self.isPlaced = True
                break
        self.render()
        
    def render(self):
        tableau.delete(self.image)

        if not self.isPlaced:
            self.image = tableau.create_image(self.x * BlockSize + 32, self.y * BlockSize + 32, image=crates[0])

        else:
            self.image = tableau.create_image(self.x * BlockSize + 32, self.y * BlockSize + 32, image=crates[1])

    def mouvement(self, posX, posY):
        possibleMoove = True

        self.x += posX
        self.y += posY

        if Couche2[self.y][self.x] != 0:
            possibleMoove = False

        for boxe in Boxes:
            if boxe != self:
                if boxe.x == self.x and boxe.y == self.y:
                    possibleMoove = False

        if possibleMoove:
            finsished = True
            self.isPlaced = False
            for boxe in placedBoxes:
                if boxe.x == self.x and boxe.y == self.y:
                    self.isPlaced = True
                    break
            self.render()

        if not possibleMoove:
            self.x -= posX
            self.y -= posY
        else:
            self.render()

        return possibleMoove

class PlacedBox:
    def __init__(self, x, y, sprite):
        self.x = x
        self.y = y
        self.sprite = sprite
        self.image = tableau.create_image(self.x * BlockSize + 32, self.y * BlockSize + 32, image=ground[self.sprite])
        
    def render(self):
        tableau.delete(self.image)
        self.image = tableau.create_image(self.x * BlockSize + 32, self.y * BlockSize + 32, image=ground[self.sprite])
        
class Clavier(threading.Thread): 
    def run(self):
        with Listener(on_press=self.on_press) as listener:
            listener.join()

    def on_press(self, key):
        if key == Key.up: isPlayer.mouvement(0, -1)
        elif key == Key.down: isPlayer.mouvement(0, 1)
        elif key == Key.left:  isPlayer.mouvement(-1, 0)
        elif key == Key.right: isPlayer.mouvement(1, 0)

        isPlayer.render()

clavier = Clavier()
clavier.start()
getLevelProg()
createLevel(Level)
Screen.mainloop()