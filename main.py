import pygame
import os
import time
import random

pygame.font.init()

WIDTH = 900
HEIGHT = 750
WIN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption('HATYAI CHICKEN SPACE WAR')

#load img
RED_SPACE_SHIP = pygame.image.load(os.path.join('assets', 'red_enemy_small.png'))
GREEN_SPACE_SHIP = pygame.image.load(os.path.join('assets', 'green_enemy_small.png'))
BLUE_SPACE_SHIP= pygame.image.load(os.path.join('assets', 'blue_enemy_small.png'))

#player player
YELLOW_SPACE_SHIP = pygame.image.load(os.path.join('assets', 'player ship.png'))

#LASERS
RED_LASER = pygame.image.load(os.path.join('assets', 'player laser.png'))
GREEN_LASER = pygame.image.load(os.path.join('assets', 'player laser.png'))
BLUE_LASER = pygame.image.load(os.path.join('assets', 'player laser.png'))
YELLOW_LASER = pygame.image.load(os.path.join('assets', 'yellow player laser.png'))

#BG
BG  = pygame.transform.scale(pygame.image.load(os.path.join('assets', 'space_bg.png')), (WIDTH, HEIGHT))
#SOUND
MENU_SOUND = mixer.Sound(os.path.join('sounds', '8bit-music-for-game-68698.mp3'))
BG_SOUND = mixer.Sound(os.path.join('sounds', background.wav')
LASER_SOUND = mixer.Sounds(os.path.join('sounds', 'laser.wav'))
EXPLOSION_SOUND = mixer.Sound(os.path.join('sounds', '8-bit-explosion1wav-14656.mp3'))                                    
PAUSED_SOUND = mixer.Sound(os.path.join('sounds', 'attack-jingle-sound-effect-jvanko-125083.mp3'))
                                    
class Laser:
    def __init__(self, x, y, img):
        self.x = x
        self.y = y
        self.img = img
        self.mask = pygame.mask.from_surface(self.img)

    def draw(self, window):
        window.blit(self.img, (self.x, self.y))
    
    def move(self, vel):
        self.y += vel
    
    def off_screen(self, height):
        return not(self.y <= height and self.y >=0)
    
    def collision(self, obj):
        return collide(self, obj)

class Ship:
    COOLDOWN = 10
    def __init__(self, x, y, health=100):
        self.x = x
        self.y = y
        self.health = health
        self.ship_img = None
        self.laser_img = None
        self.lasers = []
        self.cool_down_counter = 0

    def draw(self, window):
        window.blit(self.ship_img, (self.x, self.y))
        for laser in self.lasers:
            laser.draw(window)
    def move_lasers(self, vel, obj):
        self.cooldown()
        for laser in self.lasers:
            laser.move(vel)
            if laser.off_screen(HEIGHT):
                self.lasers.remove(laser)
            elif laser.collision(obj):
                obj.health -= 100
                EXPLOSION_SOUND.play()
                self.lasers.remove(laser)
    
    def cooldown(self):
        if self.cool_down_counter >= self.COOLDOWN:
            self.cool_down_counter = 0
        elif self.cool_down_counter > 0:
            self.cool_down_counter += 1

    def shoot(self):
        if self.cool_down_counter == 0:
            laser = Laser(self.x+40, self.y-20, self.laser_img)
            self.lasers.append(laser)
            self.cool_down_counter = 1

    def get_width(self):
        return self.ship_img.get_width()
    
    def get_height(self):
        return self.ship_img.get_height()

class Player(Ship):
    def __init__(self, x, y, health=1000):
        super().__init__(x, y, health)
        self.ship_img = YELLOW_SPACE_SHIP
        self.laser_img = YELLOW_LASER
        self.mask = pygame.mask.from_surface(self.ship_img)
        self.max_health = health

    def move_lasers(self, vel, objs):
        self.cooldown()
        for laser in self.lasers:
            laser.move(vel)
            if laser.off_screen(HEIGHT):
                self.lasers.remove(laser)
                EXPLOTION_SOUND.play() #เสียงตอนยิงโดน 
            else:
                for obj in objs:
                    if laser.collision(obj):
                        objs.remove(obj)
                        self.lasers.remove(laser)

class Enemy(Ship):
    COLOER_MAP = {
                'red': (RED_SPACE_SHIP, RED_LASER),
                'green': (GREEN_SPACE_SHIP, GREEN_LASER),
                'blue': (BLUE_SPACE_SHIP, BLUE_LASER)
                }

    def __init__(self, x, y, color, health=1):
        super().__init__(x, y, health)
        self.ship_img, self.laser_img = self.COLOER_MAP[color]
        self.mask = pygame.mask.from_surface(self.ship_img)
        self.max_health = health
    
    def move(self, vel):
        self.y += vel

    def shoot(self):
        if self.cool_down_counter == 0:
            laser = Laser(self.x+35, self.y, self.laser_img)
            self.lasers.append(laser)
            self.cool_down_counter = 1

#hitbox
def collide(obj1, obj2):
    offset_x = obj2.x - obj1.x
    offset_y = obj2.y - obj1.x
    return obj1.mask.overlap(obj2.mask, (offset_x, offset_y)) != None
def main():
    run = True
    FPS = 60
    level = 0
    lives = 5
    main_font = pygame.font.SysFont('Retro Gaming', 50)
    lost_font = pygame.font.SysFont('Retro Gaming', 60)

    enemies = []
    wave_length = 5

    laser_vel = 4

    enemy_vel = 1

    player_vel = 10 #ทุกครั้งที่กดplayerจะขยับ [เลข] pixels

    player = Player(300, 650)


    clock = pygame.time.Clock()
    lost = False
    lost_count = 0

    def redraw_window():    #redraw img ทุกอย่าง
        WIN.blit(BG, (0, 0))
        #draw text
        lives_label = main_font.render(f'Lives: {lives}', 1, (255, 255, 255))   #(r,g,b)
        level_label = main_font.render(f'Level: {level}', 1, (255, 255, 255))

        WIN.blit(lives_label, (10, 10))
        WIN.blit(level_label, (WIDTH - level_label.get_width() - 10, 10))

        for enemy in enemies:
            enemy.draw(WIN)

        player.draw(WIN)

        if lost:
            lost_label = lost_font.render('GAME OVER!!', 1, (255, 255, 255))
            WIN.blit(lost_label, (WIDTH/2 - lost_label.get_width()/2, 350))

        pygame.display.update()

    while run:
        clock.tick(FPS)
        redraw_window()
        
        if lives <= 0 or player.health <= 0:
            lost = True
            lost_count += 1
        
        if lost:
            if lost_count > FPS * 3:
                run = False
            else:
                continue

        if len(enemies) == 0:
            level += 1
            wave_length += 5    #เพิ่มenemy 5 ตัว ทุกๆเลเวล
            for i in range(wave_length):
                enemy = Enemy(random.randrange(50, WIDTH-100), random.randrange(-1500*level/5, -100), random.choice(['red', 'blue', 'green']))
                enemies.append(enemy)

        for event in pygame.event.get():    #รับeventจากuser
            if event.type == pygame.QUIT:   #ปิดเกม
                run = False

        keys = pygame.key.get_pressed()
        if keys[pygame.K_a] and player.x - player_vel > 0: #left / and player.xy +- player_vel <> 0 or HEIGHT or WIDTH คือ ไม่ให้เกินหน้าจอ
            player.x -= player_vel
        if keys[pygame.K_d] and player.x + player_vel + player.get_width() < WIDTH: #right
            player.x += player_vel
        if keys[pygame.K_w] and player.y - player_vel - 50 > 0 : #up - 50 ไม่ให้เกิน label ของ level และ lives
            player.y -= player_vel
        if keys[pygame.K_s] and player.y + player_vel + player.get_height() < HEIGHT: #down
            player.y += player_vel
        if keys[pygame.K_SPACE]:    #ยิงlaser
            player.shoot()


        for enemy in enemies[:]:
            enemy.move(enemy_vel)
            enemy.move_lasers(laser_vel, player)

            if random.randrange(0, 10*60) == 1:
                enemy.shoot()


            if enemy.y + enemy.get_height() > HEIGHT:
                lives -= 1
                enemies.remove(enemy)
        
        player.move_lasers(-laser_vel, enemies)
main()
