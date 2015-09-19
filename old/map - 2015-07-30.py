import pygame
import os
import pygame.event
import xml.etree.cElementTree as ET
from pygame.locals import *
from pprint import pprint


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
        self.tileset = tileset
        for y in xrange(h):
            wline = []
            for x in xrange(w):
                wline += [Tile()]
            self.mapp += [wline]
        pprint(self.mapp)


class App:
    def __init__(self):
        self._running = True
        self._display_surf = None
        self.size = self.width, self.height = 640, 448
        self.offset = 0
        self.switch = True
        self.tilesetfile = "tileset.png"
        self.vx = 0
        self.vy = 0
        self.vxmax = self.width/32
        self.vymax = self.height/32

    def on_init(self):
        pygame.init()
        pygame.display.set_caption('mapEditor')
        self._display_surf = pygame.display.set_mode(self.size, pygame.HWSURFACE | pygame.DOUBLEBUF)
        pygame.display.set_icon(pygame.Surface((32,32), pygame.SRCALPHA, 32).convert_alpha())
        self._running = True
        self.Tileset = Tileset(self.tilesetfile)
        self.Playfield = Playfield(self.vxmax, self.vymax, self.Tileset)
        self.SelectedTile = SelectedTile(self.width-32, self.height-32)
        #print(type(self.Playfield.mapp[0]))
        return True

    def save(self):
        #2015-07-30
        size = ET.Element("size")
        size_x = ET.SubElement(size, "x")
        size_y = ET.SubElement(size, "y")
        size_x.text = str(self.vxmax)
        size_y.text = str(self.vymax)
        tileset = ET.Element("tileset")
        tileset.text = str(self.tilesetfile)
        mapp = ET.Element("map")
        for y in xrange(len(self.Playfield.mapp)):
            for x in xrange(len(self.Playfield.mapp[y])):
                tile = ET.SubElement(mapp, "tile")
                pos_tile_x = ET.SubElement(tile, "pos_tile_x")
                pos_tile_y = ET.SubElement(tile, "pos_tile_y")
                collision = ET.SubElement(tile, "collision")
                event = ET.SubElement(tile, "event")

                pos_tile_x.text = str(self.Playfield.mapp[y][x].pos_tileset_x)
                pos_tile_y.text = str(self.Playfield.mapp[y][x].pos_tileset_y)
                collision.text = str(self.Playfield.mapp[y][x].collision)
                event.text = str(self.Playfield.mapp[y][x].event)
        tree = ET.ElementTree(mapp)
        try:
            tree.write("testmap.xml")
            print("[SUCCES] Wrote to %s successfully!" % "testmap.xml")
        except:
            print("[ERROR] Couldn't write!")
 
    def on_event(self, event):
        if event.type == pygame.QUIT:
            self._running = False
        if event.type == pygame.KEYDOWN:
            #Tileset screen
            if self.switch:
                if event.key == K_PAGEUP:
                    self.Tileset.change_pos_rel(0, 32)
                    self.offset += 32
                    print(K_PAGEUP)
                if event.key == K_PAGEDOWN:
                    self.Tileset.change_pos_rel(0, -32)
                    self.offset += -32
                    print(K_PAGEDOWN)
                if event.key == K_TAB:
                    if self.switch:
                        self.switch = False
                    elif not self.switch:
                        self.switch = True
                    print(self.switch)
            #Map screen
            elif not self.switch:
                if event.key == K_TAB:
                    if self.switch:
                        self.switch = False
                    elif not self.switch:
                        self.switch = True
                    print(self.switch)
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
        if event.type == pygame.MOUSEBUTTONDOWN:
            #Tileset screen
            if self.switch:
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
            elif not self.switch:
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
                elif pygame.mouse.get_pressed()[2]:
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

    def on_loop(self):
        pass

    def on_render(self):
        if self.switch:
            self._display_surf.fill((255, 255, 255))
            self._display_surf.blit(self.Tileset.image, (self.Tileset.pos_x, self.Tileset.pos_y))
            self._display_surf.blit(self.SelectedTile.image, (self.SelectedTile.pos_x, self.SelectedTile.pos_y))
        if not self.switch:
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
        pygame.display.flip()

    def on_cleanup(self):
        pygame.quit()

    def on_execute(self):
        if not self.on_init():
            self._running = False
        while self._running:
            for event in pygame.event.get():
                self.on_event(event)
            self.on_loop()
            self.on_render()
        self.on_cleanup()

if __name__ == "__main__":
    theApp = App()
    theApp.on_execute()