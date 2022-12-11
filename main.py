import pygame
import os
import time
import random
from pygame import mixer
import pygame.freetype

pygame.font.init()
pygame.init()

WIDTH = 900
HEIGHT = 750
WIN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption('HATYAI CHICKEN SPACE WAR')

#load img
RED_SPACE_SHIP = pygame.image.load(os.path.join('assets', 'red_enemy_small.png'))
GREEN_SPACE_SHIP = pygame.image.load(os.path.join('assets', 'green_enemy_small.png'))
BLUE_SPACE_SHIP= pygame.image.load(os.path.join('assets', 'blue_enemy_small.png'))
CHICK = pygame.image.load(os.path.join('assets', 'chick.png'))
HEALING_HEART = pygame.image.load(os.path.join('assets', 'healing-heart.png'))

#player player
YELLOW_SPACE_SHIP = pygame.image.load(os.path.join('assets', '5724-duck.png'))

#LASERS
RED_LASER = pygame.image.load(os.path.join('assets', 'player laser.png'))
GREEN_LASER = pygame.image.load(os.path.join('assets', 'player laser.png'))
BLUE_LASER = pygame.image.load(os.path.join('assets', 'player laser.png'))
YELLOW_LASER = pygame.image.load(os.path.join('assets', 'LASER YELLOW.png'))

#BG
BG_MENU = pygame.transform.scale(pygame.image.load(os.path.join('assets', 'earth space.jpg')), (WIDTH, HEIGHT))
BG_GAME  = pygame.transform.scale(pygame.image.load(os.path.join('assets', 'space_bg.png')), (WIDTH, HEIGHT))

#SOUND
MENU_SOUND = mixer.Sound(os.path.join('sounds', '8bit-music-for-game-68698.mp3'))
BG_SOUND = mixer.Sound(os.path.join('sounds', 'background.wav'))
LASER_SOUND = mixer.Sound(os.path.join('sounds', 'laser.wav'))
EXPLOSION_SOUND = mixer.Sound(os.path.join('sounds', '8-bit-explosion1wav-14656.mp3'))
GAMEOVER_SOUND = mixer.Sound(os.path.join('sounds', 'mixkit-retro-arcade-game-over-470.wav'))
PAUSED_SOUND = mixer.Sound(os.path.join('sounds', 'attack-jingle-sound-effect-jvanko-125083.mp3'))
PRESS_SOUND = mixer.Sound(os.path.join('sounds', 'attack-jingle-sound-effect-jvanko-125083.mp3'))
HEAL_SOUND = mixer.Sound(os.path.join('sounds', 'Healing-SE.mp3'))
                                    
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
    COOLDOWN = 20
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
                obj.health -= 10
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
    def __init__(self, x, y, health=100):
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
                EXPLOSION_SOUND.play()      #เสียงตอนยิงโดน
            else:
                for obj in objs:
                    if laser.collision(obj):
                        objs.remove(obj)
                        if laser in self.lasers:
                            self.lasers.remove(laser)
                            EXPLOSION_SOUND.play()      #เสียงตอนยิงโดน

    def draw(self, window):
        super().draw(window)
        self.healthbar(window)      #health bar

    def healthbar(self, window):
        pygame.draw.rect(window, (255,0,0), (self.x, self.y + self.ship_img.get_height() + 10, self.ship_img.get_width(), 10))
        pygame.draw.rect(window, (0,255,0), (self.x, self.y + self.ship_img.get_height() + 10, self.ship_img.get_width() * (self.health/self.max_health), 10))


class Enemy(Ship):
    COLOER_MAP = {
                'red': (RED_SPACE_SHIP, RED_LASER),
                'green': (GREEN_SPACE_SHIP, GREEN_LASER),
                'blue': (BLUE_SPACE_SHIP, BLUE_LASER)
                }

    def __init__(self, x, y, color, health=100):
        super().__init__(x, y, health)
        self.ship_img, self.laser_img = self.COLOER_MAP[color]
        self.mask = pygame.mask.from_surface(self.ship_img)

    def move(self, vel):
        self.y += vel

    def shoot(self):
        if self.cool_down_counter == 0:
            laser = Laser(self.x+35, self.y, self.laser_img)
            self.lasers.append(laser)
            self.cool_down_counter = 1
            
