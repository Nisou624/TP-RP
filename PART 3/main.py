from os import listdir
from os.path import isfile, join
import pygame
from Sprite import Sprite
from const import *
import socket
import json
from _thread import *

pygame.init()

pygame.display.set_caption("VS")

client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)


selected_world = -1

window = pygame.display.set_mode((WIDTH, HEIGHT))

font = pygame.font.SysFont("arialblack", 40)


maps = [pygame.image.load("PART 3/assets/maps/plain.png"), pygame.image.load("PART 3/assets/maps/oak_wood.png"), pygame.image.load("PART 3/assets/maps/stringstar.png")]

player_1 = None
player_2 = None

whoami = 0

def draw_text(text, font, text_col, x ,y):
    img = font.render(text, True, text_col)
    window.blit(img, (x, y))


config_state = Config_state.Map
global_state = Game_state.Main_menu
menu_state = Menu_state.Main
m_state = None
is_connected = False


def read_pos(str):
    str = str.split(",")
    return int(str[0]), int(str[1])

class Button:
    def __init__(self, text, x, y, color):
        self.text = text
        self.x = x
        self.y = y
        self.color = color
        self.width = 200
        self.height = 100

    def draw(self, win):
        pygame.draw.rect(win, self.color, (self.x, self.y, self.width, self.height))
        font = pygame.font.SysFont("comicsans", 40)
        text = font.render(self.text, 1, (255,255,255))
        win.blit(text, (self.x + round(self.width/2) - round(text.get_width()/2), self.y + round(self.height/2) - round(text.get_height()/2)))

    def click(self, pos):
        x1 = pos[0]
        y1 = pos[1]
        if self.x <= x1 <= self.x + self.width and self.y <= y1 <= self.y + self.height:
            return True
        else:
            return False



def flip(sprites):
    return [pygame.transform.flip(sprite, True, False) for sprite in sprites]

