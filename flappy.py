import pygame
from pygame.locals import *
import random
import sys
import os

# init
pygame.init()
clock = pygame.time.Clock()
fps = 60

# screen
screen_width = 664
screen_height = 736
screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption('Flappy Bird')
white = (255, 255, 255)


# font
font = pygame.font.SysFont('Bauhaus 93', 60)


#sound state var
sound_on = True
current_music = None
# sound
pygame.mixer.music.set_volume(0.2)
menu_music = 'sounds/rickroll.mp3'
game_music = 'sounds/game_sound.mp3'
gameover_music = pygame.mixer.Sound('sounds/gameover_sound.mp3')

def play_music(path):
    if sound_on:  
        pygame.mixer.music.load(path)
        pygame.mixer.music.play(-1)

def stop_music():
    pygame.mixer.music.stop()

# img
bg = pygame.image.load('img/bg.png').convert()
ground_img = pygame.image.load('img/ground.png').convert_alpha()
button_img = pygame.image.load('img/newgame_btn.png').convert_alpha()
new_game_img = pygame.image.load('img/start_btn.png').convert_alpha()
exit_img = pygame.image.load('img/quit_btn.png').convert_alpha()
menu_img = pygame.image.load('img/menu_btn.png').convert_alpha()
game_over_img = pygame.image.load('img/gameover.png').convert_alpha()
game_logo_img = pygame.image.load('img/flappy_logo.png').convert_alpha()
shop_img = pygame.image.load('img/shop_btn.png').convert_alpha()
sound_on_img = pygame.image.load('img/sound_on.png').convert_alpha()
sound_off_img = pygame.image.load('img/sound_off.png').convert_alpha()

# skin
bird_skins = []
base_bird_img = pygame.image.load('img/bird1.png').convert_alpha()
base_size = base_bird_img.get_size()

skin_index = 1
while True:
    skin_path = f'img/bird{skin_index}.png'
    if not os.path.isfile(skin_path):
        break
    skin_img = pygame.image.load(skin_path).convert_alpha()
    skin_img = pygame.transform.scale(skin_img, base_size)
    bird_skins.append(skin_img)
    skin_index += 1

if len(bird_skins) == 0:
    bird_skins.append(base_bird_img)

# state var
ground_scroll = 0
scroll_speed = 4
flying = False
game_over = False
pipe_gap = 180
pipe_frequency = 1500
last_pipe = pygame.time.get_ticks() - pipe_frequency
score = 0
pass_pipe = False

selected_skin = 1


# func
def draw_center_text(text, font, color, x, y):
    img = font.render(text, True, color)
    rect = img.get_rect(center=(x, y))
    screen.blit(img, rect)

