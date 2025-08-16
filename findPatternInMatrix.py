#!/usr/bin/python3
"""
usage: (this works for a 6x6 grid but can be easily adapted for others - just replace the 6 with the actual dimension)
you type 0 and then the number of empty squares until the next selected cell
you select a cell by clicking on it
if you have smth like
[ ] [ ] [ ] [x] [ ] [x]
[ ] [ ] [x] [x] [x] [x]
the code would be 010 110000 (sel, not, sel, not not, sel, sel, sel, sel)
out of convenience you can write 01020000
(0 is whether the card is empty - it's a misnomer in the code (2am))
if you dont like it remove the not and replace the hardcoded 1 in the parse function for generator
happy days

last addendum:
implementing it such that it doesnt wrap around is an exercise for the reader
Dont flatten the array,
    add 2 special symbols, (new line, directly below)
    take the match index of the top one,
    start searching at index below
"""
from __future__ import annotations
import re
import pygame
from pygame.color import Color
from pygame.surface import Surface

pygame.font.init()
pygame.init()

# type aliases that look good
class Vec2(pygame.math.Vector2): ...
class Vec3(pygame.math.Vector3): ...

FPS = 60
WIN_DIMS = (640, 480)
FONT = pygame.font.SysFont("arial", 24)
win = pygame.display.set_mode(WIN_DIMS)
clock = pygame.time.Clock()

run = True

class Tile:
    ENABLED = (255, 0, 0)
    def __init__(self, col_vec: Vec3, i: int, position: tuple | list):
        cbase = col_vec * (((i+1) % 2) if (i // Grid.GRID_SIZE) % 2 else i%2)  # checkerboard colouration
        self.colour = Color(int(cbase.x), int(cbase.y), int(cbase.z), 255)
        self.surf = Surface((Grid.BASE_SIZE, Grid.BASE_SIZE))
        self.position = position
        self.enabled = False # whether it was clicked
    def enable(self):
        self.surf.fill(Tile.ENABLED if self.enabled else self.colour)

class Grid:
    BASE_SIZE = 64
    GRID_SIZE = 6
    def __init__(self, col_vec: Vec3):
        self.mask = [[0 for _ in range(Grid.GRID_SIZE)] for _ in range(Grid.GRID_SIZE)]  # 6[6[0]] array len 6 of an array len 6 of 0
        self.surf = Surface((Grid.BASE_SIZE*Grid.GRID_SIZE, Grid.BASE_SIZE*Grid.GRID_SIZE))
        self.tiles = {}  # for fast referencing when clicked

        # populates the tiles
        for i in range(Grid.GRID_SIZE * Grid.GRID_SIZE):
            self.tiles[(i%Grid.GRID_SIZE, i//Grid.GRID_SIZE)] = Tile(col_vec, i, (i % Grid.GRID_SIZE * Grid.BASE_SIZE, i // Grid.GRID_SIZE * Grid.BASE_SIZE))
    def populate(self):
        for tile in self.tiles.values():
            tile.enable() # i dont care how memory inefficient it is, this is a python proof of concept
            self.surf.blit(tile.surf, tile.position)
    def on_click(self, ms):
        ms = Vec2(*ms) // Grid.BASE_SIZE # this normalises it (snaps to grid)
        self.tiles[ms.x, ms.y].enabled = not self.tiles[ms.x, ms.y].enabled

play_grid = Grid(Vec3(255, 255, 0))
input_label = ""
score = False

def parse():
    if not re.match("^[0-9]+$", input_label):  # ensures only numbers appear
        return
    #""" method one
    reps = re.findall("[2-9]", input_label)
    if not reps:
        return
    input_list = list(input_label)
    for rep in reps: # this replaces n (rep, non 01 number) with 1 repeated n times
        input_list[input_list.index(rep)] = "".join(map(str, ["." for _ in range(int(rep))]))
        # that is used in the search

    # because 1 signifies an empty space (there is 1 space between adjacent cards) i invert the enabled flag
    grid = map(lambda t: int(not t.enabled), play_grid.tiles.values())
    print(re.search("".join(input_list)+"+", "".join(map(str, grid))))
    # i know i can use something like (1){6} in regex for the number of repetitions instead of what im doing
    # and that i should rename the flag to maybe disabled or so but it was 2 in the morning
    # ""

def draw_onto_win():
    play_grid.populate()
    win.blit(play_grid.surf, (0, 0))

    label = Surface((196, 32))
    label.fill((0, 255, 255, 255))
    win.blit(label, (Grid.BASE_SIZE*Grid.GRID_SIZE + 32, 32))
    win.blit(FONT.render(input_label, True, (0, 0, 0, 255)), (Grid.BASE_SIZE*Grid.GRID_SIZE + 32, 32))
    
    pygame.display.update()

def logic():
    # print(list(grid))
    parse()

while run:
    clock.tick(FPS)
    keys  = pygame.key.get_pressed()
    mouse = pygame.mouse.get_pos()
    for event in pygame.event.get():
        match event.type:
            case pygame.QUIT:
                run = False
            case pygame.MOUSEBUTTONDOWN:
                if play_grid.surf.get_rect().collidepoint(*mouse):
                    play_grid.on_click(mouse)
            case pygame.KEYDOWN:
                if event.key == pygame.K_BACKSPACE:
                    input_label = input_label[:-1:]
                else:
                    input_label += event.unicode
    logic()
    draw_onto_win()
