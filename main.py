import pygame
import os
import time
import random

pygame.font.init()
pygame.init()
pygame.mixer.init()

WIDTH = HEIGHT =750
SCREEN = pygame.display.set_mode((WIDTH,HEIGHT))
pygame.display.set_caption("Space Invaders")

#Load images
RED_SPACE_SHIP = pygame.image.load(os.path.join("assets","pixel_ship_red_small.png")).convert_alpha()

GREEN_SPACE_SHIP = pygame.image.load(os.path.join("assets","pixel_ship_green_small.png")).convert_alpha()
BLUE_SPACE_SHIP = pygame.image.load(os.path.join("assets","pixel_ship_blue_small.png")).convert_alpha()
#player shp
YELLOW_SPACE_SHIP = pygame.image.load(os.path.join("assets","pixel_ship_yellow.png")).convert_alpha()


#Lasers
RED_LASER = pygame.image.load(os.path.join("assets","pixel_laser_red.png")).convert_alpha()
GREEN_LASER = pygame.image.load(os.path.join("assets","pixel_laser_green.png")).convert_alpha()
BLUE_LASER = pygame.image.load(os.path.join("assets","pixel_laser_blue.png")).convert_alpha()
YELLOW_LASER = pygame.image.load(os.path.join("assets","pixel_laser_yellow.png")).convert_alpha()


BG = pygame.image.load(os.path.join("assets","background-black.png"))
BG = pygame.transform.scale(BG,(WIDTH,HEIGHT))

SHOOT_SOUND = pygame.mixer.Sound(os.path.join("assets","shoot.wav"))
INVADER_KILLED = pygame.mixer.Sound(os.path.join("assets","invaderkilled.wav"))

def collide(obj1,obj2):
    offset_x = obj2.x - obj1.x
    offset_y = obj2.y - obj1.y
    return obj1.mask.overlap(obj2.mask,(offset_x,offset_y)) != None

class Laser:

    def __init__(self,x,y,img):
        self.x = x
        self.y = y
        self.img = img
        self.mask = pygame.mask.from_surface(self.img)

    def draw(self,screen):
        screen.blit(self.img,(self.x,self.y))

    def move(self,vel):
        self.y += vel

    def off_screen(self,height):
        return not (self.y <= height and self.y >= 0)

    def collision(self,obj):
        return collide(self,obj)

class Ship:
    COOLDOWN = 30
    def __init__(self,x,y,velocity=5,health=100):
        self.x = x
        self.y = y
        self.health = health
        self.ship_img = None
        self.laser_img = None
        self.lasers = []
        self.velocity =velocity
        self.cool_down_counter = 0
    
    def draw(self,screen):
        screen.blit(self.ship_img,(self.x,self.y))
        for laser in self.lasers:
            laser.draw(screen)
    
    def move_lasers(self,vel,obj):
        self.cooldown()

        for laser in list(self.lasers):
            laser.move(vel)
            if laser.off_screen(HEIGHT):
                self.lasers.remove(laser)
            elif laser.collision(obj):
                obj.health -= 10
                self.lasers.remove(laser)
    def get_width(self):
        return self.ship_img.get_width()

    def get_height(self):
        return self.ship_img.get_height()
    
    def cooldown(self):
        if self.cool_down_counter >= self.COOLDOWN:
            self.cool_down_counter = 0
        elif self.cool_down_counter > 0:
            self.cool_down_counter += 1
    def shoot(self):
        if self.cool_down_counter == 0:
            laser = Laser(self.x,self.y,self.laser_img)
            self.lasers.append(laser)
            self.cool_down_counter = 1
            SHOOT_SOUND.play()
class Player(Ship):
    
    def __init__(self,x,y,velocity=5,health=100):
        super().__init__(x,y,velocity,health)
        self.ship_img = YELLOW_SPACE_SHIP
        self.laser_img = YELLOW_LASER
        self.mask = pygame.mask.from_surface(self.ship_img) #tell us where pixels are in this image so if we did a collision tell you(pixel perfect collision)
        self.max_health = health

    def move_lasers(self,vel,objs):
        self.cooldown()

        for laser in list(self.lasers):
            laser.move(vel)
            if laser.off_screen(HEIGHT):
                self.lasers.remove(laser)
            else:
                for obj in list(objs):
                    if laser.collision(obj):
                        objs.remove(obj)
                        self.lasers.remove(laser)
         
    def draw(self,screen):
        super().draw(screen)
        self.healthbar(screen)

    def healthbar(self,screen):
        pygame.draw.rect(screen,(255,0,0),(self.x,self.y + self.ship_img.get_height() + 10,self.ship_img.get_width(),10))
        pygame.draw.rect(screen,(0,255,0),(self.x,self.y + self.ship_img.get_height() + 10,self.ship_img.get_width() * (self.health/self.max_health),10))
