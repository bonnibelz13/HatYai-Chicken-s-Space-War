import pygame
import os
import time
import random
from pygame import mixer
import pygame.freetype

pygame.font.init()
pygame.init()

#---------------- RESOLUTION ----------------#
WIDTH = 900
HEIGHT = 750
WIN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption('HATYAI CHICKEN SPACE WAR')

#---------------- load img ----------------#
RED_SPACE_SHIP = pygame.image.load(os.path.join('assets', 'red_enemy_small.png'))
GREEN_SPACE_SHIP = pygame.image.load(os.path.join('assets', 'green_enemy_small.png'))
BLUE_SPACE_SHIP= pygame.image.load(os.path.join('assets', 'blue_enemy_small.png'))
CHICK = pygame.image.load(os.path.join('assets', 'chick.png'))
HEALING_HEART = pygame.image.load(os.path.join('assets', 'healing-heart.png'))
GOLDEN_HEALING_HEART = pygame.image.load(os.path.join('assets', 'golden-healing-heart.png'))
DUCK = pygame.image.load(os.path.join('assets', 'DUCK.png'))

#---------------- player img ----------------#
YELLOW_SPACE_SHIP = pygame.image.load(os.path.join('assets', '5724-duck.png'))

#---------------- LASERS img ----------------#
RED_LASER = pygame.image.load(os.path.join('assets', 'player laser.png'))
GREEN_LASER = pygame.image.load(os.path.join('assets', 'player laser.png'))
BLUE_LASER = pygame.image.load(os.path.join('assets', 'player laser.png'))
YELLOW_LASER = pygame.image.load(os.path.join('assets', 'LASER YELLOW.png'))

#---------------- BG ----------------#
BG_MENU = pygame.transform.scale(pygame.image.load(os.path.join('assets', 'earth space.jpg')), (WIDTH, HEIGHT))
BG_GAME  = pygame.transform.scale(pygame.image.load(os.path.join('assets', 'space_bg.png')), (WIDTH, HEIGHT))

#---------------- SOUND ----------------#
MENU_SOUND = mixer.Sound(os.path.join('sounds', '8bit-music-for-game-68698.mp3'))
BG_SOUND = mixer.Sound(os.path.join('sounds', 'background.wav'))
LASER_SOUND = mixer.Sound(os.path.join('sounds', 'laser.wav'))
EXPLOSION_SOUND = mixer.Sound(os.path.join('sounds', '8-bit-explosion1wav-14656.mp3'))
GAMEOVER_SOUND = mixer.Sound(os.path.join('sounds', 'mixkit-retro-arcade-game-over-470.wav'))
PAUSED_SOUND = mixer.Sound(os.path.join('sounds', 'attack-jingle-sound-effect-jvanko-125083.mp3'))
PRESS_SOUND = mixer.Sound(os.path.join('sounds', 'attack-jingle-sound-effect-jvanko-125083.mp3'))
HEAL_SOUND = mixer.Sound(os.path.join('sounds', 'Healing-SE.mp3'))
LEVEL_UP_SOUND = mixer.Sound(os.path.join('sounds', 'level-up.wav'))
BOSS_DUCK_SOUND = mixer.Sound(os.path.join('sounds', 'boss-duck.wav'))
BOSS_DUCK_DEAD_SOUND = mixer.Sound(os.path.join('sounds', 'boss-duck-dead.mp3'))

#---------------- SET VOLUME SOUND ----------------#
MENU_SOUND.set_volume(0.1)
BG_SOUND.set_volume(0.1)
LASER_SOUND.set_volume(0.1)
EXPLOSION_SOUND.set_volume(0.05)
GAMEOVER_SOUND.set_volume(0.1)
PAUSED_SOUND.set_volume(0.1)
PRESS_SOUND.set_volume(0.1)
HEAL_SOUND.set_volume(0.1)
LEVEL_UP_SOUND.set_volume(0.1)
BOSS_DUCK_SOUND.set_volume(0.08)
BOSS_DUCK_DEAD_SOUND.set_volume(0.6)

#---------------- ALL CLASS setting ----------------#
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
        return not(self.y <= height and self.y >= 0)
    
    def collision(self, obj):
        return collide(self, obj)

