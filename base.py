import pygame
import tkSimpleDialog
import Tkinter as Tk
import os

class MyDialog(tkSimpleDialog.Dialog):
    def body(self, master):
        Tk.Label(master, text="width").grid(row=0)
        Tk.Label(master, text="height").grid(row=1)

        self.e1 = Tk.Entry(master)
        self.e2 = Tk.Entry(master)

        self.e1.grid(row=0, column=1)
        self.e2.grid(row=1, column=1)
        return self.e1 # initial focus

    def apply(self):
        self.first = self.e1.get()
        self.second = self.e2.get()
        #print(first)
        #print(second)


def load_png(name):
    """
    Load image and return image object
    """
    fullname = os.path.join('data', name)
    try:
        image = pygame.image.load(fullname)
        if image.get_alpha() is None:
            image = image.convert()
        else:
            image = image.convert_alpha()
    except pygame.error, message:
        print 'Cannot load image:', fullname
        raise SystemExit(message)
    return image, image.get_rect()


def blurSurf(surface, amt):
    """
    Blur the given surface by the given 'amount'.  Only values 1 and greater are valid.  Value 1 = no blur.
    """
    if amt < 1.0:
        raise ValueError("Arg 'amt' must be greater than 1.0, passed in value is %s" % amt)
    scale = 1.0/float(amt)
    surf_size = surface.get_size()
    scale_size = (int(surf_size[0]*scale), int(surf_size[1]*scale))
    surf = pygame.transform.smoothscale(surface, scale_size)
    surf = pygame.transform.smoothscale(surf, surf_size)
    return surf

def isPointInsideRect(x, y, rect):
    """
    Checks if point is inside some rectangle (Rect object)
    :param x: horizontal
    :param y: vertical
    :param rect: rect to check inside
    :return: bool
    """
    if (x > rect.left) and (x < rect.right) and (y > rect.top) and (y < rect.bottom):
        return True
    else:
        return False

def doRectsOverlap(rect1, rect2):
    """
    Checks if rectangles (Rect objects) overlap
    :param rect1: first Rect object
    :param rect2: second Rect object
    :return: bool
    """
    for a, b in [(rect1, rect2), (rect2, rect1)]:
        # Check if a's corners are inside b
        if((isPointInsideRect(a.left, a.top, b)) or
               (isPointInsideRect(a.left, a.bottom, b)) or
               (isPointInsideRect(a.right, a.top, b)) or
               (isPointInsideRect(a.right, a.bottom, b))):
            return True
    return False

class Tileset():
    def __init__(self, name):
        self.name = name
        self.image, self.rect = load_png(self.name)
        self.pos_x = 0
        self.pos_y = 0

    def change_pos_rel(self, x, y):
        self.rect.x += x
        #self.rect.move(x, y)
        self.pos_x += x
        self.rect.y += y
        self.pos_y += y
        #self.rect.x, self.rect.y = self.pos_x, self.pos_y
        #print(self.image.get_rect())
        print(self.rect, self.pos_x, self.pos_y)


class SelectedTile():
    def __init__(self, x, y):
        self.image = pygame.Surface((32, 32))
        self.pos_x = x
        self.pos_y = y
        self.pos_tileset_x = 0
        self.pos_tileset_y = 0
        #self.rect = Rect(x, y, 32, 32)
        self.collision = False
        self.event = None

    def select_tile(self, postx, posty):
        self.pos_tileset_x = postx
        self.pos_tileset_y = posty

    def mutate(self, t):
        t.pos_tileset_x = self.pos_tileset_x
        t.pos_tileset_y = self.pos_tileset_y
        #t.rect = self.rect
        t.collision = self.collision
        t.event = self.event
        t.image.blit(self.image, (0, 0))


class Tile():
    def __init__(self):
        self.image = pygame.Surface((32, 32))
        #self.pos_x = None
        #self.pos_y = None
        self.pos_tileset_x = None
        self.pos_tileset_y = None
        #self.rect = None
        self.collision = False
        self.event = None


