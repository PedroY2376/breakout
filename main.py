import pygame, time, random
from settings import *
from sprites import Player,Ball,Block,Upgrade,Projectile
from surface_maker import Surface_maker

class Game:
    def __init__(self):
        #! Display Game
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption('Brick Breaker')
        self.bg = pygame.image.load('graphics/other/bg.png').convert()
        self.clock = pygame.time.Clock()
           
        self.bg = pygame.transform.scale(self.bg, (pygame.math.Vector2(self.bg.get_size())*scale_factor))
        self.crt = CRT()
        self.font = pygame.font.SysFont('cursive', 50, False, False)
        self.active = True
        
        #! Sprites Setup
        self.all_sprites = pygame.sprite.Group()
        self.block_sprites = pygame.sprite.Group()
        self.upgrade_sprites = pygame.sprite.Group()
        self.projectile_sprites = pygame.sprite.Group()
        
        self.surface_maker = Surface_maker()
        self.player = Player(self.all_sprites, self.surface_maker)
        self.stage_setup()
        self.ball = Ball(self.all_sprites, self.player, self.block_sprites, self.player.image , self.player.vel)
        
        #! Hearts
        self.heart_surf = pygame.image.load('graphics/other/heart.png').convert_alpha()
        self.heart_surf = pygame.transform.scale(self.heart_surf, (pygame.math.Vector2(self.heart_surf.get_size())*scale_factor))
        
        #! Projectile
        self.prjectile_surf = pygame.image.load('graphics/other/projectile.png').convert_alpha()
        
        #! Timer Projectile
        self.timer_projectile = pygame.USEREVENT + 1
        pygame.time.set_timer(self.timer_projectile, 1500)
        
        #! Sounds
        self.music = pygame.mixer.Sound('sounds/music.wav')
        self.music.set_volume(0.1)
        self.music.play(loops=-1)
        
        self.powerup_sound = pygame.mixer.Sound('sounds/powerup.wav')
        self.powerup_sound.set_volume(0.15)
        
        self.laser_sound = pygame.mixer.Sound('sounds/laser.wav')
        self.laser_sound.set_volume(0.15)
        
        self.laser_hit = pygame.mixer.Sound('sounds/laser_hit.wav')
        self.laser_hit.set_volume(0.15)

    def stage_setup(self):
        #? cycle through all rows and collumns of BLOCK MAP
        for row_index, row in enumerate(BLOCK_MAP):
            for col_index, col in enumerate(row):
                if col != ' ':
                    #? find the x and y position for each block
                    x = col_index * (BLOCK_WIDTH + GAP_SIZE) + GAP_SIZE/2
                    y = TOP_OFFSET + row_index * (BLOCK_HEIGHT + GAP_SIZE) + GAP_SIZE/2
                    Block(col, (x,y), [self.all_sprites, self.block_sprites], self.surface_maker, self.create_upgrade)
    
    def create_upgrade(self,pos):
        upgrade_type = random.choice(UPGRADES)
        Upgrade(pos, upgrade_type, [self.all_sprites, self.upgrade_sprites])
    
    def upgrade_collision(self):
        overlap_sprites = pygame.sprite.spritecollide(self.player, self.upgrade_sprites, True)
        if overlap_sprites:
            for sprite in overlap_sprites:
                self.player.upgrade(sprite.upgrade_type)
                self.powerup_sound.play()
                  
    def display_hearts(self):
        for i in range(self.player.hearts):
            x = 10 + (i * (self.heart_surf.get_width()+4))
            self.screen.blit(self.heart_surf, (x,7))
        
    def create_projectile(self):
        for projectile in self.player.laser_rects:
            Projectile(projectile.midtop - pygame.math.Vector2(0,30),self.prjectile_surf,[self.all_sprites, self.projectile_sprites])
        self.laser_sound.play()
        
    def projectile_block_collision(self):
        for projectile in self.projectile_sprites:
            overlap_sprites = pygame.sprite.spritecollide(projectile, self.block_sprites, False)
            if overlap_sprites:
                for sprite in overlap_sprites:
                    sprite.get_damage(1)
                projectile.kill()
                self.laser_hit.play()

    def game_over(self):
        if self.player.hearts <= 0:
            self.active = False
            self.all_sprites.empty()

    def run_game_over(self):
        surf = pygame.Surface((SCREEN_WIDTH,SCREEN_HEIGHT))
        surf.fill((0,0,0))
        surf.set_alpha(150)
        
        txt_surf = self.font.render('Press Space to restart', True, (255,255,255))
        txt_rect = txt_surf.get_rect(center = (SCREEN_WIDTH/2, SCREEN_HEIGHT/2))
        
        self.screen.blit(surf, (0,0))
        self.screen.blit(txt_surf, txt_rect)

    def restart(self): 
        self.active = True
        self.player.hearts = 3
        self.player = Player(self.all_sprites, self.surface_maker)
        self.stage_setup()
        self.ball = Ball(self.all_sprites, self.player, self.block_sprites, self.player.image , self.player.vel)

    def run(self):
        last_time = time.time()
        while True:            
            #! Delta Time
            dt = time.time() - last_time
            last_time = time.time()
            
            #! Event loop
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    exit()
                    
                if self.active and event.type == self.timer_projectile:
                    game.create_projectile()
                    
                if event.type == pygame.KEYDOWN:
                    if self.active and event.key == pygame.K_SPACE:
                        self.ball.active = True
                        
                    elif not self.active and event.key == pygame.K_SPACE:
                        self.restart()
                        
            
            #! Draw and Update
            self.screen.blit(self.bg, (0,0))
            if self.active:
                self.all_sprites.draw(self.screen)
                self.all_sprites.update(dt)
                self.display_hearts()
                self.upgrade_collision()
                self.projectile_block_collision()
                self.game_over()
                self.crt.draw()
            
            else:
                self.run_game_over()
            
            pygame.display.update()
            self.clock.tick(FPS)       
 
class CRT:
    def __init__(self):
        vignette = pygame.image.load('graphics/other/tv.png').convert_alpha()
        self.scaled_vignette = pygame.transform.scale(vignette, (SCREEN_WIDTH, SCREEN_HEIGHT))
        self.screen = pygame.display.get_surface()
        self.create_crt_lines()
        
    def create_crt_lines(self):
        line_height = 4
        line_amount = SCREEN_HEIGHT // line_height
        for line in range(line_amount):
            y = line * line_height
            pygame.draw.line(self.scaled_vignette, (30,30,30), (0,y), (SCREEN_WIDTH,y), 1)
         
    def draw(self):
        self.scaled_vignette.set_alpha(random.randint(65,80))
        self.screen.blit(self.scaled_vignette,(0,0))
    
if __name__ == '__main__':    
    pygame.init()
    pygame.mixer.init()
    game = Game()
    game.run()
