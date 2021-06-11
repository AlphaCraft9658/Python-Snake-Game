import pygame
from pygame.locals import *
from time import time
from random import randint
from typing import Union

pygame.init()

screen = pygame.display.set_mode((500, 500))
pygame.display.set_caption("Snake!")
pygame.display.set_icon(pygame.image.load("img/icon.png"))

pygame.mixer.music.load("aud/music/back_music.mp3")
pygame.mixer.music.set_volume(.5)
pygame.mixer.music.play(-1)

clock = pygame.time.Clock()
screen_rect = screen.get_rect()

font = pygame.font.Font("fonts/DisposableDroidBB_bld.ttf", 42)
score_font = pygame.font.Font("fonts/DisposableDroidBB_bld.ttf", 32)
start_text = font.render("Press space to start!", True, (0, 0, 0))
start_text_rect = start_text.get_rect()
start_text_rect.centerx = screen_rect.centerx
start_text.set_alpha(0)
fade_direction = 0

score_text = score_font.render("Score: 0", True, (0, 0, 0))
score_text_rect = score_text.get_rect()
score_text_rect.bottomleft = screen_rect.bottomleft
score_text_rect.x += 5
score_text_rect.y -= 5

high_score = 0

data_keys = {"!": 0, "&": 1, "$": 2, "%": 3, "§": 4, "=": 5, "?": 6, ")": 7, "(": 8, "/": 9}
data = open("data.snx", "r")
data_value = list(data.read())
for i in range(len(data_value)):
    if data_value[i] in data_keys:
        data_value[i] = data_keys[data_value[i]]
    else:
        data_value = ["0"]
        data.close()
        data = open("data.snx", "w")
        data.write("!")
        break
data_value = [str(i) for i in data_value]
data_value = "".join(data_value)

try:
    int(data_value)
except:
    data.close()
    data = open("data.snx", "w")
    data.write("!")
else:
    high_score = int(data_value)
data.close()
hs_text = score_font.render(f"High-Score: {high_score}", True, (0, 0, 0))
hs_text_rect = hs_text.get_rect()
hs_text_rect.bottomright = screen_rect.bottomright
hs_text_rect.x -= 5
hs_text_rect.y -= 5


display_grid = pygame.Surface((500, 500))
display_grid.set_colorkey((0, 0, 0))
for i in range(25):
    for n in range(25):
        pygame.draw.rect(display_grid, (0, 175, 255), (n % 2 * 20 + i * 20 + i * 20, n * 20, 20, 20))

game_lost = False
started = False


def change_score_data(self):
    global high_score, hs_text, hs_text_rect, score_text, score_text_rect
    if high_score < self.length - 2:
        high_score = self.length - 2
        hs_text = score_font.render(f"High-Score: {self.length - 2}", True, (0, 0, 0))
        hs_text_rect = hs_text.get_rect()
        hs_text_rect.bottomright = screen_rect.bottomright
        hs_text_rect.x -= 5
        hs_text_rect.y -= 5
        with open("data.snx", "w") as d:
            for i in str(high_score):
                d.write(list(data_keys.keys())[int(i)])
                print(i)
    score_text = score_font.render(f"Score: {self.length - 2}", True, (0, 0, 0))
    score_text_rect = score_text.get_rect()
    score_text_rect.bottomleft = screen_rect.bottomleft
    score_text_rect.x += 5
    score_text_rect.y -= 5