def reset_game():
    pipe_group.empty()
    global flappy
    flappy = Bird(100, screen_height // 2, selected_skin)
    bird_group.empty()
    bird_group.add(flappy)
    return 0

# class
class Bird(pygame.sprite.Sprite):
    def __init__(self, x, y, skin_index):
        super().__init__()
        self.images = [bird_skins[skin_index - 1]]
        self.index = 0
        self.counter = 0
        self.image = self.images[self.index]
        self.rect = self.image.get_rect(center=(x, y))
        self.vel = 0
        self.clicked = False

    def update(self):
        if flying:
            self.vel += 0.5
            self.vel = min(self.vel, 8)
            if self.rect.bottom < 768:
                self.rect.y += int(self.vel)

        if not game_over:
            if pygame.mouse.get_pressed()[0] == 1 and not self.clicked:
                self.clicked = True
                self.vel = -10
            if pygame.mouse.get_pressed()[0] == 0:
                self.clicked = False

            self.counter += 1
            if self.counter > 5:
                self.counter = 0
                self.index = (self.index + 1) % len(self.images)
            self.image = pygame.transform.rotate(self.images[self.index], self.vel * -2)
        else:
            self.image = pygame.transform.rotate(self.images[self.index], -90)

class Pipe(pygame.sprite.Sprite):
    def __init__(self, x, y, position):
        super().__init__()
        self.image = pygame.image.load('img/pipe.png').convert_alpha()
        self.rect = self.image.get_rect()
        if position == 1:
            self.image = pygame.transform.flip(self.image, False, True)
            self.rect.bottomleft = [x, y - pipe_gap // 2]
        else:
            self.rect.topleft = [x, y + pipe_gap // 2]

    def update(self):
        self.rect.x -= scroll_speed
        if self.rect.right < 0:
            self.kill()

class Button:
    def __init__(self, x, y, image):
        self.image = image
        self.original_image = image.copy()
        self.rect = self.image.get_rect(center=(x, y))
        self.clicked = False  # bien theo doi click 

    def draw(self):
        action = False
        pos = pygame.mouse.get_pos()

        if self.rect.collidepoint(pos):
            bright_image = pygame.Surface(self.image.get_size()).convert_alpha()
            bright_image.fill((40, 40, 40, 0))
            hover_img = self.original_image.copy()
            hover_img.blit(bright_image, (0, 0), special_flags=pygame.BLEND_RGB_ADD)
            screen.blit(hover_img, self.rect)

            if pygame.mouse.get_pressed()[0] == 1 and not self.clicked:
                action = True
                self.clicked = True
            elif pygame.mouse.get_pressed()[0] == 0:
                self.clicked = False
        else:
            screen.blit(self.image, self.rect)

        return action

# sprite group
bird_group = pygame.sprite.Group()
pipe_group = pygame.sprite.Group()
flappy = Bird(100, screen_height // 2, selected_skin)
bird_group.add(flappy)

# Buttons
restart_button = Button(screen_width // 2, screen_height // 2 + 20, button_img)
back_to_menu_button = Button(screen_width // 2, screen_height // 2 + 160, menu_img)
exit_button_gameover = Button(screen_width // 2, screen_height // 2 + 220, exit_img)
new_game_button = Button(screen_width // 2, screen_height // 2 - 70, new_game_img)
shop_button = Button(screen_width // 2, screen_height // 2 + 10, shop_img)
exit_button_mainmenu = Button(screen_width // 2, screen_height // 2 + 90, exit_img)
menu_button_gameover = Button(screen_width // 2, screen_height // 2 + 130, menu_img)
sound_button = Button(screen_width - 50, 50, sound_on_img)


# menu state var
main_menu = True
shop_menu = False

# main loop
run = True
while run:
    clock.tick(fps)
    screen.blit(bg, (0, 0))
    
    #sound btn
    sound_button.image = sound_on_img if sound_on else sound_off_img
    sound_button.original_image = sound_button.image.copy()
    if sound_button.draw():
        sound_on = not sound_on
        if sound_on:
            if main_menu or shop_menu:
                play_music(menu_music)
            else:
                play_music(game_music)
        else:
            stop_music()

    # main menu
    if main_menu and not shop_menu:
        if current_music != 'menu':
            play_music(menu_music)
            current_music = 'menu'

        screen.blit(ground_img, (0, 700))
        screen.blit(game_logo_img, game_logo_img
                    .get_rect(center=(screen_width // 2, screen_height // 2 - 200)))

        if new_game_button.draw():
            main_menu = False
            shop_menu = False
            flying = False
            game_over = False
            score = reset_game()

        if shop_button.draw():
            shop_menu = True

        if exit_button_mainmenu.draw():
            run = False

    # shop Menu
    elif shop_menu:
        if current_music != 'menu':
            play_music(menu_music)
            current_music = 'menu'

        screen.blit(ground_img, (0, 700))
        draw_center_text("Select a Bird Skin", font, white, screen_width // 2, 80)

        for i, skin in enumerate(bird_skins):
            skin_scaled = pygame.transform.scale(skin, (60, 60))
            rect = skin_scaled.get_rect(center=(150 + i * 100, 200))
            screen.blit(skin_scaled, rect)

            if rect.collidepoint(pygame.mouse.get_pos()):
                pygame.draw.rect(screen, (255, 255, 0), rect.inflate(6, 6), 3)
                if pygame.mouse.get_pressed()[0]:
                    selected_skin = i + 1
                    flappy = Bird(100, screen_height // 2, selected_skin)
                    bird_group.empty()
                    bird_group.add(flappy)

            if selected_skin == i + 1:
                pygame.draw.rect(screen, (0, 255, 0), rect.inflate(8, 8), 4)

        if back_to_menu_button.draw():
            shop_menu = False
            main_menu = True

    # game
    else:
        if current_music != 'game':
            play_music(game_music)
            current_music = 'game'

        bird_group.draw(screen)
        bird_group.update()
        pipe_group.draw(screen)
        screen.blit(ground_img, (ground_scroll, 700))

        if len(pipe_group) > 0:
            bird = bird_group.sprites()[0]
            pipe = pipe_group.sprites()[0]
            if bird.rect.left > pipe.rect.left and bird.rect.right < pipe.rect.right and not pass_pipe:
                pass_pipe = True
            if pass_pipe and bird.rect.left > pipe.rect.right:
                score += 1
                pass_pipe = False

        draw_center_text(str(score), font, white, screen_width // 2, 50)

        if pygame.sprite.groupcollide(bird_group, pipe_group, False, False) or flappy.rect.top < 0:
            if not game_over:
                stop_music()
                gameover_music.play()
            game_over = True
            current_music = None

        if flappy.rect.bottom >= 700:
            if not game_over:
                stop_music()
                gameover_music.play()
            game_over = True
            flying = False
            current_music = None

        if not game_over and flying:
            time_now = pygame.time.get_ticks()
            if time_now - last_pipe > pipe_frequency:
                pipe_height = random.randint(-100, 100)
                pipe_group.add(Pipe(screen_width, screen_height // 2 + pipe_height, -1))
                pipe_group.add(Pipe(screen_width, screen_height // 2 + pipe_height, 1))
                last_pipe = time_now

            ground_scroll -= scroll_speed
            if abs(ground_scroll) > 35:
                ground_scroll = 0

            pipe_group.update()

        if game_over:
            screen.blit(game_over_img, game_over_img.get_rect(center=(screen_width // 2, screen_height // 2 - 150)))

            if restart_button.draw():
                game_over = False
                flying = False
                score = reset_game()

            if menu_button_gameover.draw():
                game_over = False
                flying = False
                main_menu = True
                shop_menu = False

            if exit_button_gameover.draw():
                run = False

    # global events
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False
        if event.type == pygame.MOUSEBUTTONDOWN and not flying and not game_over and not main_menu:
            flying = True

    pygame.display.update()

pygame.quit()
sys.exit()