class Ship: 
    COOLDOWN = 30   #ความเร็วคูลดาวlaser

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
                obj.health -= 10        #HP ลด
                EXPLOSION_SOUND.play()  #เสียงตอนโดนยิง
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
    COOLDOWN = 25   #cooldown laser ของ player
    def __init__(self, x, y, health=100):
        super().__init__(x, y, health)
        self.ship_img = YELLOW_SPACE_SHIP
        self.laser_img = YELLOW_LASER
        self.mask = pygame.mask.from_surface(self.ship_img)
        self.max_health = health

    def move_lasers(self, player_laser_vel, objs):
        self.cooldown()
        for laser in self.lasers:
            laser.move(player_laser_vel)
            if laser.off_screen(HEIGHT):
                self.lasers.remove(laser)
                EXPLOSION_SOUND.play()      #เสียงตอนยิงโดน
            else:
                for obj in objs:
                    if laser.collision(obj):
                        obj.health -= 10    #ทำให้obj นั้น HP -10
                        if obj.health == 0:
                            objs.remove(obj)    #ทำให้obj นั้นหายไป
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

    def __init__(self, x, y, color, health=10):
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

class Enemy_V2(Ship):
    COLOER_MAP = {
                'red': (RED_SPACE_SHIP, RED_LASER),
                'green': (GREEN_SPACE_SHIP, GREEN_LASER),
                'blue': (BLUE_SPACE_SHIP, BLUE_LASER)
                }

    def __init__(self, x, y, color, health=10):
        super().__init__(x, y, health)
        self.ship_img, self.laser_img = self.COLOER_MAP[color]
        self.mask = pygame.mask.from_surface(self.ship_img)
        self.move_counter = 1
        self.move_direction = 1


    def move(self, vel):
        if self.y < 80:
            self.y += vel
        if self.y > 80:
            self.x += vel * self.move_counter
            if self.x > 650:
                self.move_counter = -1
            elif self.x < -50:
                self.move_counter = 1

    def shoot(self):
        if self.cool_down_counter == 0:
            laser = Laser(self.x+35, self.y, self.laser_img)
            self.lasers.append(laser)
            self.cool_down_counter = 1


class Boss(Ship):
    def __init__(self, x, y, health=300):
        super().__init__(x, y, health)
        self.ship_img = DUCK
        self.laser_img = RED_LASER
        self.max_health = health
        self.mask = pygame.mask.from_surface(self.ship_img)
        self.move_counter = 1
        self.move_direction = 1
    
    def move(self, vel):
        if self.y < 80:
            self.y += vel
        if self.y > 80:
            self.x += vel * self.move_counter
            if self.x > 650:
                self.move_counter = -1
            elif self.x < -50:
                self.move_counter = 1


    def shoot(self):
        if self.cool_down_counter == 0:
            laser = Laser(self.x+125, self.y+100, self.laser_img)
            self.lasers.append(laser)
            self.cool_down_counter = 1

    def draw(self, window):
        super().draw(window)
        self.healthbar(window)      #health bar

    def healthbar(self, window):
        pygame.draw.rect(window, (255,0,0), (self.x, self.y + self.ship_img.get_height() + 10, self.ship_img.get_width(), 10))
        pygame.draw.rect(window, (0,255,0), (self.x, self.y + self.ship_img.get_height() + 10, self.ship_img.get_width() * (self.health/self.max_health), 10))

class Heal_Hp(Ship):
    HEAL = {'heart': (HEALING_HEART)}

    def __init__(self, x, y, color, health=100):
        super().__init__(x, y, health)
        self.ship_img = self.HEAL[color]
        self.mask = pygame.mask.from_surface(self.ship_img)

    def move(self, vel):
        self.y += vel

class Heal_Live(Ship): #หัวใจสีทอง
    HEAL = {'heart': (GOLDEN_HEALING_HEART)}

    def __init__(self, x, y, color, health=100):
        super().__init__(x, y, health)
        self.ship_img = self.HEAL[color]
        self.mask = pygame.mask.from_surface(self.ship_img)

    def move(self, vel):
        self.y += vel

#---------------- HITBOX ----------------#
def collide(obj1, obj2):
    offset_x = obj2.x - obj1.x
    offset_y = obj2.y - obj1.y
    return obj1.mask.overlap(obj2.mask, (offset_x, offset_y)) != None


#---------------- func paused หยุดเกมชั่วขณะ ----------------#
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

    #TEXT WHILE PAUSED
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


