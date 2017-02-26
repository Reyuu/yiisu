import pygame
import os
import pygame.event
import pygame.mixer
import xml.etree.cElementTree as ET
import tkinter as Tk
import tkinter.filedialog
import tkinter.simpledialog
import tkinter.scrolledtext
import tkinter.constants
import random
from pygame.locals import *
from array import array
from base import *

#TODO Load map scripts
#TODO Edit map scripts 
#TOOD Edit scripts of the tiles inside editor -> find coordinates, get file contents of that tilescript, open new tk text edit instance

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
        self.map_script = ""

    def on_init(self):
        pygame.init()
        pygame.mixer.init(frequency=44100)
        pygame.display.set_caption('mapEditor')
        self.switchsound = pygame.mixer.Sound("switch.wav")
        self.beep = pygame.mixer.Sound("beep2")
        self.boop = pygame.mixer.Sound("boop1")
        self.nop = pygame.mixer.Sound("nop")
        self.placeop = pygame.mixer.Sound("placeop")
        self.placeop2 = pygame.mixer.Sound("placeop2")
        self.placeop3 = pygame.mixer.Sound("placeop3")
        self.placeops = [self.placeop, self.placeop2, self.placeop3]
        self.switchsound.set_volume(0.5)
        for i in range(len(self.placeops)):
            self.placeops[i].set_volume(0.05)
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
            filename = tkinter.filedialog.asksaveasfilename(defaultextension='.script', filetypes=[('supported', ('*.script'))], initialdir="./")
            with open(filename, "w") as f:
                f.write("")
            filename = os.path.relpath(filename)
        except ValueError:
            return False
        nx = int((x - (x % 32) -  self.vx) / 32)
        ny = int((y - (y % 32) - self.vy) / 32)
        print(nx, ny)
        self.Playfield.mapp[ny][nx].event = filename
        print("[EVENT] Setup %s at %i, %i" % (filename, nx, ny))

def edit_event(self):
        """
        check if tile has event 
        if not pass
        else edit 
        """
        x, y = pygame.mouse.get_pos()
        nx = int((x - (x % 32) -  self.vx) / 32)
        ny = int((y - (y % 32) - self.vy) / 32)
        print(nx, ny)
        if len(self.Playfield.mapp[ny][nx].event) > 1:
            text_edit = None
            with open(self.Playfield.mapp[ny][nx].event, "r") as f:
                text_edit = MyTextDialog(self.root, f.read(), title="Script at %s, %s" % (nx, ny))
            my_script = text_edit.edited_text
            with open(self.Playfield.mapp[ny][nx].event, "w") as f:
                f.write(my_script)


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
            with open("%s.script" % filename[:-4], "w") as f:
                print(len(self.map_script))
                f.write(self.map_script)
            print("[SUCCESS] Wrote to %s successfully!" % filename)
        except:
            self.nop.play()
            print("[ERROR] Couldn't write!")

    def open(self):
        filename = tkinter.filedialog.askopenfilename(defaultextension='.xml', filetypes=[('supported', ('*.xml'))])
        try:
            e = ET.parse(filename).getroot()
            print("[SUCCESS] Opened %s successfully!" % filename)
        except:
            self.nop.play()
            print("[ERROR] Couldn't open!")
            return None
        playfield = []
        mapp = []
        tileset = e.find("tileset").text
        #print(tileset)
        w, h = int(float(e.find("size").find("x").text)), int(float(e.find("size").find("y").text))
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
        print(filename)
        with open("%s.script" % filename[:-4], "r") as f:
            try:
                self.map_script = f.read()
                print("[SUCCESS] Loaded map scirpt successfully!")
            except:
                print("[ERROR] Couldn't load map script at %s" % filename)
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
                if event.key == K_l:
                    self.edit_event()
                if event.key == K_p:
                    print("Text dialog subroutine")
                    text_edit = MyTextDialog(self.root, self.map_script, title="Map script")
                    self.map_script = text_edit.edited_text
                if event.key == K_r:
                    self.boop.play()
                    if self.SelectedTile.collision:
                        self.SelectedTile.collision = False
                    elif not self.SelectedTile.collision:
                        self.SelectedTile.collision = True
                if event.key == K_s and pygame.key.get_mods() & KMOD_LCTRL:
                    self.beep.play()
                    self.save()
                if event.key == K_o and pygame.key.get_mods() & KMOD_LCTRL:
                    self.beep.play()
                    self.open()
                if event.key == K_n and pygame.key.get_mods() & KMOD_LCTRL:
                    self.beep.play()
                    self.new()
                if event.key == K_e and pygame.key.get_mods() & KMOD_LCTRL:
                    self.beep.play()
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
                    self.boop.play()
                    print("Clicked on tileset")
            if event.type == MOUSEBUTTONDOWN:
                if event.button == 4:
                    self.Tileset.change_pos_rel(0, 32)
                    self.offset += 32
                    random.choice(self.placeops).play()
                if event.button == 5:
                    self.Tileset.change_pos_rel(0, -32)
                    self.offset += -32
                    random.choice(self.placeops).play()

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
                    random.choice(self.placeops).play()
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
                    self.SelectedTile.mutate(self.Playfield.mapp[int(ny/32)][int(nx/32)])
                    random.choice(self.placeops).play()
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
                    if self.Playfield.mapp[y][x].event:
                        s = pygame.Surface((32, 32), pygame.SRCALPHA)
                        s.fill((255, 0, 0, 100))
                        self._display_surf.blit(s, (32*x + self.vx, 32*y + self.vy))
                        pygame.draw.rect(self._display_surf,
                                         (125, 0, 125),
                                         Rect(32*x + self.vx, 32*y + self.vy, 8, 8),
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
