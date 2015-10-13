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

def get_from_image(x, y, tileset):
    s = pygame.Surface((32, 32))
    if (x is None) or (y is None):
        return s
    else:
        s.blit(tileset, (0, 0), (x, y, 32, 32))
    return s


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
        t.image = self.image
        t.image.blit(self.image, (0, 0))


class Tile():
    def __init__(self):
        #self.image = pygame.Surface((32, 32))
        self.image = None
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
        #ONLY FOR MAP.PY
        #DO NOT EVEN TRY TO USE IT IN GAME.PY
        #MEMORY INEFFICIENT
        for y in xrange(len(self.mapp)):
            for x in xrange(len(self.mapp[y])):
                self.mapp[y][x].image = pygame.Surface((32, 32))
                #print(self.mapp[y][x].pos_tileset_x, self.mapp[y][x].pos_tileset_y)
                try:
                    self.mapp[y][x].image.blit(self.tileset.image, (0, 0), (self.mapp[y][x].pos_tileset_x, self.mapp[y][x].pos_tileset_y, 32, 32))
                except TypeError:
                    #self.mapp[y][x].image.blit(self.mapp[y][x].image, (x*32, y*32), (0, 0, 32, 32))
                    pass

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
        #print(self.x, self.y, self.offsetmaxx, self.offsetmaxy)


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


class Item:
    def __init__(self, name="nothing", typ="nothing", equipable_where="nowhere", stats_d={}):
        self.stats_d = stats_d
        self.name = name
        self.description = ""
        self.type = typ
        self.equipable_where = equipable_where
        self.equiped = False


class EQ:
    def __init__(self, limit, stats):
        self.limit = limit
        self.stats = stats
        self.equipped = {"head":Item(),
                         "rhand":Item(),
                         "rarm":Item(),
                         "chest":Item(),
                         "larm": Item(),
                         "lhand": Item(),
                         "legs":Item(),
                         "feet": Item()}
        self.backpack = []
        self.bonuses = {}
        self.recalculate_bonuses()

    def add_item(self, piece):
        if self.limit > len(self.backpack):
            self.backpack += [piece]
        else:
            print("Backpack limit reached, remove some items!")

    def remove_item(self, piece):
        try:
            self.backpack -= [piece]
        except ValueError:
            print("Item not in backpack!")

    def equip(self, piece):
        self.equipped[piece.equipable_where] = piece
        self.recalculate_bonuses()

    '''def unequip(self, where):
        try:
            self.backpack[self.backpack.index(self.equipped[where])].equiped = False
            self.equipped[where] = Item()
        except KeyError:
            print("Can't unequip what does not exists")
        self.recalculate_bonuses()'''

    def unequip_all(self):
        self.equipped = {"head":Item(),
                         "rhand":Item(),
                         "rarm":Item(),
                         "chest":Item(),
                         "larm": Item(),
                         "lhand": Item(),
                         "legs":Item(),
                         "feet": Item()}
        self.recalculate_bonuses()

    def recalculate_bonuses(self):
        for i in self.equipped.keys():
            for j in self.equipped[i].stats_d.keys():
                self.stats[j].bonus_value += self.equipped[i].stats_d[j]
        #print("Recalculated bonuses")

class Attribute:
    def __init__(self, name="", resource=False):
        self.name = name
        self.type = "attribute"
        self.base_value = 0
        self.bonus_value = 0
        self.value = self.base_value + self.bonus_value
        if resource:
            self.current_value = self.value

    def recalculate(self):
        self.value = self.base_value + self.bonus_value

    def recalculate_with(self, x):
        self.base_value = x
        self.value = self.base_value + self.bonus_value