#---------------- MAIN ----------------#
def main():
    run = True
    FPS = 60
    level = 0
    lives = 5

    score = 0
    main_font = pygame.font.Font('Retro Gaming.ttf', 45)
    lost_font = pygame.font.Font('Retro Gaming.ttf', 60)

    golden_healing_potion = []
    healing_potion = []
    heal_vel = 2

    boss_laser_vel = 5
    boss_vel = 3
    boss_spawn = 0
    bosses = []


    wave_length = 5
    enemy_laser_vel = 4

    enemies = []
    enemy_vel = 1

    player_laser_vel = 3 + (level/2)    #ความเร็วของlaser player เพิ่มตามlevel
    player_vel = 10 #ทุกครั้งที่กดplayerจะขยับ [เลข] pixels
    player = Player(400, 600)   #ตำแหน่งของ player ตอนเกิด


    clock = pygame.time.Clock()
    lost = False
    lost_count = 0

#---------------- REDRAW WINDOW ----------------#
    def redraw_window():    #redraw img ทุกอย่าง
        WIN.blit(BG_GAME, (0, 0))

    #DRAW TEXT
        lives_label = main_font.render(f'LIVES: {lives}', 1, (255, 255, 255))   #(r,g,b)
        level_label = main_font.render(f'LEVEL: {level}', 1, (255, 255, 255))
        score_label = main_font.render(f'SCORE: {score}', 1, (255, 255, 255))

        WIN.blit(lives_label, (10, 50))
        WIN.blit(score_label, (10, 10))
        WIN.blit(level_label, (WIDTH - level_label.get_width() - 10, 10))

        for heal in healing_potion:
            heal.draw(WIN)

        for boss_items in bosses:
            boss_items.draw(WIN)

        for enemy in enemies:
            enemy.draw(WIN)
        
        for golden_heal in golden_healing_potion:
            golden_heal.draw(WIN)

        player.draw(WIN)

        if lost:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:   # กดX ออกเกม
                    pygame.quit()
                    quit()
                if event.type == pygame.KEYDOWN:
                    PRESS_SOUND.play()
                    if event.key == pygame.K_r:   #Pres R to restart the game
                        main_menu()
                    elif event.key == pygame.K_q:   #Press Q to exit
                        pygame.quit()
                        quit()
            lost_label = lost_font.render('GAME OVER!!', 1, (255, 255, 255))
            WIN.blit(lost_label, (WIDTH/2 - lost_label.get_width()/2, 300))
            score_label = lost_font.render('YOUR SCORE %d'%score, 1, (255, 255, 255))
            WIN.blit(score_label, (WIDTH/2 - score_label.get_width()/2, 375))
            BG_SOUND.stop()
            GAMEOVER_SOUND.play()
            BOSS_DUCK_SOUND.stop()

            title_font = pygame.font.Font('Retro Gaming.ttf', 20)
            title_label = title_font.render("Press [R] to Restart, [Q] to Exit", 1, (255, 255, 0))
            WIN.blit(title_label, (WIDTH/2 - title_label.get_width()/2, 600))

        pygame.display.update()

