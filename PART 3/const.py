from enum import Enum, auto




BG_COLOR = (255, 255, 255)
WIDTH, HEIGHT = 1280, 720
FPS = 60
PLAYER_VEL = 5


HOST, PORT = "127.0.0.1", 8921


SPRITES_WIDTH = {
    "attack"        : 64,
    "crouch_walk"   : 48,
    "crouch_idle"   : 48,
    "death"         : 64,
    "double_jump"   : 48,
    "fall"          : 48,
    "hit"           : 48,
    "idle"          : 48,
    "jump"          : 48,
    "land"          : 48,
    "roll"          : 48,
    "run"           : 48,
    "wall land"     : 48,
    "wall slide"    : 48
}

SPRITES_SIZES = {
    "attack"        : (64, 29),
    "crouch_idle"   : (48, 21),
    "crouch_walk"   : (48, 21),
    "death"         : (64, 29),
    "double_jump"   : (48, 32),
    "fall"          : (48, 33),
    "hit"           : (48, 29),
    "idle"          : (48, 30),
    "jump"          : (48, 35),
    "land"          : (48, 29),
    "roll"          : (48, 25),
    "run"           : (48, 31),
    "wall land"     : (48, 35),
    "wall slide"    : (48, 35)

}

ANIM_DELAY = {
    "attack"        : 15,
    "crouch_idle"   : 10,
    "crouch_walk"   : 10,
    "death"         : 15,
    "double_jump"   : 6,
    "fall"          : 10,
    "hit"           : 20,
    "idle"          : 20,
    "jump"          : 30,
    "land"          : 10,
    "roll"          : 10,
    "run"           : 20,
    "wall land"     : 10,
    "wall slide"    : 10,
    "attack_cooldown" : 20
}

"""
    ATTACK_CD =  
                len(sprites["attack"]) // we take the number of frames
                * ANIM_DELAY["attack"] // we take the delay between each frame
                * 2 // we double it because the animation is played in the first half of the cd
"""
ATTACK_CD = 157 # len(sprites["attack"]) * ANIM_DELAY["attack"] / 2 + ANIM_DELAY["attack_cooldown"] * 2 

HIT_CD = 80 # ANIM_DELAY["hit"] * len(sprites["hit"])

DEATH_CD = 150 # ANIM_DELAY["death"] * len(sprites["death"])

TERRAIN_SIZES = [64, 96, 60] # 16 * scale, 24 * scale, 15 * scale // scale = 4


class Game_state(Enum):
    Main_menu = auto()
    In_game = auto()
    Pause = auto()
    Game_over = auto()

class Menu_state(Enum):
    Main = auto()
    Singleplayer = auto()
    Multiplayer = auto()

class Config_state(Enum):
    Character = auto()
    Map = auto()


class Multiplayer_state(Enum):
    Welcome = 0
    Map = 1
    Pos = 2
    InGame = 3