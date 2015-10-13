# coding=utf-8
import pygame
import xml.etree.cElementTree as ET
import tkFileDialog
import random
import itertools
from script_lang import *
from pygame.locals import *
from base import *

#TODO Enemy entity
#TODO think bout fighting, stats and levels
#TODO Random encounter
#TODO Enemy scripting
#TODO instead of holding the surfaces of the tiles in the Playfield, get them from the Tileset

#More comming soon
class App:
    def __init__(self):
        self._running = True
        self._display_surf = None
        self.size = self.width, self.height = 640, 480
        self.offset = 0
        self.tileset_screen = True
        self.tilesetfile = "tileset.png"
        self.vx = 0
        self.vy = 0
        self.vxmax = self.width/32
        self.vymax = self.height/32
        self.mapsize = (self.vxmax, self.vymax)
        self.camx = 0
        self.camy = 0
        self.debug = True
        self.Queue = Queue()
        self.state = "game"

    def on_init(self):
        pygame.init()
        pygame.mixer.init()
        pygame.font.init()
        pygame.display.set_caption('mapPlayer')
        self.fontsize = int((((self.width*self.height*16**2)/(640*480)))**(1/2.0))
        self.font = pygame.font.Font("Cabin-Regular.ttf", self.fontsize)
        self._display_surf = pygame.display.set_mode(self.size, pygame.HWSURFACE | pygame.DOUBLEBUF)
        pygame.display.set_icon(pygame.Surface((32,32), pygame.SRCALPHA, 32).convert_alpha())
        self._running = True
        self.Playfield = Playfield(self.mapsize[0], self.mapsize[1], self.tilesetfile)
        self.Tileset = self.Playfield.tileset
        self.SelectedTile = SelectedTile(self.width-32, self.height-32)
        pygame.key.set_repeat(500, 50)
        self.root = Tk.Tk()
        self.root.withdraw()
        self.Player = Player_c(7, 7, "player_test.png", self._display_surf)
        self.init_scripting()
        self.open(dialog=1)
        self.relative_pos = lambda x: x*32 +  self.vx
        self.relative_pos_s = lambda x: x +  self.vx
        self.Camera = Camera(self.vxmax, self.vymax, self.Playfield.maxx, self.Playfield.maxy, self.Player)
        self.Camera.calculate_pos()
        self.col_lambda = lambda x, y: bool(not(self.collision_check_npc(x, y)) and not(self.collision_check(x, y)))
        self.random = random.randint(0, 1000)
        self.ScriptHandler.variables.update({"random_number": self.random})
        return True

    def init_scripting(self):
        def return_it(i):
            return i

        def sum(i, j):
            return i+j

        def rem(i, j):
            return i-j

        def sqroot(i):
            return i**(1.0/2)

        def sqr(i):
            return i**2

        def times(i, j):
            return i*j

        def divide(i, j):
            return i//j

        def print_me(i):
            print(i)

        def change_player_pos(x, y):
            self.Player.x = x
            self.Player.y = y

        def put_npc(x, y, imagefilename, scriptfilename):
            return NPC(x, y, imagefilename, scriptfilename, self._display_surf)

        def process_npc(npc):
            self.Playfield.npcmapp[npc.y][npc.x] = npc

        def change_stat(entity, stat, value):
            print(entity, stat, value)
            entity.stats[stat].base_value = int(value)
            entity.recalculate_stats()

        def add_item_from_EQ(entity, item):
            entity.EQ.add_item(item)

        def get_item_from_EQ(entity, index):
            return entity.EQ.backpack[index]

        def remove_item_from_EQ(entity, item):
            entity.EQ.remove_item(item)

        def get_mob(imagefilename, scriptfilename, chances=(0, 0)):
            return Mob(imagefilename, scriptfilename)

        def get_dict_from_lists(keys, values):
            magic_dict = {}
            for i, j in itertools.izip(keys, values):
                magic_dict.update({i: j})
            return magic_dict

        def get_from_dict(dict, key):
            return dict[key]

        def get_item(name, typ, equipable_where, stats_d):
            return Item(name, typ, equipable_where, stats_d)

        def recover_stat(entity, stat):
            entity.stats[stat].current_value = entity.stats[stat].value



        self.ScriptHandler = ScriptHandler(debug=self.debug)
        self.ScriptHandler.safe_functions.update({"talk": self.talk,
                                                  "open_map": self.open,
                                                  "return": return_it,
                                                  "sum": sum,
                                                  "rem": rem,
                                                  "sqrroot": sqroot,
                                                  "sqr": sqr,
                                                  "times": times,
                                                  "divide": divide,
                                                  "open_script": self.ScriptHandler.get_file,
                                                  "parse_file": self.ScriptHandler.parse_file,
                                                  "print": print_me,
                                                  "change_player_pos": change_player_pos,
                                                  "put_npc": put_npc,
                                                  "process_npc": process_npc,
                                                  "exit": self.on_cleanup,
                                                  "choice": self.choice_talk,
                                                  "change_stat": change_stat,
                                                  "get_mob": get_mob,
                                                  "get_item": get_item,
                                                  "get_item_from_EQ": get_item_from_EQ,
                                                  "remove_item_from_EQ": remove_item_from_EQ,
                                                  "add_item_to_EQ": add_item_from_EQ,
                                                  "get_dict_from_lists": get_dict_from_lists,
                                                  "get_from_dict": get_from_dict,
                                                  "recover": recover_stat})
        self.ScriptHandler.variables.update({"player": self.Player})

    def open(self, filename=None, dialog=0):
        if dialog == 1:
            filename = tkFileDialog.askopenfilename(defaultextension='.xml', filetypes=[('supported', ('*.xml'))])
        else:
            filename = filename
        try:
            e = ET.parse(filename).getroot()
            print("[SUCCESS] Opened %s successfully!" % filename)
        except IOError:
            print("[ERROR] Couldn't read!")
            return None
        playfield = []
        mapp = []
        tileset = e.find("tileset").text
        #print(tileset)
        w, h = int(e.find("size").find("x").text), int(e.find("size").find("y").text)
        self.Playfield = Playfield(w, h, tileset)
        counter = 0
        countermax = w * h
        for play in e.findall("player"):
            x, y = int(play.find("player_x").text), int(play.find("player_y").text)
            self.Player.x = x
            self.Player.y = y
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
            if self.debug:
                print("[FOUND] Tile at %s, %s" % (x, y))
        #self.Playfield.process_images()
        print("[SUCCESS] Parsed %s successfully!" % filename)
        try:
            self.Camera = Camera(self.vxmax, self.vymax, self.Playfield.maxx, self.Playfield.maxy, self.Player)
            self.Camera.calculate_pos()
        except AttributeError, errcode:
            print("[WARNING] Camera cannot initialize because instance of %s is not present" % errcode)
            print("          If you get this at the start of the app don't worry!")
        self.on_render()
        print(filename)
        self.ScriptHandler.get_file(filename.replace(".xml", ".script"))
        self.ScriptHandler.parse_file()

    def collision_check(self, offsetx, offsety):
        side = "either"
        if offsetx > 0:
            side = "right"
        if offsetx < 0:
            side = "left"
        if offsety < 0:
            side = "top"
        if offsety > 0:
            side = "bottom"
        if not(self.Playfield.mapp[self.Player.y+offsety][self.Player.x+offsetx].collision):
            return False
        else:
            if not(self.Playfield.mapp[self.Player.y+offsety][self.Player.x+offsetx].event == None):
                self.ScriptHandler.get_file(self.Playfield.mapp[self.Player.y+offsety][self.Player.x+offsetx].event)
                self.ScriptHandler.parse_file()
            else:
                if self.debug:
                    print("[COLLISION] at %s, %s on %s side" % (self.Player.x+offsetx, self.Player.y+offsety, side))
                return True

    def collision_check_npc(self, offsetx, offsety):
        side = "either"
        if offsetx > 0:
            side = "right"
        if offsetx < 0:
            side = "left"
        if offsety < 0:
            side = "top"
        if offsety > 0:
            side = "bottom"
        try:
            npc_col = self.Playfield.npcmapp[self.Player.y+offsety][self.Player.x+offsetx].collision
        except AttributeError:
            npc_col = False
        if not(npc_col):
            return False
        else:
            if not(self.Playfield.npcmapp[self.Player.y+offsety][self.Player.x+offsetx].event == None):
                self.ScriptHandler.get_file(self.Playfield.npcmapp[self.Player.y+offsety][self.Player.x+offsetx].event)
                self.ScriptHandler.parse_file()
                return True
            else:
                if self.debug:
                    print("[NPC] at %s, %s on %s side" % (self.Player.x+offsetx, self.Player.y+offsety, side))
                return True

    def on_event(self, event):
        moved = False
        if event.type == pygame.QUIT:
            self._running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == K_UP:
                if not(self.Player.y-1 < 0) and self.col_lambda(0, -1):
                    self.Player.y -= 1
                    moved = True
            if event.key == K_DOWN:
                if not(self.Player.y+2 > self.Playfield.maxy) and self.col_lambda(0, 1):
                    self.Player.y += 1
                    moved = True
                else:
                    pass
            if event.key == K_LEFT:
                if not(self.Player.x-1 < 0) and self.col_lambda(-1, 0):
                    self.Player.x -= 1
                    moved = True
            if event.key == K_RIGHT:
                if not(self.Player.x+2 > self.Playfield.maxx) and self.col_lambda(1, 0):
                    self.Player.x += 1
                    moved = True
            if event.key == K_F1:
                self.console()
            if event.key == K_c:
                self.check_stats()
            if event.key == K_i:
                self.check_inventory()
        self.Camera.calculate_pos()
        if moved == True:
            self.random = random.randint(0, 1000)
            self.ScriptHandler.variables.update({"random_number": self.random})
        moved = False
    def on_loop(self):
        pass

    def console(self):
        s = pygame.Surface((self.width, self.fontsize*1.3), pygame.SRCALPHA)
        s.fill((0, 0, 0, 230))
        inputs = []
        myvar = True
        self.lastcommand = []
        offset = 0
        self.Queue.leveltwo += [Resource(s, (0, 0))]
        self.Queue.levelthree += [Resource((self.font.render("".join(inputs), True, (255, 255, 255))), (0, 0))]
        while myvar:
            self.on_render()
            try:
                self.Queue.levelthree.pop()
            except IndexError:
                pass
            pygame.display.flip()
            for j in pygame.event.get():
                mods = pygame.key.get_mods()
                if j.type == pygame.QUIT:
                    import sys
                    self.on_cleanup()
                    sys.exit(1)
                if j.type == pygame.KEYDOWN:
                    if j.key == K_F1:
                        myvar = False
                    if j.key == K_BACKSPACE:
                        try:
                            inputs.pop()
                        except IndexError:
                            pass
                    if j.key == K_UP:
                        try:
                            inputs = self.lastcommand[offset+1]
                            offset += 1
                            print(self.lastcommand)
                        except IndexError:
                            pass
                    if j.key == K_DOWN:
                        try:
                            if not(offset < 0):
                                inputs = self.lastcommand[offset-1]
                                offset -= 1
                            else:
                                inputs = self.lastcommand[offset]
                        except IndexError:
                            pass
                    if j.key == K_RETURN:
                        try:
                            #exec("".join(inputs))
                            self.ScriptHandler.parse_line("".join(inputs))
                            if inputs in self.lastcommand:
                                pass
                            else:
                                self.lastcommand += [inputs]
                            inputs = []
                        except SyntaxError:
                            print("[ERROR] Syntax error")
                    elif j.key >= 32:
                        mods = pygame.key.get_mods()
                        char = str(j.unicode)
                        inputs += char
                    if not(myvar):
                        break
                    #print("".join(inputs))
            if len(inputs) > 0:
                try:
                    self.Queue.levelthree += [Resource((self.font.render("".join(inputs), True, (255, 255, 255))), (0, 0))]
                except pygame.error, err:
                    print("%s" % err)
            else:
                pass
        self.Queue.pop_all()

    def check_stats(self):
        #TODO skills
        self.Player.recalculate_stats()
        keys = self.Player.stats.keys()
        s = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        s.fill((0, 0, 0, 200))
        self.Queue.leveltwo += [Resource(s)]
        scaled = pygame.transform.scale(self.Player.image, (self.Player.image.get_width()*7, self.Player.image.get_height()*7))
        self.Queue.leveltwo += [Resource(scaled, (-25,50))]
        stats_tuple = ("STR", "CON", "DEX", "PER", "WIS", "INT", "LCK", "","HP", "MP", "SP", "", "ATK_k", "ATK_r", "ATK_m", "DEF_kr", "DEF_m", "", "HIT_kr", "HIT_m", "FIL_kr", "FIL_m")
        last_index = 0
        self.Queue.levelthree += [Resource(self.font.render("Attribute:", True, (255, 255, 255)), (self.width/3.0, 25))]
        self.Queue.levelthree += [Resource(self.font.render("Base + bonus = value", True, (255, 255, 255)), (self.width/1.5, 25))]
        for i, j in list(enumerate(stats_tuple)):
            try:
                self.Queue.levelthree += [Resource(self.font.render("%s: " % (self.Player.stats[j].name),
                                                                    True, (255, 255, 255)), (self.width/3.0, i*self.fontsize+50))]
                stats_str = "%i+%i = %i/%i" % (self.Player.stats[j].base_value, self.Player.stats[j].bonus_value, self.Player.stats[j].current_value, self.Player.stats[j].value)
                stats_color = (176, 227, 89)
                if self.Player.stats[j].current_value <= 0:
                    stats_color = (227, 89, 107)
                if self.Player.stats[j].current_value > self.Player.stats[j].value:
                    stats_color = (140, 89, 227)
                self.Queue.levelthree += [Resource(self.font.render(stats_str,
                                                                    True, stats_color), (self.width/1.5, i*self.fontsize+50))]
            except AttributeError:
                self.Queue.levelthree += [Resource(self.font.render("%s: " % (self.Player.stats[j].name),
                                                                    True, (255, 255, 255)), (self.width/3.0, i*self.fontsize+50))]
                stats_str = "%i+%i = %i" % (self.Player.stats[j].base_value, self.Player.stats[j].bonus_value, self.Player.stats[j].value)
                stats_color = (89, 227, 209)
                if i in xrange(0, 8):
                    stats_color = (176, 227, 89)
                if i in xrange(11, 17):
                    stats_color = (140, 89, 227)
                self.Queue.levelthree += [Resource(self.font.render(stats_str,
                                                                    True, stats_color), (self.width/1.5, i*self.fontsize+50))]
            except KeyError:
                pass
            else:
                pass
            last_index = i
        self.Queue.levelthree += [Resource(self.font.render("LEVEL: %i" % self.Player.level, True, (176, 227, 89)), (self.width/2.0, (last_index+1)*self.fontsize+50))]
        myvar = True
        while myvar:
            self.on_render()
            for j in pygame.event.get():
                if j.type == pygame.QUIT:
                    self.on_cleanup()
                if j.type == pygame.KEYDOWN:
                    if j.key == K_c:
                        myvar = False
            if not(myvar):
                break
        self.Queue.pop_all()
        pygame.display.flip()

    def check_inventory(self):
        s = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        s.fill((0, 0, 0, 200))
        offset = 0
        frame = pygame.Surface((self.fontsize, self.fontsize), pygame.SRCALPHA)
        pygame.draw.rect(frame, (255, 0, 0), Rect(0, 0, self.fontsize, self.fontsize), 1)
        #TODO check if Item is equpipped, if true then display something
        #TODO Equipping, unequipping
        def get_state_inventory():
            inventory_surf = pygame.Surface((self.width, self.fontsize*len(self.Player.EQ.backpack)), pygame.SRCALPHA)
            inventory_surf.fill((0, 0, 0, 0))
            for i in xrange(offset, len(self.Player.EQ.backpack)):
                inventory_surf.blit(self.font.render(self.Player.EQ.backpack[i].name, True, (89, 227, 209)), (0, (i*self.fontsize)-(self.fontsize*offset)))
                inventory_surf.blit(self.font.render(self.Player.EQ.backpack[i].equipable_where, True, (209, 227, 89)), (self.width/2.0, (i*self.fontsize)-(self.fontsize*offset)))
                last_index = 0
                if self.Player.EQ.backpack[i] in self.Player.EQ.equipped.values():
                    pygame.draw.rect(inventory_surf, (227, 209, 89), Rect(self.width-self.fontsize, (i*self.fontsize)-(self.fontsize*offset), self.fontsize, self.fontsize))
                for j in self.Player.EQ.backpack[i].stats_d.keys():
                    inventory_surf.blit(self.font.render("%s= %s" % (j, self.Player.EQ.backpack[i].stats_d[j]), True, (255, 255, 255)), (self.width/1.5+last_index*64, (i*self.fontsize)-(self.fontsize*offset)))
                    last_index += 1
            return inventory_surf
        inventory_surf = get_state_inventory()
        myvar = True
        while myvar:
            slice = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
            slice.fill((0, 0, 0, 0))
            slice.blit(inventory_surf, (0, 0), (0, offset*self.fontsize, self.width, self.height))
            self.Queue.leveltwo += [Resource(s)]
            self.Queue.levelthree += [Resource(slice, (0, 0))]
            self.Queue.levelthree += [Resource(frame, (self.width-self.fontsize, 0))]
            self.on_render()
            for j in pygame.event.get():
                if j.type == pygame.QUIT:
                    self.on_cleanup()
                if j.type == pygame.KEYDOWN:
                    if j.key == K_DOWN:
                        if offset+1 in xrange(0, len(self.Player.EQ.backpack)):
                            offset += 1
                        print(offset)
                    if j.key == K_UP:
                        if offset-1 in xrange(0, len(self.Player.EQ.backpack)):
                            offset -= 1
                        print(offset)
                    if j.key == K_RETURN:
                        if self.Player.EQ.backpack[offset] == self.Player.EQ.equipped[self.Player.EQ.backpack[offset].equipable_where]:
                            self.Player.EQ.equip(Item("nothing", "nothing", self.Player.EQ.backpack[offset].equipable_where))
                        else:
                            self.Player.EQ.equip(self.Player.EQ.backpack[offset])
                        self.Player.EQ.bonuses = {}
                        self.Player.EQ.recalculate_bonuses()
                        self.Player.recalculate_stats()
                        inventory_surf = get_state_inventory()
                    if j.key == K_i:
                        myvar = False
            if not(myvar):
                break
            self.Queue.pop_all()
        self.Queue.pop_all()

    def choice_talk(self, lines, choice):
        print(lines, choice)
        s = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        s.fill((0, 0, 0, 200))
        #TODO use font instead of drawn triangle
        #TODO choices -> function that returns states of the chosen numbers
        self.Queue.leveltwo += [Resource(s)]
        for i in xrange(len(lines)):
            self.Queue.levelthree += [Resource(self.font.render(lines[i], True, (255, 255, 255)), (0, i*self.fontsize))]
            myvar = True
            self.Queue.levelthree += [Resource(self.font.render("<", True, (0, 40, 255)), ((self.fontsize/2.3)*len(lines[i]), i*self.fontsize))]
            #self._display_surf.blit(triangle, (len(lines[i])*self.fontsize, i*self.fontsize))
            while myvar:
                self.on_render()
                for j in pygame.event.get():
                    if j.type == pygame.QUIT:
                        self.on_cleanup()
                    if j.type == pygame.KEYDOWN:
                        if j.key == K_SPACE:
                            myvar = False
                if not(myvar):
                    break
            self.Queue.levelthree.pop()
        for i in xrange(len(choice)):
            self.Queue.levelthree += [Resource(self.font.render(choice[i], True, (255, 125, 0)), (0, i*self.fontsize+len(lines)*self.fontsize))]
        myvar = True
        while myvar:
            self.on_render()
            for j in pygame.event.get():
                if j.type == pygame.QUIT:
                    self.on_cleanup()
                if j.type == pygame.KEYDOWN:
                    for number, mkey in list(enumerate([K_1, K_2, K_3, K_4, K_5])):
                        if (j.key == mkey) and (number in xrange(len(choice))):
                            self.Queue.pop_all()
                            return number
            if not(myvar):
                break
        self.Queue.pop_all()
        pygame.display.flip()

    def talk(self, lines):
        #<color=0>
        s = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        s.fill((0, 0, 0, 200))
        #TODO use font instead of drawn triangle
        #TODO choices -> function that returns states of the chosen numbers
        self.Queue.leveltwo += [Resource(s)]
        for i in xrange(len(lines)):
            self.Queue.levelthree += [Resource(self.font.render(lines[i], True, (255, 255, 255)), (0, i*self.fontsize))]
            myvar = True
            self.Queue.levelthree += [Resource(self.font.render("<", True, (0, 40, 255)), ((self.fontsize/2.3)*len(lines[i]), i*self.fontsize))]
            #self._display_surf.blit(triangle, (len(lines[i])*self.fontsize, i*self.fontsize))
            while myvar:
                self.on_render()
                for j in pygame.event.get():
                    if j.type == pygame.QUIT:
                        self.on_cleanup()
                    if j.type == pygame.KEYDOWN:
                        if j.key == K_SPACE:
                            myvar = False
                if not(myvar):
                    break
            self.Queue.levelthree.pop()
        self.Queue.pop_all()
        pygame.display.flip()
        #TODO pages of text
        #TODO feature: colored text

    def on_render(self):
        #print((self.camx - self.Player.x))
        #print(self.camx, self.camy, self.vxmax / 2, self.vymax / 2, self.Player.x, self.Player.y)
        if self.state == "game":
            self._display_surf.fill((0, 0, 0))
            tileset = self.Playfield.tileset.image
            if self.Camera.worldsizey < self.Camera.viewportmaxy:
                rangey = xrange(len(self.Playfield.mapp))
            else:
                rangey = xrange(self.Camera.y, (self.Camera.viewportmaxy+self.Camera.y))

            for y in rangey:
                if self.Camera.worldsizex < self.Camera.viewportmaxx:
                    rangex = xrange(len(self.Playfield.mapp[y]))
                else:
                    rangex = xrange(self.Camera.x, (self.Camera.viewportmaxx+self.Camera.x))

                for x in rangex:
                    pos_x = self.Playfield.mapp[y][x].pos_tileset_x
                    pos_y = self.Playfield.mapp[y][x].pos_tileset_y
                    #print(x, y, self.Camera.x, self.Camera.x, len(self.Playfield.mapp), len(self.Playfield.mapp[y]))
                    self._display_surf.blit(get_from_image(pos_x, pos_y, tileset), (32*x - self.Camera.x*32, 32*y - self.Camera.y*32))
                    if not(self.Playfield.npcmapp[y][x] == None):
                        self._display_surf.blit(self.Playfield.npcmapp[y][x].image, (32*x - self.Camera.x*32, 32*y - self.Camera.y*32))
                    else:
                        pass
                    #Draw rectangle to show collision
                    #debug
                    if self.debug:
                        if self.Playfield.mapp[y][x].collision:
                            s = pygame.Surface((32, 32), pygame.SRCALPHA)
                            s.fill((255, 0, 0, 100))
                            self._display_surf.blit(s, (32*x - self.Camera.x*32, 32*y - self.Camera.y*32))
                            pygame.draw.rect(self._display_surf,
                                             (255, 0, 0),
                                             Rect(32*x - self.Camera.x*32, 32*y - self.Camera.y*32, 32, 32),
                                             2)
                        if not(self.Playfield.npcmapp[y][x] == None):
                            s = pygame.Surface((32, 32), pygame.SRCALPHA)
                            s.fill((0, 0, 255, 100))
                            self._display_surf.blit(s, (32*x - self.Camera.x*32, 32*y - self.Camera.y*32))
                            pygame.draw.rect(self._display_surf,
                                             (0, 0, 255),
                                             Rect(32*x - self.Camera.x*32, 32*y - self.Camera.y*32, 32, 32),
                                             2)

            s = pygame.Surface((32, 32), pygame.SRCALPHA)
            s.fill((0, 0, 0, 155))
            self._display_surf.blit(s, (self.Player.x*32 -  self.Camera.x*32, self.Player.y*32 - self.Camera.y*32))
            self._display_surf.blit(self.Player.image, (self.Player.x*32 -  self.Camera.x*32, self.Player.y*32 - self.Camera.y*32))
            for i in [self.Queue.levelone, self.Queue.leveltwo, self.Queue.levelthree]:
                if i == []:
                    pass
                else:
                    for j in i:
                        self._display_surf.blit(j.image, j.position)
            pygame.display.flip()
        if self.state == "talk":
            for i in [self.Queue.levelone, self.Queue.leveltwo, self.Queue.levelthree]:
                if i == []:
                    pass
                else:
                    for j in i:
                        self._display_surf.blit(j.image, j.position)
            pygame.display.flip()
            pass

    def on_cleanup(self):
        self.Queue.pop_all()
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