class Snake:
    def __init__(self):
        self.LEFT = -1, 0
        self.RIGHT = 1, 0
        self.UP = 0, -1
        self.DOWN = 0, 1
        self.directions = self.RIGHT, self.DOWN, self.LEFT, self.UP
        self.direction = 0
        self.head = [11, 11]
        self.cursor = self.head.copy()
        self.self_collide_check_cursor = self.head.copy()
        self.body = []
        self.tbs = .25
        self.saved_time = time()
        self.length = 0
        self.key_pattern = []
        self.wait_for_appending = False
        self.time_since_click_start = None

    def reset(self):
        self.head = [11, 11]
        self.length = 0
        self.saved_time = time()
        self.direction = 0
        self.key_pattern = []
        self.body = []
        self.wait_for_appending = False

    def move(self):
        global started, game_lost, fade_direction, high_score, score_text, score_text_rect, hs_text, hs_text_rect
        if time() - self.saved_time > self.tbs:
            if self.check_for_self_collide():
                game_lost = True
                started = False
                fade_direction = 0
                start_text.set_alpha(0)

            if not game_lost:
                if len(self.key_pattern) > 0:
                    self.direction = self.key_pattern[0]
                    self.key_pattern.pop(0)

                if not screen_rect.contains(Rect((self.head[0] + self.directions[self.direction][0]) * 20,
                                                 (self.head[1] + self.directions[self.direction][1]) * 20, 20, 20)):
                    started = False
                    game_lost = True
                    fade_direction = 0
                    start_text.set_alpha(0)
                    self.key_pattern.clear()
                    change_score_data(self)
                    return

                if self.wait_for_appending and len(self.body) > 0:
                    self.body.append(self.body[-1])
                    self.wait_for_appending = False

                if len(self.body) > 0:
                    self.body.insert(0,
                                     (self.directions[self.direction][0] * -1, self.directions[self.direction][1] * -1))
                    self.body.pop(-1)

                self.head[0] += self.directions[self.direction][0]
                self.head[1] += self.directions[self.direction][1]

                if self.length < 2:
                    if len(self.body) > 0:
                        self.body.append((11 - (self.head[0] + self.body[-1][0]), 11 - (self.head[1] + self.body[-1][1])))
                    else:
                        self.body.append(
                            (self.directions[self.direction][0] * -1, self.directions[self.direction][1] * -1))
                    self.length += 1

                self.saved_time = time()

    def draw(self, surface):
        pygame.draw.rect(surface, (255, 219, 5), (self.head[0] * 20, self.head[1] * 20, 20, 20))
        self.cursor = self.head.copy()
        for v in self.body:
            self.cursor[0] += v[0]
            self.cursor[1] += v[1]
            pygame.draw.rect(surface, (255, 219, 5), (self.cursor[0] * 20, self.cursor[1] * 20, 20, 20))

    def handle_input(self, event: Union[pygame.event.Event] = None):
        if event:
            if event.type == KEYDOWN:
                if len(self.key_pattern) > 0:
                    if event.key == K_RIGHT:
                        if self.key_pattern[-1] != 2 != 0:
                            self.key_pattern.append(0)
                    if event.key == K_LEFT:
                        if self.key_pattern[-1] != 0 != 2:
                            self.key_pattern.append(2)
                    if event.key == K_UP:
                        if self.key_pattern[-1] != 1 != 3:
                            self.key_pattern.append(3)
                    if event.key == K_DOWN:
                        if self.key_pattern[-1] != 3 != 1:
                            self.key_pattern.append(1)
                else:
                    if event.key == K_RIGHT:
                        if self.direction != 2:
                            self.key_pattern.append(0)
                    if event.key == K_LEFT:
                        if self.direction != 0:
                            self.key_pattern.append(2)
                    if event.key == K_UP:
                        if self.direction != 1:
                            self.key_pattern.append(3)
                    if event.key == K_DOWN:
                        if self.direction != 3:
                            self.key_pattern.append(1)

        keys = pygame.key.get_pressed()
        if keys[K_RIGHT] and self.direction == 0:
            if self.time_since_click_start is None:
                self.time_since_click_start = time()
            if time() - self.time_since_click_start >= .5:
                self.tbs *= .5
        elif keys[K_DOWN] and self.direction == 1:
            if self.time_since_click_start is None:
                self.time_since_click_start = time()
            if time() - self.time_since_click_start >= .5:
                self.tbs *= .5
        elif keys[K_LEFT] and self.direction == 2:
            if self.time_since_click_start is None:
                self.time_since_click_start = time()
            if time() - self.time_since_click_start >= .5:
                self.tbs *= .5
        elif keys[K_UP] and self.direction == 3:
            if self.time_since_click_start is None:
                self.time_since_click_start = time()
            if time() - self.time_since_click_start >= .5:
                self.tbs *= .5
        elif self.time_since_click_start:
            self.time_since_click_start = None

    def food_collision(self):
        if tuple(self.head) == food.grid_pos:
            food.randomize_position()
            self.length += 1
            self.wait_for_appending = True

    def snake_collides_with(self, grid_pos: tuple):
        if grid_pos == tuple(self.head):
            return True
        else:
            self.cursor = self.head.copy()
            for tile in self.body:
                self.cursor[0] += tile[0]
                self.cursor[1] += tile[1]
                if tuple(self.cursor) == grid_pos:
                    return True
        return False

    def check_for_self_collide(self):
        global high_score, score_text, score_text_rect, hs_text, hs_text_rect
        self.self_collide_check_cursor = self.head.copy()
        for index, tile in enumerate(self.body):
            if index != len(self.body) - 1:
                self.self_collide_check_cursor[0] += tile[0]
                self.self_collide_check_cursor[1] += tile[1]
                if len(self.key_pattern) > 0:
                    if tuple(self.self_collide_check_cursor) == (self.head[0] + self.directions[self.key_pattern[0]][0],
                                                                 self.head[1] + self.directions[self.key_pattern[0]][1]):
                        change_score_data(self)
                        return True
                else:
                    if tuple(self.self_collide_check_cursor) == (self.head[0] + self.directions[self.direction][0],
                                                                 self.head[1] + self.directions[self.direction][1]):
                        change_score_data(self)
                        return True
        return False


