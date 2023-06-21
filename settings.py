import pygame

SCREEN_WIDTH = 1280
SCREEN_HEIGHT = 720
FPS = 120

preto = (30,30,30)

#! Scale factor
bg_height = pygame.image.load('graphics/other/bg.png').get_height()
scale_factor = SCREEN_HEIGHT/bg_height

BLOCK_MAP = [
    '666666666666',
    '444444444444',
    '333333333333', 
    '222222222222', 
    '111111111111',
    '            ',
    '            ',
    '            ',
    '            ']

COLOR_LEGEND = {
    '1' : 'blue',
    '2' : 'green',
    '3' : 'red', 
    '4' : 'orange',
    '5' : 'purple',
    '6' : 'bronce',
    '7' : 'grey',
}

GAP_SIZE = 2
BLOCK_HEIGHT = (SCREEN_HEIGHT/(len(BLOCK_MAP))) - GAP_SIZE
BLOCK_WIDTH = (SCREEN_WIDTH/len(BLOCK_MAP[0])) - GAP_SIZE
TOP_OFFSET = SCREEN_HEIGHT/20

UPGRADES = ['speed', 'laser', 'heart', 'size']