class Heal_Hp(Ship):
    HEAL = {'heart': (HEALING_HEART)}

    def __init__(self, x, y, color, health=100):
        super().__init__(x, y, health)
        self.ship_img = self.HEAL[color]
        self.mask = pygame.mask.from_surface(self.ship_img)

    def move(self, vel):
        self.y += vel
            
#hitbox
def collide(obj1, obj2):
    offset_x = obj2.x - obj1.x
    offset_y = obj2.y - obj1.y
    return obj1.mask.overlap(obj2.mask, (offset_x, offset_y)) != None

#func paused
def pause():
    paused = True
    PAUSED_SOUND.play()
    while paused:
        for event in pygame.event.get():

            if event.type == pygame.QUIT:   # กดX ออกเกม
                pygame.quit()
                quit()

            if event.type == pygame.KEYDOWN:
                PRESS_SOUND.play()
                if event.key == pygame.K_c:     #Press C to continue the game
                    BG_SOUND.play()
                    paused = False
                elif event.key == pygame.K_r:   #Pres R to restart the game
                    main_menu()
                elif event.key == pygame.K_q:   #Press Q to exit
                    pygame.quit()
                    quit()
        
        MESSAGE_font = pygame.font.Font('Retro Gaming.ttf', 70)
        MESSAGE_TO_SCREEN = MESSAGE_font.render('PAUSED', 1, (255, 255, 255))
        WIN.blit(MESSAGE_TO_SCREEN, (WIDTH/2 - MESSAGE_TO_SCREEN.get_width()/2, 300))
        MESSAGE_font = pygame.font.Font('Retro Gaming.ttf', 40)
        MESSAGE_TO_SCREEN = MESSAGE_font.render('Press [C] to continue', 1, (255, 255, 255))
        WIN.blit(MESSAGE_TO_SCREEN, (WIDTH/2 - MESSAGE_TO_SCREEN.get_width()/2, 400))
        MESSAGE_font = pygame.font.Font('Retro Gaming.ttf', 30)
        MESSAGE_TO_SCREEN = MESSAGE_font.render('[Q] to exit', 1, (255, 255, 255))
        WIN.blit(MESSAGE_TO_SCREEN, (WIDTH/1.2 - MESSAGE_TO_SCREEN.get_width()/2, 670))
        MESSAGE_TO_SCREEN = MESSAGE_font.render('[R] to restart', 1, (255, 255, 255))
        WIN.blit(MESSAGE_TO_SCREEN, (WIDTH/6 - MESSAGE_TO_SCREEN.get_width()/2, 670))
        #gameDisplay.fill(white)

        pygame.display.update()

