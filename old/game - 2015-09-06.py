import pygame
import xml.etree.cElementTree as ET
import tkFileDialog
from pygame.locals import *
from base import *

class Player_c:
    def __init__(self, x, y, image, displaysurf):
        self.x = x
        self.y = y
        self.image = image[0] # load_png("image.png") in init field required
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
        self.offsetmaxy = self.worldsizey -  self.viewportmaxy
        self.offsetminx = 0
        self.offsetminy = 0
        self.calculate_pos()

    def calculate_pos(self):
        self.x = self.playerx - self.viewportmaxx / 2
        self.y = self.playery - self.viewportmaxy / 2
        if self.x > self.offsetmaxx:
            self.x = self.offsetmaxx
        elif self.x < self.offsetminx:
            self.x = self.offsetminx
        if self.y > self.offsetmaxy:
            self.x = self.offsetmaxy
        elif self.y < self.offsetminy:
            self.y = self.offsetminy


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
        print(self.vxmax)
        self.vymax = self.height/32
        self.mapsize = (self.vxmax, self.vymax)
        self.camx = 0
        self.camy = 0

    def on_init(self):
        pygame.init()
        pygame.mixer.init()
        pygame.display.set_caption('mapPlayer')
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
        self.open()
        self.Player = Player_c(7, 7, load_png("player_test.png"), self._display_surf)
        self.relative_pos = lambda x: x*32 +  self.vx
        self.relative_pos_s = lambda x: x +  self.vx
        self.camx = self.Player.x - self.vxmax / 2
        self.camy = self.Player.y - self.vymax / 2
        self.Camera = Camera(self.vxmax, self.vymax, self.Playfield.maxx, self.Playfield.maxy, self.Player)
        return True

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
            #print(counter)
            x, y = int(tile.find("list_pos_x").text), int(tile.find("list_pos_y").text)
            #print(y, x)
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
            print("[FOUND] Tile at %s, %s" % (x, y))
        self.Playfield.process_images()
        print("[SUCCESS] Parsed %s successfully!" % filename)


    def on_event(self, event):
        if event.type == pygame.QUIT:
            self._running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == K_UP:
                if not(self.Player.y-1 < 0):
                    self.Player.y -= 1
                else:
                    pass
            if event.key == K_DOWN:
                if not(self.Player.y+2 > self.Playfield.maxy):
                    self.Player.y += 1
                else:
                    pass
            if event.key == K_LEFT:
                if not(self.Player.x-1 < 0):
                    self.Player.x -= 1
                    print(self.Player.x)
                else:
                    pass
            if event.key == K_RIGHT:
                if not(self.Player.x+2 > self.Playfield.maxx):
                    self.Player.x += 1
                    print(self.Player.x)
                else:
                    pass
            if event.key == K_c:
                self.Player.x -= 1
        if event.type == MOUSEBUTTONDOWN:
            if event.button == 4 and pygame.key.get_mods() & KMOD_LSHIFT:
                self.vx += 32
            elif event.button == 5 and pygame.key.get_mods() & KMOD_LSHIFT:
                self.vx -= 32
            elif event.button == 4:
                self.vy += 32
            elif event.button == 5:
                self.vy -= 32
        print(self.camx, self.camy, self.vxmax / 2, self.vymax / 2, self.Player.x, self.Player.y)
    def on_loop(self):
        pass

    def on_render(self):
        self.camx = self.Player.x - self.vxmax / 2
        self.camy = self.Player.y - self.vymax / 2
        #print((self.camx - self.Player.x))
        #print(self.camx, self.camy, self.vxmax / 2, self.vymax / 2, self.Player.x, self.Player.y)
        self._display_surf.fill((255, 255, 255))
        for y in xrange(len(self.Playfield.mapp)):
            for x in xrange(len(self.Playfield.mapp[y])):
                self._display_surf.blit(self.Playfield.mapp[y][x].image, (32*x - self.camx*32, 32*y - self.camy*32))
                #Draw rectangle to show collision
                #debug
                '''if self.Playfield.mapp[y][x].collision:
                    s = pygame.Surface((32, 32), pygame.SRCALPHA)
                    s.fill((255, 0, 0, 100))
                    self._display_surf.blit(s, (32*x + self.vx, 32*y + self.vy))
                    pygame.draw.rect(self._display_surf,
                                     (255, 0, 0),
                                     Rect(32*x + self.vx, 32*y + self.vy, 32, 32),
                                     2)'''
        self._display_surf.blit(self.Player.image, (self.Player.x*32 -  self.camx*32, self.Player.y*32 - self.camy*32))
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