class Player_c:
    def __init__(self, x, y, imagefilename, displaysurf):
        self.x = int(x)
        self.y = int(y)
        self.image = load_png(imagefilename)[0] # load_png("image.png") in init field required
        self.real_x = self.x * 32
        self.real_y = self.y * 32
        self._display_surf = displaysurf
        self.name = None
        self.stats = {"STR": Attribute("Strength"),
                      "CON": Attribute("Constitution"),
                      "DEX": Attribute("Dexterity"),
                      "PER": Attribute("Perception"),
                      "WIS": Attribute("Wisdom"),
                      "INT": Attribute("Intelligence"),
                      "LCK": Attribute("Luck"),

                      "HP": Attribute("Health points", True),
                      "MP": Attribute("Magic points", True),
                      "SP": Attribute("Stamina points", True),

                      "ATK_k": Attribute("Melee attack"),
                      "ATK_r": Attribute("Ranged attack"),
                      "ATK_m": Attribute("Magic attack"),
                      "DEF_kr": Attribute("Melee and ranged defence"),
                      "DEF_m": Attribute("Magic defence"),

                      "HIT_kr": Attribute("Melee and ranged hit chance"),
                      "HIT_m": Attribute("Magic hit chance"),
                      "FIL_kr": Attribute("Melee and ranged fail chance"),
                      "FIL_m": Attribute("Magic fail chance")
                      }
        self.EXP = 0
        self.level_lambda = lambda x: int(x**(1.0/4.0))
        self.level = self.level_lambda(self.EXP)
        self.EQ = EQ(99, self.stats)
        self.recalculate_stats()

    def recalculate_stats(self):
        self.EQ.recalculate_bonuses()
        #Change the way bonus stats are calculated
        for i in self.EQ.bonuses.keys():
            self.stats[i].bonus_value = self.EQ.bonuses[i].value
        for i in self.stats.keys():
            self.stats[i].recalculate()
        self.stats["HP"].recalculate_with((1.5*self.stats["CON"].value+5)+((1.5*self.stats["STR"].value+5)/3))
        self.stats["MP"].recalculate_with(1.5*self.stats["WIS"].value+2)
        self.stats["SP"].recalculate_with(1.5*self.stats["CON"].value+3)
        self.stats["ATK_k"].recalculate_with(1.25*self.stats["STR"].value+self.stats["INT"].value)
        self.stats["ATK_r"].recalculate_with(1.25*self.stats["DEX"].value+self.stats["INT"].value)
        self.stats["ATK_m"].recalculate_with(1.25*self.stats["INT"].value+self.stats["PER"].value)
        self.stats["DEF_kr"].recalculate_with(2*self.stats["CON"].value)
        self.stats["DEF_m"].recalculate_with(2*self.stats["INT"].value)
        self.stats["HIT_kr"].recalculate_with((self.stats["DEX"].value/2) + ((1.5*self.stats["PER"].value)**2/4) + (self.stats["LCK"].value/2))
        if self.stats["HIT_kr"].base_value > 100.0:
            self.stats["HIT_kr"].value = 100.0
        self.stats["HIT_m"].value = 100.0
        self.stats["FIL_kr"].value = 0.0
        self.stats["FIL_m"].recalculate_with(100-((self.stats["INT"].value/2) + ((1.5*self.stats["PER"].value)**2/4) + (self.stats["LCK"].value/2)))
        if self.stats["FIL_m"].base_value < 0.0:
            self.stats["FIL_m"].value = 0.0
        self.level = self.level_lambda(self.EXP)

class NPC:
    def __init__(self, x, y, imagefilename, scriptfilename, displaysurf):
        self.script = scriptfilename
        self.collision = True
        self.event = self.script
        self.x = int(x)
        self.y = int(y)
        self.image = load_png(imagefilename)[0] # load_png("image.png") in init field required
        self.real_x = self.x * 32
        self.real_y = self.y * 32
        self._display_surf = displaysurf
        self.name = None
        self.stats = {"STR": Attribute("Strength"),
                      "CON": Attribute("Constitution"),
                      "DEX": Attribute("Dexterity"),
                      "PER": Attribute("Perception"),
                      "WIS": Attribute("Wisdom"),
                      "INT": Attribute("Intelligence"),
                      "LCK": Attribute("Luck"),

                      "HP": Attribute("Health points", True),
                      "MP": Attribute("Magic points", True),
                      "SP": Attribute("Stamina points", True),

                      "ATK_k": Attribute("Melee attack"),
                      "ATK_r": Attribute("Ranged attack"),
                      "ATK_m": Attribute("Magic attack"),
                      "DEF_kr": Attribute("Melee and ranged defence"),
                      "DEF_m": Attribute("Magic defence"),

                      "HIT_kr": Attribute("Melee and ranged hit chance"),
                      "HIT_m": Attribute("Magic hit chance"),
                      "FIL_kr": Attribute("Melee and ranged fail chance"),
                      "FIL_m": Attribute("Magic fail chance")
                      }
        self.EXP = 0
        self.level_lambda = lambda x: int(x**(1.0/4.0))
        self.level = self.level_lambda(self.EXP)
        self.EQ = EQ(99, self.stats)
        self.recalculate_stats()

    def recalculate_stats(self):
        self.EQ.recalculate_bonuses()
        #Change the way bonus stats are calculated
        for i in self.EQ.bonuses.keys():
            self.stats[i].bonus_value = self.EQ.bonuses[i].value
        for i in self.stats.keys():
            self.stats[i].recalculate()
        self.stats["HP"].recalculate_with((1.5*self.stats["CON"].value+5)+((1.5*self.stats["STR"].value+5)/3))
        self.stats["MP"].recalculate_with(1.5*self.stats["WIS"].value+2)
        self.stats["SP"].recalculate_with(1.5*self.stats["CON"].value+3)
        self.stats["ATK_k"].recalculate_with(1.25*self.stats["STR"].value+self.stats["INT"].value)
        self.stats["ATK_r"].recalculate_with(1.25*self.stats["DEX"].value+self.stats["INT"].value)
        self.stats["ATK_m"].recalculate_with(1.25*self.stats["INT"].value+self.stats["PER"].value)
        self.stats["DEF_kr"].recalculate_with(2*self.stats["CON"].value)
        self.stats["DEF_m"].recalculate_with(2*self.stats["INT"].value)
        self.stats["HIT_kr"].recalculate_with((self.stats["DEX"].value/2) + ((1.5*self.stats["PER"].value)**2/4) + (self.stats["LCK"].value/2))
        if self.stats["HIT_kr"].value > 100.0:
            self.stats["HIT_kr"].value = 100.0
        self.stats["HIT_m"].value = 100.0
        self.stats["FIL_kr"].value = 0.0
        self.stats["FIL_m"].recalculate_with(100-((self.stats["INT"].value/2) + ((1.5*self.stats["PER"].value)**2/4) + (self.stats["LCK"].value/2)))
        if self.stats["FIL_m"].value < 0.0:
            self.stats["FIL_m"].value = 0.0
        self.level = self.level_lambda(self.EXP)

