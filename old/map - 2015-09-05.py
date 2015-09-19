import pygame
import os
import pygame.event
import pygame.mixer
import xml.etree.cElementTree as ET
import Tkinter as Tk
import tkFileDialog
import tkSimpleDialog
from pygame.locals import *
from array import array

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
        self.tileset = Tileset(tileset)
        for y in xrange(h):
            wline = []
            for x in xrange(w):
                wline += [Tile()]
            self.mapp += [wline]
        #pprint(self.mapp)

    def process_images(self):
        for y in xrange(len(self.mapp)):
            for x in xrange(len(self.mapp[y])):
                #print(self.mapp[y][x].pos_tileset_x, self.mapp[y][x].pos_tileset_y)
                try:
                    self.mapp[y][x].image.blit(self.tileset.image, (0, 0), (self.mapp[y][x].pos_tileset_x, self.mapp[y][x].pos_tileset_y, 32, 32))
                except TypeError:
                    #self.mapp[y][x].image.blit(self.mapp[y][x].image, (x*32, y*32), (0, 0, 32, 32))
                    pass


class App:
    def __init__(self):
        self._running = True
        self._display_surf = None
        self.size = self.width, self.height = 640, 448
        self.offset = 0
        self.tileset_screen = True
        self.tilesetfile = "tileset.png"
        self.vx = 0
        self.vy = 0
        self.vxmax = self.width/32
        self.vymax = self.height/32
        self.mapsize = (self.vxmax, self.vymax)

    def on_init(self):
        pygame.init()
        pygame.mixer.init()
        pygame.display.set_caption('mapEditor')
        self.switchsound = pygame.mixer.Sound("switch.wav")
        self._display_surf = pygame.display.set_mode(self.size, pygame.HWSURFACE | pygame.DOUBLEBUF)
        pygame.display.set_icon(pygame.Surface((32,32), pygame.SRCALPHA, 32).convert_alpha())
        self._running = True
        #self.Tileset = Tileset(self.tilesetfile)
        self.Playfield = Playfield(self.mapsize[0], self.mapsize[1], self.tilesetfile)
        self.Tileset = self.Playfield.tileset
        self.SelectedTile = SelectedTile(self.width-32, self.height-32)
        #print(type(self.Playfield.mapp[0]))
        pygame.key.set_repeat(500, 50)
        self.root = Tk.Tk()
        self.root.withdraw()
        return True

    def new(self):
        size_d = MyDialog(self.root)
        size = (int(size_d.first), int(size_d.second))
        size_d.destroy()
        self.mapsize = size
        myFormats = [
            ('Windows Bitmap','*.bmp'),
            ('Portable Network Graphics','*.png'),
            ('JPEG / JFIF','*.jpg'),
            ('CompuServer GIF','*.gif'),]
        tileset = tkFileDialog.askopenfilename(defaultextension='.png', filetypes=myFormats, title="Open tileset image")
        self.tilesetfile = tileset
        self.Playfield = Playfield(size[0], size[1], self.tilesetfile)
        self.Tileset = self.Playfield.tileset

    def add_event(self):
        x, y = pygame.mouse.get_pos()
        filename = tkFileDialog.askopenfilename(defaultextension='.py', filetypes=[('supported', ('*.py'))], initialdir="./")
        filename = os.path.relpath(filename)
        nx = (x - (x % 32) -  self.vx) / 32
        ny = (y - (y % 32) - self.vy) / 32
        print(nx, ny)
        self.Playfield.mapp[ny][nx].event = filename
        print("[EVENT] Setup %s at %i, %i" % (filename, nx, ny))

    def save(self):
        #2015-07-30
        filename = tkFileDialog.asksaveasfilename(defaultextension='.xml', filetypes=[('supported', ('*.xml'))])
        mapp = ET.Element("map")
        size = ET.SubElement(mapp, "size")
        size_x = ET.SubElement(size, "x")
        size_y = ET.SubElement(size, "y")
        size_x.text = str(self.mapsize[0])
        size_y.text = str(self.mapsize[1])
        tileset = ET.SubElement(mapp, "tileset")
        tileset.text = str(self.tilesetfile)

        for y in xrange(len(self.Playfield.mapp)):
            for x in xrange(len(self.Playfield.mapp[y])):
                if (self.Playfield.mapp[y][x].pos_tileset_x == None) and (self.Playfield.mapp[y][x].pos_tileset_y == None) and (self.Playfield.mapp[y][x].collision == False):
                    pass
                else:
                    tile = ET.SubElement(mapp, "tile")

                    list_pos_x = ET.SubElement(tile, "list_pos_x")
                    list_pos_y = ET.SubElement(tile, "list_pos_y")

                    pos_tile_x = ET.SubElement(tile, "pos_tile_x")
                    pos_tile_y = ET.SubElement(tile, "pos_tile_y")
                    collision = ET.SubElement(tile, "collision")
                    event = ET.SubElement(tile, "event")

                    list_pos_x.text = str(x)
                    list_pos_y.text = str(y)

                    pos_tile_x.text = str(self.Playfield.mapp[y][x].pos_tileset_x)
                    pos_tile_y.text = str(self.Playfield.mapp[y][x].pos_tileset_y)
                    collision.text = str(self.Playfield.mapp[y][x].collision)
                    event.text = str(self.Playfield.mapp[y][x].event)
        tree = ET.ElementTree(mapp)
        try:
            tree.write(filename)
            print("[SUCCESS] Wrote to %s successfully!" % filename)
        except:
            print("[ERROR] Couldn't write!")

    def open(self):
        filename = tkFileDialog.askopenfilename(defaultextension='.xml', filetypes=[('supported', ('*.xml'))])
        try:
            e = ET.parse(filename).getroot()
            print("[SUCCESS] Opened %s successfully!" % filename)
        except:
            print("[ERROR] Couldn't open!")
            return None
        playfield = []
        mapp = []
        tileset = e.find("tileset").text
        #print(tileset)
        w, h = int(e.find("size").find("x").text), int(e.find("size").find("y").text)
        self.Playfield = Playfield(w, h, tileset)
        counter = 0
        countermax = w * h
        for tile in e.findall("tile"):
            counter += 1
            if counter > countermax:
                break
            print(counter)
            x, y = int(tile.find("list_pos_x").text), int(tile.find("list_pos_y").text)
            #print(tile.find("pos_tile_x").text)
            print(y, x)
            if tile.find("pos_tile_x").text == "None":
                self.Playfield.mapp[y][x].pos_tileset_x = None
            else:
                self.Playfield.mapp[y][x].pos_tileset_x = int(tile.find("pos_tile_x").text)
            if tile.find("pos_tile_y").text == "None":
                self.Playfield.mapp[y][x].pos_tileset_y = None
            else:
                self.Playfield.mapp[y][x].pos_tileset_y = int(tile.find("pos_tile_y").text)


            if tile.find("collision").text == "True":
                self.Playfield.mapp[y][x].collision = True
            else:
                self.Playfield.mapp[y][x].collision = False
            if tile.find("event").text == "None":
                self.Playfield.mapp[y][x].event = None
            else:
                self.Playfield.mapp[y][x].event = tile.find("event").text
        self.Playfield.process_images()
        print("[SUCCESS] Parsed %s successfully!" % filename)

 
    def on_event(self, event):
        if event.type == pygame.QUIT:
            self._running = False
        elif event.type == pygame.KEYDOWN:
            #Tileset screen
            if self.tileset_screen:
                if event.key == K_PAGEUP:
                    self.Tileset.change_pos_rel(0, 32)
                    self.offset += 32
                if event.key == K_PAGEDOWN:
                    self.Tileset.change_pos_rel(0, -32)
                    self.offset += -32
                if event.key == K_TAB:
                    if self.tileset_screen:
                        self.tileset_screen = False
                    elif not self.tileset_screen:
                        self.tileset_screen = True
                    self.switchsound.play()
                    print(self.tileset_screen)
            #Map screen
            elif not self.tileset_screen:
                if event.key == K_TAB:
                    if self.tileset_screen:
                        self.tileset_screen = False
                    elif not self.tileset_screen:
                        self.tileset_screen = True
                    self.switchsound.play()
                    print(self.tileset_screen)
                if event.key == K_UP:
                    self.vy += 32
                    print(self.vy)
                if event.key == K_DOWN:
                    self.vy -= 32
                    print(self.vy)
                if event.key == K_LEFT:
                    self.vx += 32
                    print(self.vx)
                if event.key == K_RIGHT:
                    self.vx -= 32
                    print(self.vx)
                if event.key == K_r:
                    if self.SelectedTile.collision:
                        self.SelectedTile.collision = False
                    elif not self.SelectedTile.collision:
                        self.SelectedTile.collision = True
                if event.key == K_s and pygame.key.get_mods() & KMOD_LCTRL:
                    self.save()
                if event.key == K_o and pygame.key.get_mods() & KMOD_LCTRL:
                    self.open()
                if event.key == K_n and pygame.key.get_mods() & KMOD_LCTRL:
                    self.new()
                if event.key == K_e and pygame.key.get_mods() & KMOD_LCTRL:
                    self.add_event()
        if self.tileset_screen:
            if pygame.mouse.get_pressed()[0]:
                print(pygame.mouse.get_pos())
                if isPointInsideRect(pygame.mouse.get_pos()[0], pygame.mouse.get_pos()[1], self.Tileset.rect):
                    x, y = pygame.mouse.get_pos()
                    #MARCIN LOVE
                    nx = x - (x % 32)
                    ny = y - (y % 32) - self.offset
                    print("Formatted: %i, %i" % (nx, ny))
                    self.SelectedTile.image.fill((255, 255, 255))
                    self.SelectedTile.image.blit(self.Tileset.image, (0, 0), (nx, ny, 32, 32))
                    self.SelectedTile.select_tile(nx, ny)
                    print("Clicked on tileset")
            if event.type == MOUSEBUTTONDOWN:
                if event.button == 4:
                    self.Tileset.change_pos_rel(0, 32)
                    self.offset += 32
                if event.button == 5:
                    self.Tileset.change_pos_rel(0, -32)
                    self.offset += -32

        if not self.tileset_screen:
            if pygame.mouse.get_pressed()[0]:
                #pygame.event.pool()
                print(pygame.mouse.get_pos())
                #paint selected tile
                x, y = pygame.mouse.get_pos()
                #MARCIN LOVE
                nx = x - (x % 32) - self.vx
                ny = y - (y % 32) - self.vy
                print("Formatted: %i, %i" % (nx, ny))
                try:
                    self.SelectedTile.mutate(self.Playfield.mapp[ny/32][nx/32])
                    print(self.SelectedTile.collision)
                except IndexError:
                    pass
            if pygame.mouse.get_pressed()[2]:
                print(pygame.mouse.get_pos())
                #paint selected tile
                x, y = pygame.mouse.get_pos()
                #MARCIN LOVE
                nx = x - (x % 32) - self.vx
                ny = y - (y % 32) - self.vy
                print("Formatted: %i, %i" % (nx, ny))
                try:
                    self.SelectedTile = SelectedTile(self.SelectedTile.pos_x, self.SelectedTile.pos_y)
                    self.SelectedTile.mutate(self.Playfield.mapp[ny/32][nx/32])
                except IndexError:
                    pass
            if event.type == MOUSEBUTTONDOWN:
                if event.button == 4 and pygame.key.get_mods() & KMOD_LSHIFT:
                    self.vx += 32
                elif event.button == 5 and pygame.key.get_mods() & KMOD_LSHIFT:
                    self.vx -= 32
                elif event.button == 4:
                    self.vy += 32
                elif event.button == 5:
                    self.vy -= 32
    def on_loop(self):
        pass

    def on_render(self):
        if self.tileset_screen:
            self._display_surf.fill((255, 255, 255))
            self._display_surf.blit(self.Tileset.image, (self.Tileset.pos_x, self.Tileset.pos_y))
            self._display_surf.blit(self.SelectedTile.image, (self.SelectedTile.pos_x, self.SelectedTile.pos_y))
        if not self.tileset_screen:
            self._display_surf.fill((255, 255, 255))
            for y in xrange(len(self.Playfield.mapp)):
                for x in xrange(len(self.Playfield.mapp[y])):
                    self._display_surf.blit(self.Playfield.mapp[y][x].image, (32*x + self.vx, 32*y + self.vy))
                    #Draw rectangle to show collision
                    if self.Playfield.mapp[y][x].collision:
                        s = pygame.Surface((32, 32), pygame.SRCALPHA)
                        s.fill((255, 0, 0, 100))
                        self._display_surf.blit(s, (32*x + self.vx, 32*y + self.vy))
                        pygame.draw.rect(self._display_surf,
                                         (255, 0, 0),
                                         Rect(32*x + self.vx, 32*y + self.vy, 32, 32),
                                         2)

            self._display_surf.blit(self.SelectedTile.image, (self.SelectedTile.pos_x, self.SelectedTile.pos_y))
            if self.SelectedTile.collision:
                pygame.draw.rect(self._display_surf, (255, 0, 255), Rect(self.SelectedTile.pos_x, self.SelectedTile.pos_y, 32, 32), 1)
            else:
                pygame.draw.rect(self._display_surf, (255, 255, 0), Rect(self.SelectedTile.pos_x, self.SelectedTile.pos_y, 32, 32), 1)
        pygame.display.flip()

    def on_cleanup(self):
        pygame.quit()

    def on_execute(self):
        if not self.on_init():
            self._running = False
        while self._running:
            for event in pygame.event.get():
                self.on_event(event)
            #self.on_event(pygame.event.poll())
            self.on_loop()
            self.on_render()
        self.on_cleanup()

if __name__ == "__main__":
    theApp = App()
    theApp.on_execute()