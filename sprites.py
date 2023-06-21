import pygame, random
from settings import *

class Player(pygame.sprite.Sprite):
    def __init__(self, group, surface_maker):
        super().__init__(group)
        
        #! Setup
        self.screen = pygame.display.get_surface()
        self.surface_maker = surface_maker
        self.image = self.surface_maker.get_surf('player', (SCREEN_WIDTH/10, SCREEN_HEIGHT/20))
        
        #! Position
        self.rect = self.image.get_rect(midbottom = (SCREEN_WIDTH/2, SCREEN_HEIGHT - 20))
        self.old_rect = self.rect.copy()
        self.direction = pygame.math.Vector2(0,0)
        self.pos = pygame.math.Vector2(self.rect.topleft)
        self.vel = 300
  
        self.hearts = 3
        
        #? Laser
        self.laser_amount = 0
        self.laser_surf = pygame.image.load('graphics/other/laser.png').convert_alpha()
        self.laser_rects = []
  
    def mover(self, dt):
        keys = pygame.key.get_pressed()
        if keys[pygame.K_RIGHT] and self.rect.right <= SCREEN_WIDTH: self.direction.x = 1
        elif keys[pygame.K_LEFT] and self.rect.x >= 0: self.direction.x = -1
        else: self.direction.x = 0
        
        self.pos.x += self.direction.x * self.vel * dt
        self.rect.x = round(self.pos.x)
        
    def create_old_rect(self):
        self.old_rect = self.rect.copy()
        
    def upgrade(self, upgrade_type):
        if upgrade_type == 'speed': self.vel += 50
        if upgrade_type == 'heart': self.hearts += 1
        if upgrade_type == 'size': 
            new_width = self.rect.width * 1.1
            self.image = self.surface_maker.get_surf('player', (new_width, self.rect.height))
            self.rect = self.image.get_rect(center = (self.rect.center))
            self.pos.x = self.rect.x
        if upgrade_type == 'laser': 
            self.laser_amount += 1
       
    def display_lasers(self):
        self.laser_rects = []
        if self.laser_amount > 0:
            divider_lenght = self.rect.width / (self.laser_amount + 1)
            for i in range(self.laser_amount):
                x = self.rect.left + (divider_lenght * (i + 1))
                laser_rect = self.laser_surf.get_rect(midbottom = (x,self.rect.top))
                self.laser_rects.append(laser_rect)
        
            for laser_rect in self.laser_rects:
                self.screen.blit(self.laser_surf, laser_rect)
        
    def update(self, dt):
        self.create_old_rect()
        self.mover(dt)
        self.display_lasers()