class Food:
    def __init__(self):
        self.grid_pos = (0, 0)
        self.randomize_position()

    def randomize_position(self):
        while True:
            self.grid_pos = (randint(0, 24), randint(0, 24))
            if len(snake.key_pattern) == 0:
                if snake.snake_collides_with(self.grid_pos) or snake.snake_collides_with((self.grid_pos[0] - snake.directions[snake.direction][0], self.grid_pos[1] - snake.directions[snake.direction][1])):
                    continue
                else:
                    break
            else:
                if snake.snake_collides_with(self.grid_pos) or snake.snake_collides_with((self.grid_pos[0] - snake.directions[snake.key_pattern[0]][0], self.grid_pos[1] - snake.directions[snake.key_pattern[0]][1])):
                    continue
                else:
                    break

    def draw(self, surface):
        pygame.draw.rect(surface, (254, 1, 0), (self.grid_pos[0] * 20 + 4, self.grid_pos[1] * 20 + 4, 12, 12))


def change_text_transparency():
    global start_text, fade_direction
    if fade_direction == 0 and start_text.get_alpha() < 255:
        start_text.set_alpha(start_text.get_alpha() + 15)
    elif fade_direction == 1 and start_text.get_alpha() > 0:
        start_text.set_alpha(start_text.get_alpha() - 15)
    if fade_direction == 0 and start_text.get_alpha() == 255:
        fade_direction = 1
    elif fade_direction == 1 and start_text.get_alpha() == 0:
        fade_direction = 0


def draw_score():
    if snake.length < 2:
        score = font.render("0", True, (0, 0, 0))
    else:
        score = font.render(f"{snake.length - 2}", True, (0, 0, 0))
    score_rect = score.get_rect()
    score_rect.centerx = screen_rect.centerx
    screen.blit(score, score_rect)


snake = Snake()
snake.reset()
food = Food()
run = True
while run:
    for event in pygame.event.get():
        if event.type == QUIT or (event.type == KEYDOWN and event.key == K_ESCAPE):
            change_score_data(snake)
            run = False
        if event.type == KEYDOWN:
            if event.key == K_SPACE:
                if not started:
                    started = True
                    game_lost = False
                    snake.tbs = .25
                    snake.reset()
                    food.randomize_position()
        if started:
            snake.handle_input(event)
    snake.handle_input()

    screen.fill((0, 200, 255))
    screen.blit(display_grid, (0, 0))

    if game_lost:
        food.draw(screen)
        snake.draw(screen)

    if not started:
        screen.blit(score_text, score_text_rect)
        screen.blit(hs_text, hs_text_rect)
        screen.blit(start_text, start_text_rect)
        change_text_transparency()

    if started:
        snake.food_collision()
        if not game_lost:
            food.draw(screen)
            snake.move()
            snake.draw(screen)
            draw_score()
            if snake.length > 1:
                snake.tbs = .25 - (snake.length - 2) * .01
                if snake.tbs < .1:
                    snake.tbs = .1

    pygame.display.update()
    clock.tick(60)
pygame.quit()
