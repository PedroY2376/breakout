import pygame
from settings import *
from os import walk

class Surface_maker:
    def __init__(self):
        #! Import all the graphics
        for index, info in enumerate(walk('graphics/blocks')):
            if index == 0:
                self.assets = {color:{} for color in info[1]}
            else:
                for image_name in info[2]:
                    color_type = list(self.assets.keys())[index - 1]
                    full_path = f'graphics/blocks/{color_type}/{image_name}'
                    surf = pygame.image.load(full_path).convert_alpha()
                    self.assets[color_type][image_name.split('.')[0]] = surf    
    
    def get_surf(self, block_type, size):
        #! Create one surface with the graphics with any size
        image = pygame.Surface(size)
        image.set_colorkey((0,0,0))
        sides = self.assets[block_type]
        
        #? 4 corners
        image.blit(sides['topleft'], (0,0))
        image.blit(sides['topright'], (size[0] - sides['topright'].get_width(),0))
        image.blit(sides['bottomleft'], (0,size[1] - sides['bottomleft'].get_height()))
        image.blit(sides['bottomright'], (size[0] - sides['bottomright'].get_width(), size[1] - sides['bottomright'].get_height()))
        
        #? 4 sides
        #? top
        top_width = size[0] - (sides['topleft'].get_width() + sides['topright'].get_width())
        scale_top_surf = pygame.transform.scale(sides['top'], (top_width, sides['top'].get_height()))
        image.blit(scale_top_surf, (sides['topleft'].get_width(),0))
        
        #? bottom
        bottom_width = size[0] - (sides['bottomleft'].get_width() + sides['bottomright'].get_width())
        scale_bottom_surf = pygame.transform.scale(sides['bottom'], (bottom_width, sides['bottom'].get_height()))
        image.blit(scale_bottom_surf, (sides['bottomleft'].get_width(), size[1] - sides['bottomleft'].get_height()))
        
        #? left
        left_height = size[1] - (sides['topleft'].get_height() + sides['bottomleft'].get_height())
        scale_left_surf = pygame.transform.scale(sides['left'], (sides['left'].get_width(), left_height))
        image.blit(scale_left_surf, (0,sides['topleft'].get_height()))
        
        #? right
        right_height = size[1] - (sides['topright'].get_height() + sides['bottomright'].get_height())
        scale_right_surf = pygame.transform.scale(sides['right'], (sides['right'].get_width(), right_height))
        image.blit(scale_right_surf, (size[0] - sides['bottomright'].get_width(), sides['topright'].get_height()))
        
        #? center color
        center_width = size[0] - (sides['left'].get_width() + sides['right'].get_width())
        center_height = size[1] - (sides['top'].get_height() + sides['bottom'].get_height())
        scale_center_surf = pygame.transform.scale(sides['center'], (center_width, center_height))
        image.blit(scale_center_surf, (sides['left'].get_width(), sides['top'].get_height()))
        
        #! Return that image to the blocks or the player
        return image