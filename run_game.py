import math
import random
import sys
import time
import pickle

import pygame
from pygame.locals import *

from Assets.std_sprite_sheet_splitter import SpriteSheet, TextBox, Buttons

# Colours
bgcolour = (60, 60, 60)
map_color = (160, 160, 160)
blue = (25, 117, 174)
red = (211, 47, 47)


# BASIC VARIABLES ARE HERE!!!!!!
FPS = 20
twin_speed = 5
windowWidth = 1260
windowHeight = 810
gridbox = 90
smoothnessfactor = 0.1  # 90/2
movecounter: int

pygame.init()
pygame.mixer.init()
pygame.mixer.music.load('Assets/BG Music.ogg')
pygame.mixer.music.set_volume(0.09)
pygame.mixer.music.play(-1)

fps_clock = pygame.time.Clock()

DisplaySurface = pygame.display.set_mode((windowWidth, windowHeight))        # +80 for game buttons
pygame.display.set_caption('The Two Within You')
DisplaySurface.fill(bgcolour)

game_banner = pygame.image.load('Assets/Game Banner.png')
game_complete_screen = pygame.image.load('Assets/Game Complete.png')
win_text = pygame.Surface((764, 239))
win_text.blit(pygame.image.load('Assets/WinButton.png'), (0, 0))
how_to_play_image = pygame.image.load('Assets/How to play button.png')
play_image = pygame.image.load('Assets/play button.png')

tick_image = SpriteSheet('Assets/Tick.png')
tick_sprite = pygame.sprite.Sprite()
tick_sprite.image = tick_image.get_sprite(0, 0, 151, 116)
tick_sprite.rect = tick_sprite.image.get_rect()

rules_text = SpriteSheet('Assets/RulesText.png')
rules_text_sprite = pygame.sprite.Sprite()
rules_text_sprite.image = rules_text.get_sprite(0, 0, 1146, 761)
rules_text_sprite.rect = rules_text_sprite.image.get_rect()
rules_text_sprite.rect.center = (DisplaySurface.get_rect().centerx - int(gridbox/2), DisplaySurface.get_rect().centery)

twin_sprite_sheet = SpriteSheet('Assets/TwinsSpriteSheet.png')
GTLeft = twin_sprite_sheet.get_sprite(0, 0, gridbox, gridbox)
GTRight = twin_sprite_sheet.get_sprite(gridbox, 0, gridbox, gridbox)
GTDown = twin_sprite_sheet.get_sprite(gridbox*2, 0, gridbox, gridbox)
GTUp = twin_sprite_sheet.get_sprite(gridbox*3, 0, gridbox, gridbox)
ETLeft = twin_sprite_sheet.get_sprite(gridbox*4, 0, gridbox, gridbox)
ETRight = twin_sprite_sheet.get_sprite(gridbox*5, 0, gridbox, gridbox)
ETDown = twin_sprite_sheet.get_sprite(gridbox*6, 0, gridbox, gridbox)
ETUp = twin_sprite_sheet.get_sprite(gridbox*7, 0, gridbox, gridbox)


level_elements_images = SpriteSheet('Assets/LevelElements.png')
flag = level_elements_images.get_sprite(0, 0, gridbox, gridbox)
hole = level_elements_images.get_sprite(gridbox, 0, gridbox, gridbox)
wall = level_elements_images.get_sprite(2*gridbox, 0, gridbox, gridbox)
restart_image = level_elements_images.get_sprite(3*gridbox, 0, gridbox, gridbox)
restart_image_hover = level_elements_images.get_sprite(4*gridbox, 0, gridbox, gridbox)
next_image = level_elements_images.get_sprite(5*gridbox, 0, gridbox, gridbox)
next_image_hover = level_elements_images.get_sprite(6*gridbox, 0, gridbox, gridbox)
previous_image = level_elements_images.get_sprite(7*gridbox, 0, gridbox, gridbox)
previous_image_hover = level_elements_images.get_sprite(8*gridbox, 0, gridbox, gridbox)
help_image = level_elements_images.get_sprite(9*gridbox, 0, gridbox, gridbox)
help_image_hover = level_elements_images.get_sprite(10*gridbox, 0, gridbox, gridbox)