class Enemy(Ship):
    COLOR_MAP = {'red': (RED_SPACE_SHIP,RED_LASER), 'blue': (BLUE_SPACE_SHIP,BLUE_LASER),'green': (GREEN_SPACE_SHIP,GREEN_LASER)}
    def __init__(self,x,y,color,velocity=5,health=100):
        super().__init__(x,y,velocity,health)
        self.ship_img,self.laser_img = self.COLOR_MAP[color]
        self.mask = pygame.mask.from_surface(self.ship_img)

    def shoot(self):
        if self.cool_down_counter == 0:
            laser = Laser(self.x - 20,self.y,self.laser_img)
            self.lasers.append(laser)
            self.cool_down_counter = 1

    def move(self,vel):
        self.y += vel

def main():
    done = False
    FPS = 60
    clock = pygame.time.Clock()
    level = 0
    lives = 5
    main_font = pygame.font.SysFont("comicsansms",50)
    lost_font = pygame.font.SysFont("comicsansms",60)
    player = Player(300,630)
    enemies =[] 
    wave_length = 0
    enemy_vel = 2
    laser_velocity = 4

    def redraw_window():
        
        SCREEN.blit(BG,(0,0))
        #draw text
        lives_label = main_font.render(f"Lives: {lives}",True,(255,255,255))
        level_label = main_font.render(f"Level: {level}",True,(255,255,255))
        SCREEN.blit(lives_label,(10,10))
        SCREEN.blit(level_label,(WIDTH - level_label.get_width() - 10,10))
        for enemy in enemies:
            enemy.draw(SCREEN)
        player.draw(SCREEN)

        if lost:
            lost_label = lost_font.render("You Lost!!",True,(255,255,255))
            SCREEN.blit(lost_label,(WIDTH/2 - lost_label.get_width() /2,350))
        pygame.display.update()

    lost = False
    lost_count = 0
    clicked_exit = False
    while not done:
        if lives <= 0 or player.health <= 0:
            pygame.mixer.music.stop()
            pygame.mixer.music.load(os.path.join('assets',"death.ogg"))
            pygame.mixer.music.play(-1)
            lost = True
            lost_count += 1
        
        if lost:
            if lost_count > FPS * 3:
                done = True
                pygame.mixer.music.stop()
            else:
                redraw_window()
                clock.tick(FPS)
                continue

        if len(enemies) == 0:
            level += 1
            wave_length += 5
            for i in range(wave_length):
                enemy = Enemy(random.randint(50,WIDTH - 100),random.randint(-1500,-100),random.choice(["red","blue","green"]))
                enemies.append(enemy)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                done = True
                clicked_exit = True

        pressed_keys = pygame.key.get_pressed()
        if pressed_keys[pygame.K_a] and player.x - player.velocity >= 0: #left
            player.x -= player.velocity
        if pressed_keys[pygame.K_d] and player.x + player.velocity + player.get_width() <= WIDTH:
            player.x += player.velocity
        if pressed_keys[pygame.K_w] and player.y - player.velocity >= 0:
            player.y -= player.velocity
        if pressed_keys[pygame.K_s] and player.y + player.velocity + player.get_height() + 20 <= HEIGHT:
            player.y += player.velocity
        if pressed_keys[pygame.K_SPACE]:
            player.shoot()
        for enemy in list(enemies):
            enemy.move(enemy_vel)
            enemy.move_lasers(laser_velocity,player)
            if random.randint(1,2 * 60) == 1:
                enemy.shoot()
            if collide(enemy,player):
                player.health -= 10
                enemies.remove(enemy)
            elif enemy.y + enemy.get_height() > HEIGHT:
                lives -= 1
                enemies.remove(enemy)
        player.move_lasers(-laser_velocity,enemies)

        redraw_window()
        clock.tick(FPS)

    return clicked_exit

#main game loop


def main_menu():
    title_font = pygame.font.SysFont("comicsansms",60)
    done = False
    pygame.mixer.music.load(os.path.join("assets","intro.ogg"))
    pygame.mixer.music.play(loops=-1)
    pygame.mixer.music.set_volume(0.5)
    while not done:
        SCREEN.blit(BG,(0,0))
        title_label = title_font.render("Press the mouse to begin...",True,(255,255,255))
        SCREEN.blit(title_label,(WIDTH/2 - title_label.get_width()/2,350))
        pygame.display.update()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                done = True
            if event.type == pygame.MOUSEBUTTONDOWN:
                pygame.mixer.music.stop()
                pygame.mixer.music.load(os.path.join("assets","level1.ogg"))
                pygame.mixer.music.play(loops=-1)
                done = main()
                pygame.mixer.music.load(os.path.join("assets","intro.ogg"))
                pygame.mixer.music.play(loops=-1)
                pygame.mixer.music.set_volume(0.5)
            
         
    pygame.quit()

if __name__ == "__main__":
    main_menu()