class Mob:
    def __init__(self, imagefilename, scriptfilename):
        self.image = load_png(imagefilename)[0] # load_png("image.png") in init field required
        self.script = scriptfilename
        self.name = None
        self.stats = {"STR": Attribute("Strength"),
                      "CON": Attribute("Constitution"),
                      "DEX": Attribute("Dexterity"),
                      "PER": Attribute("Perception"),
                      "WIS": Attribute("Wisdom"),
                      "INT": Attribute("Intelligence"),
                      "LCK": Attribute("Luck"),

                      "HP": Attribute("Health points", True),
                      "MP": Attribute("Magic points", True),
                      "SP": Attribute("Stamina points", True),

                      "ATK_k": Attribute("Melee attack"),
                      "ATK_r": Attribute("Ranged attack"),
                      "ATK_m": Attribute("Magic attack"),
                      "DEF_kr": Attribute("Melee and ranged defence"),
                      "DEF_m": Attribute("Magic defence"),

                      "HIT_kr": Attribute("Melee and ranged hit chance"),
                      "HIT_m": Attribute("Magic hit chance"),
                      "FIL_kr": Attribute("Melee and ranged fail chance"),
                      "FIL_m": Attribute("Magic fail chance")
                      }
        self.EXP = 0
        self.level_lambda = lambda x: int(x**(1.0/4.0))
        self.level = self.level_lambda(self.EXP)
        self.EQ = EQ(99, self.stats)
        self.recalculate_stats()

    def recalculate_stats(self):
        self.EQ.recalculate_bonuses()
        #Change the way bonus stats are calculated
        for i in self.EQ.bonuses.keys():
            self.stats[i].bonus_value = self.EQ.bonuses[i].value
        for i in self.stats.keys():
            self.stats[i].recalculate()
        self.stats["HP"].recalculate_with((1.5*self.stats["CON"].value+5)+((1.5*self.stats["STR"].value+5)/3))
        self.stats["MP"].recalculate_with(1.5*self.stats["WIS"].value+2)
        self.stats["SP"].recalculate_with(1.5*self.stats["CON"].value+3)
        self.stats["ATK_k"].recalculate_with(1.25*self.stats["STR"].value+self.stats["INT"].value)
        self.stats["ATK_r"].recalculate_with(1.25*self.stats["DEX"].value+self.stats["INT"].value)
        self.stats["ATK_m"].recalculate_with(1.25*self.stats["INT"].value+self.stats["PER"].value)
        self.stats["DEF_kr"].recalculate_with(2*self.stats["CON"].value)
        self.stats["DEF_m"].recalculate_with(2*self.stats["INT"].value)
        self.stats["HIT_kr"].recalculate_with((self.stats["DEX"].value/2) + ((1.5*self.stats["PER"].value)**2/4) + (self.stats["LCK"].value/2))
        if self.stats["HIT_kr"].value > 100.0:
            self.stats["HIT_kr"].value = 100.0
        self.stats["HIT_m"].value = 100.0
        self.stats["FIL_kr"].value = 0.0
        self.stats["FIL_m"].recalculate_with(100-((self.stats["INT"].value/2) + ((1.5*self.stats["PER"].value)**2/4) + (self.stats["LCK"].value/2)))
        if self.stats["FIL_m"].value < 0.0:
            self.stats["FIL_m"].value = 0.0
        self.level = self.level_lambda(self.EXP)