class Twin (pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.evil_twin = [ETLeft, ETRight, ETUp, ETDown]
        self.good_twin = [GTLeft, GTRight, GTUp, GTDown]
        self.current_twin = self.good_twin
        self.sprite_direction = 'right'
        self.sprite = GTRight               # Starting Sprite
        self.image = self.sprite
        self.rect = self.image.get_rect()
        self.coor = (0, 0)

    def update(self):
        self.image = self.sprite
        self.rect.topleft = (level_current.x() + characx, level_current.y() + characy)
        self.coor = (int(characx / gridbox), int(characy / gridbox))

    def switch(self):
        if self.current_twin == self.good_twin:
            self.current_twin = self.evil_twin
        else:                               # aka current twin is evil
            self.current_twin = self.good_twin

    def direction(self, direction):
        self.sprite_direction = direction
        if direction == 'left':
            self.sprite = self.current_twin[0]
        if direction == 'right':
            self.sprite = self.current_twin[1]
        if direction == 'up':
            self.sprite = self.current_twin[2]
        if direction == 'down':
            self.sprite = self.current_twin[3]


class Flag (pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.x = x
        self.y = y
        self.coor = (x, y)
        self.image = flag
        self.rect = self.image.get_rect()
        self.rect.topleft = (level_current.x() + gridbox*x, level_current.y() + gridbox*y)


class Hole (pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.x = x
        self.y = y
        self.coor = (x, y)
        self.image = hole
        self.rect = self.image.get_rect()
        self.rect.topleft = (level_current.x() + gridbox*x, level_current.y() + gridbox*y)


class Wall (pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.x = x
        self.y = y
        self.coor = (x, y)
        self.image = wall
        self.rect = self.image.get_rect()
        self.rect.topleft = (level_current.x() + gridbox*x, level_current.y() + gridbox*y)

class DynamicText (TextBox):
    def update(self):
        self.image = self.font.render(self.caption, True, self.colour)
        self.rect = self.rect

class LevelBase (pygame.sprite.Sprite):
    def __init__(self, width, height):      # Width and height in terms of gridbox
        super().__init__()
        self.image = pygame.Surface((width*gridbox, height*gridbox))
        self.image.fill(map_color)
        self.rect = self.image.get_rect()
        self.rect.center = DisplaySurface.get_rect().center

        self.start_pos = (0, 0)
        self.flag_pos = (0, 0)
        self.hole_pos = (0, 0)
        self.wall_list = [(-1, -1)]
        self.GTtoETswitch = 2
        self.ETtoGTswitch = 1

    def x(self, grid=False):
        if grid:
            return int(self.rect.left/gridbox)
        else:
            return self.rect.left

    def y(self, grid=False):
        if grid:
            return int(self.rect.top/gridbox)
        else:
            return self.rect.top

    def x_limit(self, grid=False):
        if grid:
            return int(self.rect.width/gridbox)
        else:
            return self.rect.width

    def y_limit(self, grid=False):
        if grid:
            return int(self.rect.height/90)
        else:
            return self.rect.height

    def level_elements(self, start_pos, flag_pos, hole_pos, wall_list, GTtoET, ETtoGT):        # Everything in terms of Grid
        self.start_pos = start_pos
        self.flag_pos = flag_pos
        self.hole_pos = hole_pos
        self.wall_list = wall_list
        self.GTtoETswitch = GTtoET
        self.ETtoGTswitch = ETtoGT

    def get_start_coor(self):
        return self.start_pos

    def get_flag_coor(self):
        return self.flag_pos

    def get_hole_coor(self):
        return self.hole_pos


# LEVEL MAPPING IS HERE !!!!!!!!
level0 = LevelBase(5, 3)
level0.level_elements((0, 1), (4, 0), (4, 2), [(1, 0)], 4, 3)

level1 = LevelBase(8, 5)
level1.level_elements((1, 4), (4, 2), (3, 2), [(0, 2), (1, 2), (2, 3), (2, 4), (4, 1), (5, 1), (6, 1), (6, 2), (6, 3), (5, 3), (4, 3)], 7, 4)

level2 = LevelBase(8, 3)
l2_wall_list = [(1, 0), (4, 0), (1, 3), (1, 1), (2, 1), (3, 1), (4, 1), (5, 1), (1, 2), (5, 2)]
level2.level_elements((0, 1), (6, 1), (7, 1), l2_wall_list, 9, 1)

level3 = LevelBase(5, 6)
l3_wall_list = [(0, 0), (1, 0),         (3, 0), (4, 0),

                (0, 2),                         (4, 2),
                (0, 3), (1, 3),         (3, 3), (4, 3),
                (0, 4), (1, 4), (2, 4), (3, 4), (4, 4)]
level3.level_elements((3, 5), (2, 0), (2, 3), l3_wall_list, 3, 3)


level4 = LevelBase(9, 5)
l4_wall_list = [(0, 1)]
for i in range(1, 8):
    for j in range(1, 4):
        l4_wall_list.append((i, j))
l4_wall_list.remove((1, 3))
level4.level_elements((0, 2), (0, 0), (1, 3), l4_wall_list, 5, 2)

level5 = LevelBase(9, 7)
l5_wall_list = []
for i in range(9):
    for j in range(1, 6):
        l5_wall_list.append((i, j))
l5_wall_list.remove((0, 1))
level5.level_elements((4, 6), (8, 0), (0, 1), l5_wall_list, 6, 5)

levels = [level0, level1, level2, level3, level4, level5]
gamestates = ['main menu', 'how_to_play', 'levels', 'completed', 'secret Level']
current_gamestate = gamestates[0]
with open('Assets/save_state.txt', 'rb') as save_file:
    levels_completed = pickle.load(save_file)

level_index = 0
pre_completed = False
for level in levels_completed:
    if level:
        level_index += 1
    else:
        break
    if level_index == 6:
        level_index = 0
        pre_completed = True

std_gamplay = True


# SETTING STUFF UP
dirty_group = pygame.sprite.Group()
button_strip = pygame.Rect(windowWidth - gridbox, 0, gridbox, windowHeight)
all_buttons = []
help_button = Buttons(help_image, button_strip.left, button_strip.top, 20)
restart_button = Buttons(restart_image, button_strip.left, button_strip.top + gridbox, 20)
next_level_button = Buttons(next_image, button_strip.left, restart_button.rect.bottom, 20)

play_button = Buttons(play_image, 0, 0)
play_button.rect.center = (DisplaySurface.get_rect().centerx, DisplaySurface.get_rect().centery + 300)
previous_level_button = Buttons(previous_image, button_strip.left, next_level_button.rect.bottom, 20)

twin_win_sprite = pygame.sprite.Sprite()
twin_win_sprite.image = GTDown
twin_win_sprite.rect = twin_win_sprite.image.get_rect()

def setup():

    global all_buttons, characx, characy, level_current, twin_sprite, flag_sprite, hole_sprite, movecounter, moves_to_switch, next_move_to_switch, all_buttons, all_walls

    level_current = levels[level_index]
    characx = level_current.start_pos[0] * gridbox          # start_pos[0] => x coor
    characy = level_current.start_pos[1] * gridbox          # start_pos[1] => y coor
    twin_sprite = Twin()
    flag_sprite = Flag(level_current.flag_pos[0], level_current.flag_pos[1])
    hole_sprite = Hole(level_current.hole_pos[0], level_current.hole_pos[1])
    movecounter = level_current.GTtoETswitch

    # creating wall border
    all_walls = []
    for i in range(-1, level_current.x_limit(grid=True)+1):
        all_walls.append(Wall(i, -1))
        all_walls.append(Wall(i, level_current.y_limit(grid=True)))
    for i in range(level_current.y_limit(grid=True)):
        all_walls.append(Wall(-1, i))
        all_walls.append(Wall(level_current.x_limit(grid=True), i))
    for wall_pos in level_current.wall_list:
        wall_sprite = Wall(wall_pos[0], wall_pos[1])
        all_walls.append(wall_sprite)

    moves_to_switch = DynamicText(str(movecounter), blue, 0, 0, 60)
    moves_to_switch.rect.center = (windowWidth - int(gridbox/2), windowHeight-gridbox - int(gridbox/2))

    next_move_to_switch = DynamicText(str(level_current.ETtoGTswitch), red, 0, 0, 60)
    next_move_to_switch.rect.center = (windowWidth - int(gridbox/2), windowHeight - int(gridbox/2))

    all_buttons = [restart_button, help_button]
    if level_index + 1 < len(levels):
        all_buttons.append(next_level_button)
    if level_index - 1 >= 0:
        all_buttons.append(previous_level_button)

    dirty_group.add(level_current, all_walls, flag_sprite, hole_sprite, twin_sprite, all_buttons, moves_to_switch, next_move_to_switch)


setup()


def win_check(flag_pos: tuple, charac_pos: tuple):
    if flag_pos == charac_pos:
        return True         # Win
    else:
        return False        # Not Win

def lose_check(hole_pos: tuple, charac_pos: tuple):
    if hole_pos == charac_pos:
        return True
    else:
        return False

def wall_check(wall_list, charac_pos):
    collide = False
    for wall_loc in wall_list:
        if wall_loc.coor == charac_pos:
            return True
    if not collide:
        return False

def next_frame():
    DisplaySurface.fill(bgcolour)
    if std_gamplay:
        pygame.draw.rect(DisplaySurface, map_color, button_strip)
        moves_to_switch.caption = str(movecounter)
        if levels_completed[level_index]:
            dirty_group.add(tick_sprite)
    if current_gamestate == 'main menu':
        game_banner.get_rect().center = DisplaySurface.get_rect().center
        DisplaySurface.blit(game_banner, (50, 0))
    restart_button.mouse_hover(restart_image_hover)
    next_level_button.mouse_hover(next_image_hover)
    help_button.mouse_hover(help_image_hover)
    previous_level_button.mouse_hover(previous_image_hover)
    dirty_group.update()
    dirty_group.draw(DisplaySurface)
    win = win_check(flag_sprite.coor, twin_sprite.coor)      # check if twin on flag
    if win:
        if not levels_completed[level_index]:
            levels_completed[level_index] = True
            with open('Assets/save_state.txt', 'wb') as save_here:
                pickle.dump(levels_completed, save_here)
        win_text.get_rect().center = DisplaySurface.get_rect().center
        DisplaySurface.blit(win_text, (250, 200))
        dirty_group.remove(twin_sprite)
        dirty_group.add(twin_win_sprite)
        twin_win_sprite.rect = flag_sprite.rect
        if not pre_completed and all(levels_completed):
            dirty_group.empty()
            DisplaySurface.fill(bgcolour)
            DisplaySurface.blit(game_complete_screen, (50, 100))
    lose = lose_check(hole_sprite.coor, twin_sprite.coor)
    if lose:
        # dirty_group.add(loser_text)
        dirty_group.remove(twin_sprite)
    pygame.display.update()


# Main Loop
game_on = True
while game_on:

    for event in pygame.event.get():
        if event.type == QUIT:
            pygame.quit()
            sys.exit()

    keys = pygame.key.get_pressed()

    if current_gamestate == 'main menu':
        std_gamplay = False
        dirty_group.empty()
        dirty_group.add(play_button)
        next_frame()
        if play_button.mouse_click():
            current_gamestate = gamestates[2]
            std_gamplay = True

    if twin_sprite in dirty_group:
        if twin_sprite.current_twin == twin_sprite.good_twin:
            if keys[pygame.K_LEFT]:      # Move Twin Left
                twin_sprite.direction('left')
                next_frame()
                if wall_check(all_walls, (twin_sprite.coor[0]-1, twin_sprite.coor[1])):
                    twin_sprite.direction('right')
                else:
                    characx -= 1
                    while characx % gridbox != 0:
                        x_rel = characx % gridbox
                        dx = x_rel
                        x_rel = math.ceil(dx*smoothnessfactor)
                        characx -= x_rel
                        next_frame()
                        time.sleep(0.01)
                    movecounter -= 1

            if keys[pygame.K_RIGHT]:   # Move Twin Right
                twin_sprite.direction('right')
                next_frame()
                # var = wall_check(all_walls, (twin_sprite.coor[0]+1, twin_sprite.coor[1]))
                if wall_check(all_walls, (twin_sprite.coor[0]+1, twin_sprite.coor[1])):
                    twin_sprite.direction('left')
                else:
                    characx += 1
                    while characx % gridbox != 0:
                        x_rel = characx % gridbox
                        dx = gridbox - x_rel
                        x_rel = math.ceil(dx*smoothnessfactor)
                        characx += x_rel
                        next_frame()
                        time.sleep(0.01)
                    movecounter -= 1

            if keys[pygame.K_UP]:     # Move Twin Up
                twin_sprite.direction('up')
                next_frame()
                if wall_check(all_walls, (twin_sprite.coor[0], twin_sprite.coor[1]-1)):
                    twin_sprite.direction('down')
                else:
                    characy -= 1
                    while characy % gridbox != 0:
                        y_rel = characy % gridbox
                        dy = y_rel
                        y_rel = math.ceil(dy*smoothnessfactor)
                        characy -= y_rel
                        next_frame()
                        time.sleep(0.01)
                    movecounter -= 1

            if keys[pygame.K_DOWN]:   # Move Twin Down
                twin_sprite.direction('down')
                if wall_check(all_walls, (twin_sprite.coor[0], twin_sprite.coor[1]+1)):
                    twin_sprite.direction('up')
                else:
                    characy += 1
                    while characy % gridbox != 0:
                        y_rel = characy % gridbox
                        dy = gridbox - y_rel
                        y_rel = math.ceil(dy*smoothnessfactor)
                        characy += y_rel
                        next_frame()
                        time.sleep(0.01)
                    movecounter -= 1

        # Evil Twin Mechanics
        elif twin_sprite.current_twin == twin_sprite.evil_twin:
            preferences = []
            if characx - hole_sprite.x*gridbox >= abs(characy - hole_sprite.y*gridbox):
                preferences.append('left')
            elif hole_sprite.x*gridbox - characx >= abs(characy - hole_sprite.y*gridbox):
                preferences.append('right')
            if characy - hole_sprite.y*gridbox >= abs(characx - hole_sprite.x*gridbox):
                preferences.append('up')
            elif hole_sprite.y * gridbox - characy >= abs(characx - hole_sprite.x * gridbox):
                preferences.append('down')
            prefer = random.choice(preferences)

            if prefer == 'left':       # Move ET left
                twin_sprite.direction('left')
                characx -= 1
                while characx % gridbox != 0:
                    x = characx % gridbox
                    dx = x
                    x = math.ceil(dx * smoothnessfactor)
                    characx -= x
                    next_frame()
                    time.sleep(0.01)
                movecounter -= 1

            elif prefer == 'right':     # Move ET Right
                twin_sprite.direction('right')
                next_frame()
                characx += 1
                while characx % gridbox != 0:
                    x = characx % gridbox
                    dx = gridbox - x
                    x = math.ceil(dx*smoothnessfactor)
                    characx += x
                    next_frame()
                    time.sleep(0.01)
                movecounter -= 1

            elif prefer == 'up':     # Move Twin Up
                twin_sprite.direction('up')
                next_frame()
                characy -= 1
                while characy % gridbox != 0:
                    y = characy % gridbox
                    dy = y
                    y = math.ceil(dy*smoothnessfactor)
                    characy -= y
                    next_frame()
                    time.sleep(0.01)
                movecounter -= 1

            elif prefer == 'down':    # Move Twin Down
                twin_sprite.direction('down')
                characy += 1
                while characy % gridbox != 0:
                    y = characy % gridbox
                    dy = gridbox - y
                    y = math.ceil(dy*smoothnessfactor)
                    characy += y
                    next_frame()
                    time.sleep(0.01)
                movecounter -= 1

        if movecounter == 0:
            next_frame()
            if twin_sprite.current_twin == twin_sprite.good_twin:
                movecounter = level_current.ETtoGTswitch
                moves_to_switch.colour = red
                next_move_to_switch.caption = str(level_current.GTtoETswitch)
                next_move_to_switch.colour = blue
            elif twin_sprite.current_twin == twin_sprite.evil_twin:
                movecounter = level_current.GTtoETswitch
                moves_to_switch.colour = blue
                next_move_to_switch.caption = str(level_current.ETtoGTswitch)
                next_move_to_switch.colour = red
            twin_sprite.switch()
            twin_sprite.direction(twin_sprite.sprite_direction)
            next_frame()

    if play_button in dirty_group and play_button.mouse_click():
        setup()
        dirty_group.remove(play_button)

    if help_button in dirty_group and help_button.mouse_click():
        if rules_text_sprite in dirty_group:
            dirty_group.remove(rules_text_sprite)
            time.sleep(0.2)
        else:
            dirty_group.add(rules_text_sprite)
            time.sleep(0.2)

    if restart_button in dirty_group and restart_button.mouse_click():
        dirty_group.empty()
        setup()

    if next_level_button.mouse_click() or previous_level_button.mouse_click():
        if next_level_button in dirty_group and next_level_button.mouse_click():
            level_index += 1
            time.sleep(0.2)
        if previous_level_button in dirty_group and previous_level_button.mouse_click():
            level_index -= 1
            time.sleep(0.2)

        level_current = levels[level_index]
        moves_to_switch.colour = blue
        next_move_to_switch.caption = str(level_current.ETtoGTswitch)
        next_move_to_switch.colour = red
        dirty_group.add(twin_sprite)
        twin_sprite.direction('right')
        twin_sprite.current_twin = twin_sprite.good_twin
        time.sleep(0.2)

        # Resetup - Does the same thing as setup
        dirty_group.empty()
        setup()

    next_frame()
    fps_clock.tick(FPS)
