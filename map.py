import pygame
import os
import pygame.event
import pygame.mixer
import xml.etree.cElementTree as ET
import tkinter as Tk
import tkinter.filedialog
import tkinter.simpledialog
from pygame.locals import *
from array import array
from base import *

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
        self.player_x = 7
        self.player_y = 7

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
            ('Portable Network Graphics','*.png'),
            ('Windows Bitmap','*.bmp'),
            ('JPEG / JFIF','*.jpg'),
            ('CompuServer GIF','*.gif'),]
        tileset = tkinter.filedialog.askopenfilename(defaultextension='.png', filetypes=myFormats, title="Open tileset image")
        self.tilesetfile = tileset
        self.Playfield = Playfield(size[0], size[1], self.tilesetfile)
        self.Tileset = self.Playfield.tileset

    def add_event(self):
        x, y = pygame.mouse.get_pos()
        try:
            filename = tkinter.filedialog.askopenfilename(defaultextension='.script', filetypes=[('supported', ('*.script'))], initialdir="./")
            filename = os.path.relpath(filename)
        except ValueError:
            return False
        nx = (x - (x % 32) -  self.vx) / 32
        ny = (y - (y % 32) - self.vy) / 32
        print(nx, ny)
        self.Playfield.mapp[ny][nx].event = filename
        print("[EVENT] Setup %s at %i, %i" % (filename, nx, ny))

    def save(self):
        #2015-07-30
        try:
            filename = tkinter.filedialog.asksaveasfilename(defaultextension='.xml', filetypes=[('supported', ('*.xml'))])
        except ValueError:
            return False
        mapp = ET.Element("map")
        size = ET.SubElement(mapp, "size")
        size_x = ET.SubElement(size, "x")
        size_y = ET.SubElement(size, "y")
        size_x.text = str(self.mapsize[0])
        size_y.text = str(self.mapsize[1])
        tileset = ET.SubElement(mapp, "tileset")
        player = ET.SubElement(mapp, "player")
        player_x = ET.SubElement(player, "player_x")
        player_y = ET.SubElement(player, "player_y")
        player_x.text = str(7)
        player_y.text = str(7)
        tileset.text = str(self.tilesetfile)

        for y in range(len(self.Playfield.mapp)):
            for x in range(len(self.Playfield.mapp[y])):
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
        filename = tkinter.filedialog.askopenfilename(defaultextension='.xml', filetypes=[('supported', ('*.xml'))])
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
        #self.Playfield.process_images()
        self.vx = 0
        self.vy = 0
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
                    self.SelectedTile.mutate(self.Playfield.mapp[int(ny/32)][int(nx/32)])
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
            tileset = self.Tileset.image
            for y in range(len(self.Playfield.mapp)):
                for x in range(len(self.Playfield.mapp[y])):
                    pos_x = self.Playfield.mapp[y][x].pos_tileset_x
                    pos_y = self.Playfield.mapp[y][x].pos_tileset_y
                    try:
                        self._display_surf.blit(get_from_image(pos_x, pos_y, tileset), (32*x + self.vx, 32*y + self.vy))
                    except TypeError:
                        self._display_surf.blit(pygame.Surface((32, 32)), (32*x + self.vx, 32*y + self.vy))
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
