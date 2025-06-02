import pygame
from pygame.locals import *
import random
import sys

pygame.init()

clock = pygame.time.Clock()
fps = 60

# Screen setup
screen_width = 664
screen_height = 736
screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption('Flappy Bird')

# Font
font = pygame.font.SysFont('Bauhaus 93', 60)

# Colours
white = (255, 255, 255)

# Game variables
ground_scroll = 0
scroll_speed = 4
flying = False
game_over = False
pipe_gap = 150
pipe_frequency = 1500
last_pipe = pygame.time.get_ticks() - pipe_frequency
score = 0
pass_pipe = False
main_menu = True

# Load images
bg = pygame.image.load('img/bg.png')
ground_img = pygame.image.load('img/ground.png')
button_img = pygame.image.load('img/newgame_btn.png')
new_game_img = pygame.image.load('img/start_btn.png')
exit_img = pygame.image.load('img/quit_btn.png')
menu_img = pygame.image.load('img/menu_btn.png')
game_over_img = pygame.image.load('img/gameover.png')
game_logo_img =  pygame.image.load('img/flappy_logo.png')


# draw center text
def draw_center_text(text, font, color, x, y):
    img = font.render(text, True, color)
    rect = img.get_rect(center=(x, y))
    screen.blit(img, rect)

# Reset game
def reset_game():
    pipe_group.empty()
    flappy.rect.x = 100
    flappy.rect.y = int(screen_height / 2)
    return 0

# Bird class
class Bird(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.images = [pygame.image.load(f'img/bird{num}.png') for num in range(1, 4)]
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

# Pipe class
class Pipe(pygame.sprite.Sprite):
    def __init__(self, x, y, position):
        super().__init__()
        self.image = pygame.image.load('img/pipe.png')
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

# Button class with hover effect
class Button():
    def __init__(self, x, y, image):
        self.image = image
        self.original_image = image.copy()
        self.rect = self.image.get_rect(center=(x, y))

    def draw(self):
        action = False
        pos = pygame.mouse.get_pos()

        if self.rect.collidepoint(pos):
            bright_image = pygame.Surface(self.image.get_size()).convert_alpha()
            bright_image.fill((40, 40, 40, 0))
            hover_img = self.original_image.copy()
            hover_img.blit(bright_image, (0, 0), special_flags=pygame.BLEND_RGB_ADD)
            screen.blit(hover_img, self.rect)
            if pygame.mouse.get_pressed()[0] == 1:
                action = True
        else:
            screen.blit(self.image, self.rect)

        return action

# Sprite groups
bird_group = pygame.sprite.Group()
pipe_group = pygame.sprite.Group()

flappy = Bird(100, screen_height // 2)
bird_group.add(flappy)

# Buttons
restart_button = Button(screen_width // 2, screen_height // 2 + 20, button_img)
back_to_menu_button = Button(screen_width // 2, screen_height // 2 + 90, menu_img)
exit_button_gameover = Button(screen_width // 2, screen_height // 2 + 160, exit_img)
new_game_button = Button(screen_width // 2 - 80, screen_height // 2, new_game_img)
exit_button_mainmenu = Button(screen_width // 2 + 80, screen_height // 2, exit_img)

# Main loop
run = True
while run:
    clock.tick(fps)

    if main_menu:
        screen.blit(bg, (0, 0))
        screen.blit(ground_img, (0, 768))
        screen.blit(game_logo_img, game_logo_img.get_rect(center=(screen_width // 2, screen_height // 2 - 100)))

        if new_game_button.draw():
            main_menu = False
            flying = False
            game_over = False
            score = reset_game()

        if exit_button_mainmenu.draw():
            run = False

    else:
        screen.blit(bg, (0, 0))
        bird_group.draw(screen)
        bird_group.update()
        pipe_group.draw(screen)
        screen.blit(ground_img, (ground_scroll, 768))

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
            game_over = True
        if flappy.rect.bottom >= 768:
            game_over = True
            flying = False

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
                score = reset_game()

            if back_to_menu_button.draw():
                game_over = False
                flying = False
                score = reset_game()
                main_menu = True

            if exit_button_gameover.draw():
                run = False

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False
        if event.type == pygame.MOUSEBUTTONDOWN and not flying and not game_over and not main_menu:
            flying = True

    pygame.display.update()

pygame.quit()
sys.exit()