class Playfield():
    def __init__(self, w, h, tileset):
        self.mapp = []
        self.npcmapp = []
        self.tileset = Tileset(tileset)
        for y in xrange(h):
            wline = []
            for x in xrange(w):
                wline += [Tile()]
            self.mapp += [wline]
        for y in xrange(h):
            wline = []
            for x in xrange(w):
                wline += [None]
            self.npcmapp += [wline]
        #pprint(self.mapp)
        self.maxx = w
        self.maxy = h

    def process_images(self):
        for y in xrange(len(self.mapp)):
            for x in xrange(len(self.mapp[y])):
                #print(self.mapp[y][x].pos_tileset_x, self.mapp[y][x].pos_tileset_y)
                try:
                    self.mapp[y][x].image.blit(self.tileset.image, (0, 0), (self.mapp[y][x].pos_tileset_x, self.mapp[y][x].pos_tileset_y, 32, 32))
                except TypeError:
                    #self.mapp[y][x].image.blit(self.mapp[y][x].image, (x*32, y*32), (0, 0, 32, 32))
                    pass


class Player_c:
    def __init__(self, x, y, imagefilename, displaysurf):
        self.x = int(x)
        self.y = int(y)
        self.image = load_png(imagefilename)[0] # load_png("image.png") in init field required
        self.real_x = self.x * 32
        self.real_y = self.y * 32
        self._display_surf = displaysurf
        self.name = None
        #stats
        #_b for bonuses
        self.STR = 0
        self.DEX = 0
        self.INT = 0
        self.ATK_b = 0
        self.DEF_b = 0
        self.HP = 0
        self.ATK = self.STR + (self.STR * (self.DEX/2)) + self.ATK_b
        self.DEF = self.INT + (self.INT * (self.DEX/2)) + self.DEF_b

    def _recalculate_stats(self):
        self.ATK = self.STR + (self.STR * (self.DEX/2)) + self.ATK_b
        self.DEF = self.INT + (self.INT * (self.DEX/2)) + self.DEF_b


class Camera:
    def __init__(self, viewportmaxx, viewportmaxy, worldsizex, worldsizey, Playerclass):
        self.viewportmaxx = viewportmaxx
        self.viewportmaxy = viewportmaxy
        self.worldsizex = worldsizex
        self.worldsizey = worldsizey
        self.player = Playerclass
        self.playerx = self.player.x
        self.playery = self.player.y
        self.offsetmaxx = self.worldsizex - self.viewportmaxx
        self.offsetmaxy = self.worldsizey - self.viewportmaxy
        self.offsetminx = 0
        self.offsetminy = 0
        self.calculate_pos()

    def calculate_pos(self):
        self.playerx = self.player.x
        self.playery = self.player.y
        self.x = self.playerx - self.viewportmaxx / 2
        self.y = self.playery - self.viewportmaxy / 2

        if self.x > self.offsetmaxx:
            self.x = self.offsetmaxx

        elif self.x < self.offsetminx:
            self.x = self.offsetminx

        if self.y > self.offsetmaxy:
            self.y = self.offsetmaxy

        elif self.y < self.offsetminy:
            self.y = self.offsetminy

        if self.worldsizey < self.viewportmaxy:
            self.y = self.offsetmaxy/2.0
        if self.worldsizex < self.viewportmaxx:
            self.x = self.offsetmaxx/2.0


class Queue:
    def __init__(self):
        #1 --> 2 --> 3
        #reversed executing
        self.levelone = []
        self.leveltwo = []
        self.levelthree = []

    def pop_all(self):
        self.levelone = []
        self.leveltwo = []
        self.levelthree = []

class Resource:
    def __init__(self, image, position=(0, 0)):
        self.image = image
        self.position = position
        self.x = position[0]
        self.y = position[1]

class NPC:
    def __init__(self, x, y, imagefilename, scriptfilename, displaysurf):
        self.script = scriptfilename
        self.x = int(x)
        self.y = int(y)
        self.image = load_png(imagefilename)[0] # load_png("image.png") in init field required
        self.real_x = self.x * 32
        self.real_y = self.y * 32
        self._display_surf = displaysurf
        self.name = None
        self.collision = True
        self.event = self.script
        #stats
        #_b for bonuses
        self.STR = 0
        self.DEX = 0
        self.INT = 0
        self.ATK_b = 0
        self.DEF_b = 0
        self.HP = 0
        self.ATK = self.STR + (self.STR * (self.DEX/2)) + self.ATK_b
        self.DEF = self.INT + (self.INT * (self.DEX/2)) + self.DEF_b

    def _recalculate_stats(self):
        self.ATK = self.STR + (self.STR * (self.DEX/2)) + self.ATK_b
        self.DEF = self.INT + (self.INT * (self.DEX/2)) + self.DEF_b