class Ball(pygame.sprite.Sprite):
    def __init__(self, groups, player, blocks, player_width, player_vel):
        super().__init__(groups)
        
        #! Setup
        self.image = pygame.image.load('graphics/other/ball.png').convert_alpha()
        
        #! Collision objects
        self.player = player
        self.player_image = player_width
        self.player_vel = player_vel
        self.blocks = blocks
        
        #! Position
        self.rect = self.image.get_rect(midbottom = (SCREEN_WIDTH/2, SCREEN_HEIGHT - 20 - self.player.rect.height))
        self.old_rect = self.rect.copy()
        self.direction = pygame.math.Vector2((random.choice((1,-1)), -1))
        self.pos = pygame.math.Vector2(self.rect.topleft)
        self.vel = 400
        
        #! active
        self.active = False
        
        self.fail_sound = pygame.mixer.Sound('sounds/fail.wav')
        self.fail_sound.set_volume(0.15)
        
        self.impact_sound = pygame.mixer.Sound('sounds/impact.wav')
        self.impact_sound.set_volume(0.15)
        
    def mover(self, dt):
        if self.active:
            
            if self.direction.magnitude != 0:
                self.direction = self.direction.normalize()
               
            #? Horizontal movement + collision
            self.pos.x += self.direction.x * self.vel * dt
            self.rect.x = round(self.pos.x)
            self.collision('horizontal')
            self.screen_collision('horizontal')
            
            #? Vertical movement + collision
            self.pos.y += self.direction.y * self.vel * dt
            self.rect.y = round(self.pos.y)
            self.collision('vertical')
            self.screen_collision('vertical')
        else:
            self.rect.midbottom = self.player.rect.midtop
            self.pos = pygame.math.Vector2(self.rect.topleft)
           
    def screen_collision(self, direction):
        if direction == 'horizontal':
            if self.rect.x <= 0 :
                self.rect.x = 0
                self.pos.x = self.rect.x
                self.direction.x *= -1
            elif self.rect.right >= SCREEN_WIDTH: 
                self.rect.right = SCREEN_WIDTH
                self.pos.x = self.rect.x
                self.direction.x *= -1
        if direction == 'vertical':
            if self.rect.bottom >= SCREEN_HEIGHT: 
                self.active = False
                self.player.hearts -= 1
                self.direction.y = -1
                self.fail_sound.play()
                self.restart_player()
            elif self.rect.top <= 0:
                self.rect.top = 0
                self.pos.y = self.rect.y
                self.direction.y *= -1
        
    def collision(self, direction):
        #? Find overlaping objects
        overlap_sprites = pygame.sprite.spritecollide(self, self.blocks, False)
        if self.rect.colliderect(self.player.rect):
            overlap_sprites.append(self.player)
            
        if overlap_sprites:
            if direction == 'horizontal':
                for sprite in overlap_sprites:
                    if self.rect.right >= sprite.rect.left and self.old_rect.right <= sprite.old_rect.left:
                        self.rect.right = sprite.rect.left - 1
                        self.pos.x = self.rect.x
                        self.direction.x *= -1
                        self.impact_sound.play()
                        
                    if self.rect.left <= sprite.rect.right and self.old_rect.left >= sprite.old_rect.right:
                        self.rect.left = sprite.rect.right + 1
                        self.pos.x = self.rect.x
                        self.direction.x *= -1
                        self.impact_sound.play()
                        
                    if getattr(sprite, 'health', None): 
                        sprite.get_damage(1)
                
            if direction == 'vertical':
                 for sprite in overlap_sprites:
                    if self.rect.bottom >= sprite.rect.top and self.old_rect.bottom <= sprite.old_rect.top:
                        self.rect.bottom = sprite.rect.top - 1
                        self.pos.y = self.rect.y
                        self.direction.y *= -1
                        self.impact_sound.play()
                        
                    if self.rect.top <= sprite.rect.bottom and self.old_rect.top >= sprite.old_rect.bottom:
                        self.rect.top = sprite.rect.bottom + 1
                        self.pos.y = self.rect.y
                        self.direction.y *= -1
                        self.impact_sound.play()
                        
                    if getattr(sprite, 'health', None): 
                        sprite.get_damage(1)
    
    def create_old_rect(self):
        self.old_rect = self.rect.copy()
    
    def restart_player(self):
        self.player.laser_amount = 0
        self.player.laser_rects = []
        self.player.vel = self.player_vel
        
        self.player.image = self.player_image
        self.player.rect = self.player.image.get_rect(center = (self.player.rect.center))
        self.player.pos.x = self.player.rect.x
    
    def update(self, dt):
        self.create_old_rect()
        self.mover(dt)
        
class Block(pygame.sprite.Sprite):
    def __init__(self,block_type, pos, groups, surface_maker, create_upgrade):
        super().__init__(groups)
        self.surface_maker = surface_maker
        self.image = self.surface_maker.get_surf(COLOR_LEGEND[block_type], (BLOCK_WIDTH, BLOCK_HEIGHT))
        self.rect = self.image.get_rect(topleft = pos)
        self.old_rect = self.rect.copy()
        
        #? Damage information
        self.health = int(block_type)
        
        #? Upgrade
        self.create_upgrade = create_upgrade
        
    def get_damage(self, amount):
        self.health -= amount
        if self.health > 0:
            self.image = self.surface_maker.get_surf(COLOR_LEGEND[str(self.health)], (BLOCK_WIDTH, BLOCK_HEIGHT))
        else:
            if random.randint(0,9) < 3: self.create_upgrade(self.rect.center)
            self.kill()
            
class Upgrade(pygame.sprite.Sprite):
    def __init__(self,pos, upgrade_type,groups):
        super().__init__(groups)
        self.upgrade_type = upgrade_type
        self.image = pygame.image.load(f'graphics/upgrades/{upgrade_type}.png').convert_alpha()
        self.rect = self.image.get_rect(midtop = pos)
        
        self.pos = pygame.math.Vector2(self.rect.topleft)
        self.vel = 300
        
    def update(self, dt):
        self.pos.y += self.vel * dt
        self.rect.y = round(self.pos.y)
        
        if self.rect.top > SCREEN_HEIGHT: self.kill()
        
class Projectile(pygame.sprite.Sprite):
    def __init__(self,pos, surface, groups):
        super().__init__(groups)
        self.image = surface
        self.rect = self.image.get_rect(midbottom = pos)
        self.pos = pygame.math.Vector2(self.rect.topleft)
        self.vel = 300
        
    def update(self, dt):
        self.pos.y -= self.vel * dt
        self.rect.y = self.pos.y
        
        if self.rect.bottom <= -50:
            self.kill()