# ---------------- RUN GAME ----------------#
    while run:
        clock.tick(FPS)
        redraw_window()

        if lives <= 0 or player.health <= 0:
            lost = True
            lost_count += 1
        
        if lost:
            if lost_count > FPS * 10:    #ขึ้นGAME OVER นาน FPS * 10 แล้วจะให้เริ่มเกมใหม่ทันที
                run = False
            else:
                continue

        if len(enemies) == 0 and boss_spawn == 0 or boss_spawn >= 1 and boss_items.health <= 0: #เพิ่มlevelทุกครั้งที่กำจัดenemiesหมด หรือ กำจัดบอส
            level += 1
            LEVEL_UP_SOUND.play()

        if boss_spawn >= 1 and boss_items.health <= 0:
            BOSS_DUCK_SOUND.stop()
            BOSS_DUCK_DEAD_SOUND.play()


    #SCORE
        if len(enemies) == 0:
            if level > 1:
                score += 500

        #HEAL
            if level%2 == 0:    #ปล่อยHeal ทุกๆ 2 level 
                for _ in range(level//2): #เพิ่มHeal 1 อัน ทุกรอบที่ปล่อย Heal
                    heal = Heal_Hp(random.randrange(50, WIDTH-100), random.randrange(-1500*level/5, -100), random.choice(['heart']))
                    healing_potion.append(heal)

        #ENEMIES SPAWN
            wave_length += 3    #เพิ่มenemy 5 ตัว ทุกๆเลเวล
            if level%3 == 0:
                # EXCLUSIVE ระดับ 1
                for _ in range(wave_length):
                    strong_enemy = Enemy(random.randrange(50, WIDTH-100), random.randrange(-1500*level/5, -100), random.choice(['red', 'blue', 'green']))
                    enemies.append(strong_enemy)
                for _ in range(2):
                    strong_enemy = Enemy(random.randrange(50, WIDTH-100), random.randrange(-1500*level/5, -100), random.choice(['blue']))
                    enemies.append(strong_enemy)
                # ปล่อยหัวใจสีทอง
                golden_heal = Heal_Live(random.randrange(50, WIDTH-100), random.randrange(-1500*level/5, -100), random.choice(['heart']))
                golden_healing_potion.append(golden_heal)
            elif level%4 == 0:
                # EXCLUSIVE ระดับ 2
                for _ in range(wave_length - 5):
                    strong_enemy = Enemy(random.randrange(50, WIDTH-100), random.randrange(-1500*level/5, -100), random.choice(['red', 'blue', 'green']))
                    enemies.append(strong_enemy)
                for _ in range(5):
                    strong_enemy = Enemy_V2(random.randrange(50, WIDTH-100), random.randrange(-1500*level/5, -100), random.choice(['red', 'blue', 'green']))
                    enemies.append(strong_enemy)
            else:
                for _ in range(wave_length):
                    enemy = Enemy(random.randrange(50, WIDTH-100), random.randrange(-1500*level/5, -100), random.choice(['red', 'blue', 'green']))
                    enemies.append(enemy)

    #BOSS SPAWN
        if level %5 == 0 and boss_spawn == 0:   #ทุกๆ 5 เลเวล จะมี Boss
            boss_spawn += 1
            boss_items = Boss(350, -200)
            bosses.append(boss_items)
            BOSS_DUCK_SOUND.play(-1)
            for _ in range(5): # Drop Heal ก่อนเจอบอส
                    heal = Heal_Hp(random.randrange(50, WIDTH-100), random.randrange(-1500*level/5, -100), random.choice(['heart']))
                    healing_potion.append(heal)
        # if boss_spawn >= 1:     #ในกรณีมีบอส และเลือดบอส <= 0 level += 1
        #     if boss_items.health <= 0:
        #         level += 1

        if level %5 != 0:
            boss_spawn = 0

    #PLAYER EVENT
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
        if keys[pygame.K_s] and player.y + player_vel + player.get_height() + 30 < HEIGHT: #down
            player.y += player_vel
        if keys[pygame.K_SPACE]:    #ยิงlaser
            LASER_SOUND.play()
            player.shoot()
        if keys[pygame.K_ESCAPE]:   #Paused
            BG_SOUND.stop()
            pause()

    #BOSS EVENT
        for boss in bosses[:]:
            boss.move(boss_vel)
            boss.move_lasers(boss_laser_vel, player)

            if random.randrange(0, 60) == 1:
                LASER_SOUND.play()
                boss.shoot()

            if collide(boss, player):
                EXPLOSION_SOUND.play()
                player.health -= 20
        player.move_lasers(-player_laser_vel, bosses)

    #ENEMIES EVENT
        for enemy in enemies[:]:
            enemy.move(enemy_vel + (level/10))  #ความเร็วของenemy ทุกๆ level เพิ่มความเร็ว + level/10
            enemy.move_lasers(enemy_laser_vel, player)

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

        player.move_lasers(-player_laser_vel, enemies)

    #HEALING EVENT
        for heal in healing_potion[:]:
            heal.move(heal_vel)
            if collide(heal, player):
                HEAL_SOUND.play()
                if player.health < 100:
                    player.health += 30
                    if player.health > 100:
                        player.health = 100
                healing_potion.remove(heal)
        for heal in golden_healing_potion[:]:
            heal.move(lives)
            if collide(golden_heal, player):
                HEAL_SOUND.play()
                if lives < 5:
                    lives += 1
                golden_healing_potion.remove(heal)

#---------------- MAIN MENU ----------------#
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
