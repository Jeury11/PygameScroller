import pygame
import os

pygame.init()


SCREEN_WIDTH = 800
SCREEN_HEIGHT = int(SCREEN_WIDTH * 0.8)

screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption('Game')

#set framerat
clock = pygame.time.Clock()
FPS = 60

#define game variables
GRAVITY = 0.75

#define player action variables
moving_left = False
moving_right = False
swing = False


#load images
#bullet
slash_img = pygame.image.load('Characters/Effects/0.png').convert_alpha()
#grenade
slash_img = pygame.image.load('Characters/Effects/0.png').convert_alpha()


#define coulers
BG = (144, 201, 120)
RED = (255, 0, 0)

def draw_bg():
    screen.fill(BG)
    pygame.draw.line(screen, RED, (0, 300), (SCREEN_WIDTH, 300))

#

class Character(pygame.sprite.Sprite):
    def __init__(self, char_type, x, y, scale, speed, ammo):
        pygame.sprite.Sprite.__init__(self)
        self.alive = True
        self.char_type = char_type
        self.speed = speed
        self.ammo = ammo
        self.start_ammo = ammo
        self.swing_cooldown = 0
        self.health = 100
        self.max_health = self.health
        self.direction = 1
        self.vel_y = 0
        self.jump = False
        self.in_air = True
        self.flip = False
        self.animation_list = []
        self.frame_index = 0
        self.action = 0
        self.update_time = pygame.time.get_ticks()

        #load all images for the players
        animation_types = ['Idle', 'Run', 'Jump', 'Death']
        for animation in animation_types:
            #reset temporary list of images
            temp_list = []
            #count number of files in the folder
            num_of_frames = len(os.listdir(f'Characters/{self.char_type}/{animation}'))
            for i in range(num_of_frames):
                img = pygame.image.load(f'Characters/{self.char_type}/{animation}/{i}.png').convert_alpha()
                img = pygame.transform.scale(img, (int(img.get_width() * scale), int(img.get_height() * scale)))
                temp_list.append(img)
            self.animation_list.append(temp_list)

            self.image = self.animation_list[self.action][self.frame_index]
            self.rect = self.image.get_rect()
            self.rect.center = (x, y)


    def update(self):
        self.update_animation()
        self.check_alive()
        #update cooldown
        if self.swing_cooldown > 0:
            self.swing_cooldown -= 1


    def move(self, moving_left, moving_right):
        #reset movement variables
        dx = 0
        dy = 0

        #assign movement variables if moving left or right
        if moving_left:
            dx = -self.speed
            self.flip = True
            self.direction = -1
        if moving_right:
            dx = self.speed
            self.flip = False
            self.direction = 1

        #jump
        if self.jump == True and self.in_air == False:
            self.vel_y = -15
            self.jump = False
            self.in_air = True

        #apply gravity
        self.vel_y += GRAVITY
        if self.vel_y > 10:
            self.vel_y
        dy += self.vel_y

        #check collision with floor
        if self.rect.bottom + dy > 300:
            dy = 300 - self.rect.bottom
            self.in_air = False

        #update rectangle position
        self.rect.x += dx
        self.rect.y += dy


    def swing(self):
        if self.swing_cooldown == 0 and self.ammo > 0:
            self.swing_cooldown = 20
            slash = Slash(self.rect.centerx + (0.99 * self.rect.size[0] * self.direction), self.rect.centery, self.direction)
            slash_group.add(slash)
            #reduce ammo
            self.ammo -= 1


    def update_animation(self):
        #update animation
        ANIMATION_COOLDOWN = 80
        #update image depending on current frame
        self.image = self.animation_list[self.action][self.frame_index]
        #check if enough time has passed since the last update
        if pygame.time.get_ticks() - self.update_time > ANIMATION_COOLDOWN:
            self.update_time = pygame.time.get_ticks()
            self.frame_index += 1
        #if the animation has run out then reset nack to the start
        if self.frame_index >= len(self.animation_list[self.action]):
            if self.action == 3:
                self.frame_index = len(self.animation_list[self.action]) - 1
            else:
                self.frame_index = 0



    def update_action(self, new_action):
        #check if the new action is different to the previous one
        if new_action != self.action:
            self.action = new_action
            #update the animation settings
            self.frame_index = 0
            self.update_time = pygame.time.get_ticks()



    def check_alive(self):
        if self.health <= 0:
            self.health = 0
            self.speed = 0
            self.alive = False
            self.update_action(3)

    def draw(self):
        screen.blit(pygame.transform.flip(self.image, self.flip, False),self.rect)




class Slash(pygame.sprite.Sprite):
    def __init__(self, x, y, direction):
        pygame.sprite.Sprite.__init__(self)
        self.speed = 10
        self.image = slash_img
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        self.direction = direction

    def update(self):
        #move slash
        self.rect.x += (self.direction * self.speed)
        #check if bullet has gone off screen
        if self.rect.right < 0 or self.rect.left > SCREEN_WIDTH:
            self.kill()

        #check collision with characters
        if pygame.sprite.spritecollide(player, slash_group, False):
            if player.alive:
                player.health -= 5
                self.kill()
        if pygame.sprite.spritecollide(enemy, slash_group, False):
            if enemy.alive:
                enemy.health -= 25
                self.kill()



class Grenade(pygame.sprite.Sprite):
    def __init__(self, x, y, direction):
        pygame.sprite.Sprite.__init__(self)
        self.timer = 100
        self.vel_y = -11
        self.speed = 7
        self.image = grenade_img
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        self.direction = direction

#create sprite groups
slash_group = pygame.sprite.Group()



player = Character('Player', 200, 200, 3, 5, 200)
enemy = Character('Enemy', 400, 200, 3, 5, 20)



run = True
while run:

    clock.tick(FPS)

    draw_bg()

    player.update()
    player.draw()

    enemy.update()
    enemy.draw()

    #update nd draw groups
    slash_group.update()
    slash_group.draw(screen)


    #update player actions
    if player.alive:
        #swing sword
        if swing:
            player.swing()
        if player.in_air:
            player.update_action(2)# 2: jump
        elif moving_left or moving_right:
            player.update_action(1)#1: run
        else:
            player.update_action(0)#0: idle
        player.move(moving_left, moving_right)


    for event in pygame.event.get():
        #quit game
        if event.type == pygame.QUIT:
            run = False
        #keyboard presses
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_a:
                moving_left = True
            if event.key == pygame.K_d:
                moving_right = True
            if event.key == pygame.K_SPACE:
                swing = True
            if event.key == pygame.K_w and player.alive:
                player.jump = True
            if event.key == pygame.K_ESCAPE:
                run = False


        #keyboard button releases
        if event.type == pygame.KEYUP:
            if event.key == pygame.K_a:
                moving_left = False
            if event.key == pygame.K_d:
                moving_right = False
            if event.key == pygame.K_SPACE:
                swing = False



    pygame.display.update()

pygame.quit()