def load_sprite_sheets(dir1, sprite_sizes, scale_factor=3, direction=True):
    path = join("PART 3/assets", dir1)
    images = [f for f in listdir(path) if isfile(join(path, f))]
    
    all_sprites = {}

    for image in images:
        sprite_sheets = pygame.image.load(join(path, image)).convert_alpha()
        img_name = image.replace(".png", "")

        sprites = []
        for i in range(sprite_sheets.get_width() // sprite_sizes[img_name][0]):
            surface = pygame.Surface(sprite_sizes[img_name], pygame.SRCALPHA, 32)
            rect = pygame.Rect(i * sprite_sizes[img_name][0], 0, sprite_sizes[img_name][0], sprite_sizes[img_name][1])
            surface.blit(sprite_sheets, (0, 0), rect)
            scaled_surface = pygame.transform.scale(surface, (sprite_sizes[img_name][0] * scale_factor, sprite_sizes[img_name][1] * scale_factor))
            sprites.append(scaled_surface)
        
        if direction:
            all_sprites[image.replace(".png", "") + "_right"] = sprites
            all_sprites[image.replace(".png", "") + "_left"] = [pygame.transform.flip(sprite, True, False) for sprite in sprites]
        else:
            all_sprites[image.replace(".png", "")] = sprites

    return all_sprites



class Player(pygame.sprite.Sprite):
    COLOR = (255, 0, 0)
    PLAYER_VEL = 5
    GRAVITY = 1

    SPRITES = load_sprite_sheets("Player", SPRITES_SIZES)
    ANIMATION_DELAY = 10

    def __init__(self, x, y, width, height):
        super().__init__()
        self.rect = pygame.Rect(x, y, width, height)
        self.x_vel = 0
        self.y_vel = 0
        self.mask = None
        self.direction = "left"
        self.animation_count = 0
        self.fall_count = 0
        self.jump_count = 0
        self.hit_count = 0
        self.got_hit = False
        self.attacking = False
        self.attack_cooldown = 0
        self.health = 100
        self.alive = True
        self.death_anim = False

    def jump(self):
        #print("Before jump - Player position:", self.rect.x, self.rect.y)
        #print("Before jump - Player y_vel:", self.y_vel, "jump counter:", self.jump_count)

        self.y_vel = -self.GRAVITY * 5
        self.animation_count = 0
        self.jump_count += 1
        if self.jump_count == 1:
            self.fall_count = 0

        #print("After jump - Player position:", self.rect.x, self.rect.y)
        #print("After jump - Player y_vel:", self.y_vel, "jump counter:", self.jump_count)

    def move(self, dx, dy):
        self.rect.x += dx
        self.rect.y += dy

    def move_left(self, vel):
        self.x_vel = -vel
        if self.direction != "left":
            self.direction = 'left'
            self.animation_count = 0

    def move_right(self, vel):
        self.x_vel = vel
        if self.direction != "right":
            self.direction = 'right'
            self.animation_count = 0

    def loop(self, fps):
        self.y_vel += min(1, (self.fall_count / fps) * self.GRAVITY)
        self.move(self.x_vel, self.y_vel)

        self.fall_count += 1
        self.update()

    def update(self):
        sprite_sheet = "death"
        if self.alive:
            sprite_sheet = "idle"
            if self.y_vel < 0:
                if self.jump_count == 1:
                    sprite_sheet = "jump"
                elif self.jump_count == 2:
                    sprite_sheet = "double_jump"
            elif self.y_vel >  self.GRAVITY * 2:
                sprite_sheet = "fall"
            elif self.x_vel != 0:
                sprite_sheet = "run"
            #elif 0 < self.hit_count < self.attack_cooldown / 2:
            #    self.attacking = True
            #    sprite_sheet = "attack"
            #    self.hit_count += 1
            #elif self.hit_count >= self.attack_cooldown / 2:
            #    self.attacking = False
            #    self.hit_count = 0

            if self.attack_cooldown > 0:
                if self.attack_cooldown > ANIM_DELAY["attack"] * 7:
                    sprite_sheet = "attack"
                    #self.attacking = True
                #else:
                #    self.animation_count = 0
                self.attack_cooldown -= 1
            else:
                self.attacking = False

            if self.hit_count > 0:
                sprite_sheet = "hit"
                self.hit_count -= 1

            self.reduce_health()
        
        else:
            if not self.death_anim:
                self.death_anim = True
                self.animation_count = 0

        sprite_sheet_name = sprite_sheet + "_" + self.direction
        sprites = self.SPRITES[sprite_sheet_name]
        if sprite_sheet == "death" and (self.animation_count // ANIM_DELAY[sprite_sheet]) >= len(sprites):
            sprite_index = len(sprites) - 1  # Stay on the last frame
        else:
            sprite_index = (self.animation_count // ANIM_DELAY[sprite_sheet]) % len(sprites)
            self.animation_count += 1  # Only increment if not on the last frame of death animation
        self.sprite = sprites[sprite_index]
        self.update_mask()

    
    def update_mask(self):
        self.rect = self.sprite.get_rect(topleft=(self.rect.x, self.rect.y))
        self.mask = pygame.mask.from_surface(self.sprite)

    def draw(self, win):
        win.blit(self.sprite, (self.rect.x, self.rect.y))

    def attack(self):
        self.attack_cooldown = ATTACK_CD

    def landed(self):
        self.fall_count = 0
        self.y_vel = 0
        self.jump_count = 0

    def hit_head(self):
        self.count = 0
        self.y_vel *= -1

    def reduce_health(self, damage=10):
        if self.got_hit and self.alive:
            self.health -= damage
            self.hit_count = 80
            self.animation_count = 0
            
            self.got_hit = False
            print("health reduced, health now is :", self.health)
            #print("health:", self.health)
            if self.health <= 0:
                self.alive = False
        

    def handle_vertical_collision(self, objects):
        if self.y_vel < 0:
            return None
        collided_objects = []
        for object in objects:
            if pygame.sprite.collide_mask(self, object):
                if self.y_vel > 0:
                    self.rect.bottom = object.rect.top
                    self.landed()

                elif self.y_vel < 0:
                    self.rect.top = object.rect.bottom
                    self.hit_head()

                collided_objects.append(object)
        return collided_objects
    
    def collide(self, objects, dx):
        self.move(dx, 0)
        self.update()
        collided_object = None
        for object in objects:
            if pygame.sprite.collide_mask(self, object):
                if isinstance(object, Player):
                    if self.attacking == True:
                        if not object.hit_count > 0:
                            object.got_hit = True
                            #object.reduce_health()
                        #print("ennemy health:", object.health)
                collided_object = object
                break
        self.move(-dx, 0)
        self.update()
        return collided_object


    def listen(self, objects, controls=True):

        
        collide_left = self.collide(objects, -PLAYER_VEL * 2) #self.collide([obj for obj in objects if obj.name != "terrain"], -PLAYER_VEL * 2)
        collide_right = self.collide(objects, PLAYER_VEL * 2)


        if controls:
            keys = pygame.key.get_pressed()
            if keys[pygame.K_LEFT] and not collide_left:
                self.move_left(self.PLAYER_VEL)
            elif keys[pygame.K_RIGHT] and not collide_right:
                self.move_right(self.PLAYER_VEL)
            elif keys[pygame.K_UP]:
                if not self.attacking:
                    self.attacking = True
                    self.animation_count = 0
                    self.attack()
            else:
                self.x_vel = 0

        self.handle_vertical_collision([object for object in objects if not isinstance(object, Player)])

def listen_online(self, objects, has_controls, controls=None):

    collide_left = self.collide(objects, -PLAYER_VEL * 2) #self.collide([obj for obj in objects if obj.name != "terrain"], -PLAYER_VEL * 2)
    collide_right = self.collide(objects, PLAYER_VEL * 2)
    
    if has_controls:
        if controls:
            if controls[pygame.K_LEFT] and not collide_left:
                self.move_left(self.PLAYER_VEL)
            elif controls[pygame.K_RIGHT] and not collide_right:
                self.move_right(self.PLAYER_VEL)
            elif controls[pygame.K_UP]:
                if not self.attacking:
                    self.attacking = True
                    self.animation_count = 0
                    self.attack()
            else:
                self.x_vel = 0
        else:
            keys = pygame.key.get_pressed()
            try:
                client.send(json.dumps(keys).encode("utf-8"))
            except:
                print("error sending controls")
            if keys[pygame.K_LEFT] and not collide_left:
                self.move_left(self.PLAYER_VEL)
            elif keys[pygame.K_RIGHT] and not collide_right:
                self.move_right(self.PLAYER_VEL)
            elif keys[pygame.K_UP]:
                if not self.attacking:
                    self.attacking = True
                    self.animation_count = 0
                    self.attack()
            else:
                self.x_vel = 0

    self.handle_vertical_collision([object for object in objects if not isinstance(object, Player)])


def game_online(p1, p2):
    terrain = Block(0, HEIGHT - TERRAIN_SIZES[selected_world], "terrain", TERRAIN_SIZES[selected_world])
    window.blit(pygame.transform.scale_by(maps[selected_world], 4), (0, 0))
    p1.loop(FPS)
    p1.draw(window)
    p2.loop(FPS)
    p2.draw(window)
    if whoami == 1:
        p1.listen_online([terrain, p2], True)
        try:
            controls = client.recv(2048).decode("utf-8")
            controls = json.loads(controls)
        except:
            controls = None
            print("error receiving controls")
        p2.listen_online([terrain, p1], False, None) # None should be the packet received from the socket
    else:
        p2.listen_online([terrain, p1], False, None)
        try:
            controls = client.recv(2048).decode("utf-8")
            controls = json.loads(controls)
        except:
            controls = None
            print("error receiving controls")
        p1.listen_online([terrain, p2], True, controls)

class Object(pygame.sprite.Sprite):
    def __init__(self, x, y, width, height, name=""):
        super().__init__()
        self.name = name
        self.rect = pygame.Rect(x, y, width, height)
        self.image = pygame.Surface((width, height), pygame.SRCALPHA)
        self.width = width
        self.height = height
        self.name = name

    def draw(self, win):
        win.blit(self.image, (self.rect.x, self.rect.y))


class Block(Object):
    def __init__(self, x, y, name, height, width=WIDTH):
        super().__init__(x, y, width, height, name)
        self.image = pygame.Surface((width, height))  # Create an image for the block
        self.image.fill((255, 255, 255))  # Fill the image with a color
        self.image.set_alpha(0)  # Set alpha value to 0 for transparency
        self.mask = pygame.mask.from_surface(self.image)  # Create a mask from the image

sp = Button("Singleplayer", WIDTH/2 - 200 / 2, 100, (52,78,91))
mp = Button("Multiplayer", WIDTH/2 - 200 / 2, 250, (52,78,91))
quit = Button("Quit", WIDTH/2 - 200 / 2, 400, (52,78,91))
confirm = Button("Confirm", WIDTH / 2 - 200 / 2, HEIGHT - 200, (52,78,91))

def get_background():
    pass

def listen_server(arg1, arg2):
    print("thread started")
    global m_state, player_2, player_1
    while True:
        print(m_state)
        try:
            message = client.recv(2048).decode("utf-8")
            print("received first message: ", message)
            if not message:
                break
            if m_state != Multiplayer_state.InGame:
                #print("received first message: ", message)
                mode = message.split(":")[0].lower().strip()
                if mode == "welcome":
                    print("in the welcome state")
                    m_state = Multiplayer_state.Welcome
                    client.send(str(m_state).encode("utf-8"))
                elif mode == "map":
                    m_state = Multiplayer_state.Map
                    print("in the map state")
                    whoami = 1
                elif mode == "pos":
                    if m_state == None:
                        whoami = 2
                        print(whoami)
                    m_state = Multiplayer_state.Pos
                    print("in the pos state")
                    if message.split(":")[1].lower().lstrip() == "pos " + str(whoami):
                        player_1 = Player(read_pos(message.split(":")[2])[0], read_pos(message.split(":")[2][1]), 96, 96)
                        print("received my positions")
                    else:
                        player_2 = Player(read_pos(message.split(":")[2])[0], read_pos(message.split(":")[2][1]), 96, 96)
                        print("received the other one positions")
                        client.send("received".encode("utf-8"))
                elif mode == "Start":
                    m_state = Multiplayer_state.InGame
            else:
                mode = message.split(":")[0].lower().strip()
                if mode == "state":
                    print(mode)
                elif mode == "move":
                    c2 = json.loads(message.split(":")[1])
        except Exception as e:
            print(f"Error receiving message: {e}")
            break





def multi():
    if m_state == None:
        draw_text("Waiting for connection", font, (0, 0, 0), WIDTH / 2 - 200, HEIGHT / 2 - 200)
    elif m_state == Multiplayer_state.Map:
        draw_selection()
        if selected_world != -1:
            client.send(f"map : {selected_world}".encode("utf-8"))
    elif m_state == Multiplayer_state.Pos:
        if player_2 == None:
            draw_text("Waiting for Player 2", font, (0, 0, 0), WIDTH /2 - 200, HEIGHT / 2 - 200)
        else:
            if not player_1 == None:
                client.send("received".encode("utf-8"))
    elif m_state == Multiplayer_state.InGame:
        game_online(player_1, player_2)
        

def draw_menu():
    global menu_state, is_connected
    if menu_state == Menu_state.Main:
        sp.draw(window)
        mp.draw(window)
        quit.draw(window)
    elif menu_state == Menu_state.Singleplayer:
        draw_selection()
    elif menu_state == Menu_state.Multiplayer:
        try:
            if not is_connected:
                client.connect((HOST, PORT))
                start_new_thread(listen_server, (None, None))
                is_connected = True
            multi()
        except Exception as e:
            print(f"Error connecting to the server: {e}")
            exit()

def mouse_hovering(x, y, width, height):
    pos = pygame.mouse.get_pos()
    if x <= pos[0] <= x + width and y <= pos[1] <= y + height:
        return True
    else:
        return False

def draw_selection():
    global global_state, selected_world, config_state, menu_state
    chosen_world = -1
    if config_state == Config_state.Map:
        confirm.draw(window)
        if pygame.mouse.get_pressed()[0]:
            if confirm.click(pygame.mouse.get_pos()):
                print(f"selected world: {selected_world}")
                print("confirmed")
                print(config_state)
                if selected_world != -1:
                    config_state = Config_state.Character
                    
        worlds = [Sprite('PART 3/assets/worlds/earth.png', 180), Sprite('PART 3/assets/worlds/oak_wood.png', 180), Sprite('PART 3/assets/worlds/stringstar.png', 180)]
        x_padding = WIDTH / len(worlds) - 100
        for i in range(len(worlds)):
            if mouse_hovering(100 + (100 + x_padding) * i, HEIGHT / 2 - 50, 100, 100):
                worlds[i].update()
                selected_world = i
            window.blit(worlds[i].animate(0, worlds[i].image.get_width() / 100), (100 + (100 + x_padding) * i, HEIGHT / 2 - 50))
        
    elif config_state == Config_state.Character and menu_state == Menu_state.Singleplayer:
        global_state = Game_state.In_game
        
def game(p1, p2):
    terrain = Block(0, HEIGHT - TERRAIN_SIZES[selected_world], "terrain", TERRAIN_SIZES[selected_world])
    wall = Block(250, HEIGHT - 100 - TERRAIN_SIZES[selected_world], "wall", 100, 100)
    window.blit(pygame.transform.scale_by(maps[selected_world], 4), (0, 0))
    pygame.draw.rect(window, (255,0,0), p1.rect, 2)
    p1.loop(FPS)
    p1.draw(window)
    p2.loop(FPS)
    p2.draw(window)
    p1.listen([terrain, p2])#, wall
    p2.listen([terrain, p1], False)
    #if not p2.alive:
    #    print("player died")
    #if pygame.sprite.collide_mask(player, p2):
    #    print("p2 health:", p2.health)


def main(window):
    global global_state, menu_state
    player = Player(100, 528 , 96, 96)
    p2 = Player(250, HEIGHT - 96 - TERRAIN_SIZES[selected_world], 96, 96)
    clock = pygame.time.Clock()

    run = True
    while run:
        clock.tick(FPS)
        window.fill(BG_COLOR)
        
        if global_state == Game_state.Main_menu:
            draw_menu()
        elif global_state == Game_state.In_game:
            if menu_state == Menu_state.Singleplayer:
                game(player, p2)
            elif menu_state == Menu_state.Multiplayer:
                game(player_1, player_2)

        if pygame.mouse.get_pressed()[0]:
                pos = pygame.mouse.get_pos()
                if global_state == Game_state.Main_menu:
                    if menu_state == Menu_state.Main:
                        if sp.click(pos):
                            menu_state = Menu_state.Singleplayer
                        if mp.click(pos):
                            menu_state = Menu_state.Multiplayer
                        if quit.click(pos):
                            run = False
                            break
                    
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
                break

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE and player.jump_count < 2:
                    player.jump()

        pygame.display.update()

    pygame.quit()
    quit()


if __name__ == "__main__":
    main(window)