def main():
    run = True
    FPS = 60
    level = 0
    lives = 5
    score = 0
    main_font = pygame.font.SysFont('Retro Gaming', 45)
    lost_font = pygame.font.SysFont('Retro Gaming', 60)


    wave_length = 5
    laser_vel = 10
    enemy_laser_vel = 4

    enemies = []
    enemy_vel = 1
    
    healing_potion = []
    heal_vel = 2

    player_vel = 10 #ทุกครั้งที่กดplayerจะขยับ [เลข] pixels
    player = Player(375, 600)


    clock = pygame.time.Clock()
    lost = False
    lost_count = 0

    def redraw_window():    #redraw img ทุกอย่าง
        WIN.blit(BG_GAME, (0, 0))
        #draw text
        lives_label = main_font.render(f'LIVES: {lives}', 1, (255, 255, 255))   #(r,g,b)
        level_label = main_font.render(f'LEVEL: {level}', 1, (255, 255, 255))
        score_label = main_font.render(f'SCORE: {score}', 1, (255, 255, 255))

        WIN.blit(lives_label, (10, 10))
        WIN.blit(score_label, (10, 50))
        WIN.blit(level_label, (WIDTH - level_label.get_width() - 10, 10))

        for enemy in enemies:
            enemy.draw(WIN)
            
        for heal in healing_potion:
            heal.draw(WIN)
            
        player.draw(WIN)

        if lost:
            lost_label = lost_font.render('GAME OVER!!', 1, (255, 255, 255))
            WIN.blit(lost_label, (WIDTH/2 - lost_label.get_width()/2, 350))
            BG_SOUND.stop()
            GAMEOVER_SOUND.play()

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
            if level > 1:
                score += 500
            if level%2 == 0:    #ปล่อยHeal ทุกๆ 2 level 
                for i in range(level//2): #เพิ่มHeal 1 อัน ทุกรอบที่ปล่อย Heal
                    heal = Heal_Hp(random.randrange(50, WIDTH-100), random.randrange(-1500*level/5, -100), random.choice(['heart']))
                    healing_potion.append(heal)
            wave_length += 5    #เพิ่มenemy 5 ตัว ทุกๆเลเวล
            if level == 3:
                # EXCLUSIVE ระดับ 1
                for _ in range(wave_length + 5):
                    strong_enemy = Enemy(random.randrange(50, WIDTH-100), random.randrange(-1500*level/5, -100), random.choice(['green']))
                    enemies.append(strong_enemy)
            else:
                for i in range(wave_length):
                    enemy = Enemy(random.randrange(50, WIDTH-100), random.randrange(-1500*level/5, -100), random.choice(['red', 'blue', 'green']))
                    enemies.append(enemy)
                
        for event in pygame.event.get():    #รับeventจากuser
            if event.type == pygame.QUIT:   #ปิดเกม
                quit()

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
            LASER_SOUND.play()
            player.shoot()
        if keys[pygame.K_ESCAPE]:   #Paused
            BG_SOUND.stop()
            pause()


        for enemy in enemies[:]:
            enemy.move(enemy_vel)
            enemy.move_lasers(laser_vel, player)

            if random.randrange(0, 10*60) == 1:
                LASER_SOUND.play()
                enemy.shoot()


            #Enemy ชน Player
            if collide(enemy, player):
                EXPLOSION_SOUND.play()
                player.health -= 10
                enemies.remove(enemy)
            
            #Enemy ผ่านไปได้
            elif enemy.y + enemy.get_height() > HEIGHT:
                EXPLOSION_SOUND.play()
                lives -= 1
                enemies.remove(enemy)
                
        for heal in healing_potion[:]:
            heal.move(heal_vel)
            if collide(heal, player):
                HEAL_SOUND.play()
                if player.health < 100:
                    player.health += 10
                healing_potion.remove(heal)


        player.move_lasers(-laser_vel, enemies)
        
#หน้าแรก
def main_menu():
    MENU_SOUND.play(-1)
    title_font = pygame.font.Font('Retro Gaming.ttf', 40)
    run = True
    while run:

        WIN.blit(BG_MENU, (0,0))
        #WIN.blit(CHICK, (WIDTH/2 - CHICK.get_width()/2, 100))
        title_label = title_font.render("Press the [SPACEBAR] to Start", 1, (255, 255, 0))
        WIN.blit(title_label, (WIDTH/2 - title_label.get_width()/2, 400))

        MESSAGE_font = pygame.font.Font('Retro Gaming.ttf', 30)
        MESSAGE_TO_SCREEN = MESSAGE_font.render('HATYAI CHICKEN\'S SPACE WAR', 1, (255, 255, 255))
        WIN.blit(MESSAGE_TO_SCREEN, (WIDTH/2 - MESSAGE_TO_SCREEN.get_width()/2, 330))

        pygame.display.update()


        keys = pygame.key.get_pressed()
        for event in pygame.event.get():

            #กดX ออกเกม
            if event.type == pygame.QUIT:
                run = False

            #SPACEBAR to Start the game
            if keys[pygame.K_SPACE]:
                MENU_SOUND.stop()
                PRESS_SOUND.play()
                BG_SOUND.play(-1)
                main()

    pygame.quit()

main_menu()
