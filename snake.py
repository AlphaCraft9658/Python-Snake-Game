import pygame
from pygame.locals import *
from time import time, sleep
from random import randint
from typing import Union

pygame.mixer.pre_init(44100, -16, 2, 1024)
pygame.init()

screen = pygame.display.set_mode((500, 500))
pygame.display.set_caption("pySnake!")
pygame.display.set_icon(pygame.image.load("img/icon.png"))

# pygame.mixer.music.load("aud/music/back_music.wav")
# pygame.mixer.music.set_volume(.5)
# pygame.mixer.music.play(-1)
sound_left = pygame.mixer.Sound("aud/sounds/left.wav")
sound_right = pygame.mixer.Sound("aud/sounds/right.wav")
sound_die = pygame.mixer.Sound("aud/sounds/die2.wav")
sound_eat = pygame.mixer.Sound("aud/sounds/eat.wav")

clock = pygame.time.Clock()
screen_rect = screen.get_rect()

font = pygame.font.Font("fonts/DisposableDroidBB_bld.ttf", 42)
score_font = pygame.font.Font("fonts/DisposableDroidBB_bld.ttf", 32)
live_score_font = pygame.font.Font("fonts/DisposableDroidBB_bld.ttf", 54)
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
live_hs_text = score_font.render("0", True, (0, 0, 0))
live_hs_rect = live_hs_text.get_rect()
live_hs_rect.y = 45

play_death_animation = False
d_a_i = 0
d_a_s = pygame.Surface((500, 500))

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
        self.double_time = 0
        self.saved_key_pattern = None

        self.b_styles = ((0, 4, 20, 12), (4, 0, 12, 20), (0, 4, 20, 12), (4, 0, 12, 20))
        self.b_styles_c = (((4, 4), (20, 4), (20, 15), (15, 15), (15, 20), (4, 20)),
                           ((0, 4), (15, 4), (15, 20), (4, 20), (4, 15), (0, 15)),
                           ((0, 4), (4, 4), (4, 0), (15, 0), (15, 15), (0, 15)),
                           ((4, 0), (15, 0), (15, 4), (20, 4), (20, 15), (4, 15)))
        self.e_styles = ((0, 4, 16, 12), (4, 0, 12, 16), (4, 4, 16, 12), (4, 4, 12, 16))

    def reset(self):
        self.head = [11, 11]
        self.length = 0
        self.saved_time = time()
        self.direction = 0
        self.key_pattern = []
        self.body = []
        self.wait_for_appending = False

    def move(self):
        global started, game_lost, fade_direction, high_score, score_text, score_text_rect, hs_text, hs_text_rect, play_death_animation
        if self.saved_key_pattern != self.key_pattern:
            self.double_time = 0
        if (time() - self.saved_time >= self.tbs and self.double_time == 0) or (time() - self.saved_time >= .5 and self.double_time == 1):
            self.saved_key_pattern = self.key_pattern.copy()
            if self.double_time == 1 and not self.check_for_self_collide():
                self.double_time = 0
            if self.check_for_self_collide() and self.double_time == 0:
                self.double_time = 1
                return
            elif self.check_for_self_collide() and self.double_time == 1:
                game_lost = True
                started = False
                fade_direction = 0
                start_text.set_alpha(0)
                game_lost = True
                play_death_animation = True
                sound_die.play()

            if not game_lost:
                if len(self.key_pattern) > 0:
                    self.direction = self.key_pattern[0]
                    self.key_pattern.pop(0)

                if self.wait_for_appending and len(self.body) > 0:
                    self.body.append(self.body[-1])
                    self.wait_for_appending = False

                if len(self.body) > 0:
                    self.body.insert(0,
                                     (self.directions[self.direction][0] * -1, self.directions[self.direction][1] * -1))
                    self.body.pop(-1)

                if self.head[0] == 0 and self.direction == 2:
                    self.head[0] = 24
                elif self.head[0] == 24 and self.direction == 0:
                    self.head[0] = 0
                else:
                    self.head[0] += self.directions[self.direction][0]

                if self.head[1] == 0 and self.direction == 3:
                    self.head[1] = 24
                elif self.head[1] == 24 and self.direction == 1:
                    self.head[1] = 0
                else:
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
        corner = pygame.Surface((20, 20))
        corner.set_colorkey((0, 0, 0))
        tile_dir = None
        if len(self.body) == 0:
            pygame.draw.rect(surface, (255, 219, 5), (self.head[0] * 20 + 4, self.head[1] * 20 + 4, 12, 12))
        else:
            pygame.draw.rect(surface, (255, 219, 5), (self.head[0] * 20 + self.e_styles[self.direction][0], self.head[1] * 20 + self.e_styles[self.direction][1], self.e_styles[self.direction][2], self.e_styles[self.direction][3]))
        self.cursor = self.head.copy()
        for v_i, v in enumerate(self.body):
            if self.cursor[0] == 0 and v[0] == -1:
                self.cursor[0] = 24
            elif self.cursor[0] == 24 and v[0] == 1:
                self.cursor[0] = 0
            else:
                self.cursor[0] += v[0]

            if self.cursor[1] == 0 and v[1] == -1:
                self.cursor[1] = 24
            elif self.cursor[1] == 24 and v[1] == 1:
                self.cursor[1] = 0
            else:
                self.cursor[1] += v[1]

            tile_dir = self.directions.index((v[0] * -1, v[1] * -1))
            if v_i == len(self.body) - 1:
                pygame.draw.rect(surface, (255, 219, 5), (self.cursor[0] * 20 + self.e_styles[tile_dir - 2][0],
                                                          self.cursor[1] * 20 + self.e_styles[tile_dir - 2][1],
                                                          self.e_styles[tile_dir - 2][2],
                                                          self.e_styles[tile_dir - 2][3]))
            elif v_i < len(self.body) - 1:
                if self.body[v_i + 1] != v:
                    corner.fill((0, 0, 0))
                    if (tile_dir == 1 and self.directions.index((self.body[v_i + 1][0] * -1, self.body[v_i + 1][1] * -1)) == 2) or (tile_dir == 0 and self.directions.index((self.body[v_i + 1][0] * -1, self.body[v_i + 1][1] * -1)) == 3):
                        pygame.draw.polygon(corner, (255, 219, 5), self.b_styles_c[0])
                    elif (tile_dir == 1 and self.directions.index((self.body[v_i + 1][0] * -1, self.body[v_i + 1][1] * -1)) == 0) or (tile_dir == 2 and self.directions.index((self.body[v_i + 1][0] * -1, self.body[v_i + 1][1] * -1)) == 3):
                        pygame.draw.polygon(corner, (255, 219, 5), self.b_styles_c[1])
                    elif (tile_dir == 3 and self.directions.index((self.body[v_i + 1][0] * -1, self.body[v_i + 1][1] * -1)) == 0) or (tile_dir == 2 and self.directions.index((self.body[v_i + 1][0] * -1, self.body[v_i + 1][1] * -1)) == 1):
                        pygame.draw.polygon(corner, (255, 219, 5), self.b_styles_c[2])
                    elif (tile_dir == 0 and self.directions.index((self.body[v_i + 1][0] * -1, self.body[v_i + 1][1] * -1)) == 1) or (tile_dir == 3 and self.directions.index((self.body[v_i + 1][0] * -1, self.body[v_i + 1][1] * -1)) == 2):
                        pygame.draw.polygon(corner, (255, 219, 5), self.b_styles_c[3])
                    surface.blit(corner, (self.cursor[0] * 20, self.cursor[1] * 20))
                else:
                    pygame.draw.rect(surface, (255, 219, 5), (self.cursor[0] * 20 + self.b_styles[tile_dir][0], self.cursor[1] * 20 + self.b_styles[tile_dir][1], self.b_styles[tile_dir][2], self.b_styles[tile_dir][3]))
            else:
                pygame.draw.rect(surface, (255, 219, 5), (self.cursor[0] * 20 + self.b_styles[tile_dir][0], self.cursor[1] * 20 + self.b_styles[tile_dir][1], self.b_styles[tile_dir][2], self.b_styles[tile_dir][3]))

    def handle_input(self, event: Union[pygame.event.Event] = None):
        if event:
            if event.type == KEYDOWN:
                if len(self.key_pattern) <= 6:
                    if len(self.key_pattern) > 0:
                        if event.key == K_RIGHT:
                            if 0 != self.key_pattern[-1] != 2:
                                self.key_pattern.append(0)
                                self.time_since_click_start = None
                                if self.key_pattern[-2] == 3:
                                    sound_right.play()
                                else:
                                    sound_left.play()
                        if event.key == K_LEFT:
                            if 2 != self.key_pattern[-1] != 0:
                                self.key_pattern.append(2)
                                self.time_since_click_start = None
                                if self.key_pattern[-2] == 1:
                                    sound_right.play()
                                else:
                                    sound_left.play()
                        if event.key == K_UP:
                            if 3 != self.key_pattern[-1] != 1:
                                self.key_pattern.append(3)
                                self.time_since_click_start = None
                                if self.key_pattern[-2] == 2:
                                    sound_right.play()
                                else:
                                    sound_left.play()
                        if event.key == K_DOWN:
                            if 1 != self.key_pattern[-1] != 3:
                                self.key_pattern.append(1)
                                self.time_since_click_start = None
                                if self.key_pattern[-2] == 0:
                                    sound_right.play()
                                else:
                                    sound_left.play()
                    else:
                        if event.key == K_RIGHT:
                            if 0 != self.direction != 2:
                                self.key_pattern.append(0)
                                self.time_since_click_start = None
                                if self.direction == 3:
                                    sound_right.play()
                                else:
                                    sound_left.play()
                        if event.key == K_LEFT:
                            if 2 != self.direction != 0:
                                self.key_pattern.append(2)
                                self.time_since_click_start = None
                                if self.direction == 1:
                                    sound_right.play()
                                else:
                                    sound_left.play()
                        if event.key == K_UP:
                            if 3 != self.direction != 1:
                                self.key_pattern.append(3)
                                self.time_since_click_start = None
                                if self.direction == 2:
                                    sound_right.play()
                                else:
                                    sound_left.play()
                        if event.key == K_DOWN:
                            if 1 != self.direction != 3:
                                self.key_pattern.append(1)
                                self.time_since_click_start = None
                                if self.direction == 0:
                                    sound_right.play()
                                else:
                                    sound_left.play()

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
            food.create_particles()
            food.randomize_position()
            self.length += 1
            self.wait_for_appending = True
            sound_eat.play()

    def snake_collides_with(self, grid_pos: tuple):
        if grid_pos == tuple(self.head):
            return True
        else:
            self.cursor = self.head.copy()
            for tile in self.body:
                if self.cursor[0] == 0 and tile[0] == -1:
                    self.cursor[0] = 24
                elif self.cursor[0] == 24 and tile[0] == 1:
                    self.cursor[0] = 0
                else:
                    self.cursor[0] += tile[0]

                if self.cursor[1] == 0 and tile[1] == -1:
                    self.cursor[1] = 24
                elif self.cursor[1] == 24 and tile[1] == 1:
                    self.cursor[1] = 0
                else:
                    self.cursor[1] += tile[1]

                if tuple(self.cursor) == grid_pos:
                    return True
        return False

    def check_for_self_collide(self):
        global high_score, score_text, score_text_rect, hs_text, hs_text_rect
        self.self_collide_check_cursor = self.head.copy()
        for index, tile in enumerate(self.body):
            if index != len(self.body) - 1:
                if self.self_collide_check_cursor[0] == 0 and tile[0] == -1:
                    self.self_collide_check_cursor[0] = 24
                elif self.self_collide_check_cursor == 24 and tile[0] == 1:
                    self.self_collide_check_cursor[0] = 0
                else:
                    self.self_collide_check_cursor[0] += tile[0]

                if self.self_collide_check_cursor[1] == 0 and tile[1] == -1:
                    self.self_collide_check_cursor[1] = 24
                elif self.self_collide_check_cursor[1] == 24 and tile[1] == 1:
                    self.self_collide_check_cursor[1] = 0
                else:
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
        self.particles = []

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

    def create_particles(self):
        abs_pos = [self.grid_pos[0] * 20, self.grid_pos[1] * 20]
        for par_c in range(25):
            self.particles.append([[*abs_pos, 6, 6], pygame.Vector2(randint(100, 500) / 100, 0).rotate(randint(0, 360)), 0])


def change_text_transparency():
    global start_text, fade_direction
    if fade_direction == 0 and start_text.get_alpha() < 255:
        start_text.set_alpha(start_text.get_alpha() + 15 * dt)
    elif fade_direction == 1 and start_text.get_alpha() > 0:
        start_text.set_alpha(start_text.get_alpha() - 15 * dt)
    if fade_direction == 0 and start_text.get_alpha() == 255:
        fade_direction = 1
    elif fade_direction == 1 and start_text.get_alpha() == 0:
        fade_direction = 0


def draw_score():
    global high_score, live_hs_text, live_hs_rect
    if snake.length < 2:
        score = live_score_font.render("0", True, (0, 0, 0))
    else:
        score = live_score_font.render(f"{snake.length - 2}", True, (0, 0, 0))

    live_hs_text = score_font.render(f"{high_score}", True, (0, 0, 0))
    live_hs_rect = live_hs_text.get_rect()
    live_hs_rect.centerx = screen_rect.centerx
    live_hs_rect.y = 45

    score_rect = score.get_rect()
    score_rect.centerx = screen_rect.centerx
    screen.blit(score, score_rect)
    screen.blit(live_hs_text, live_hs_rect)


snake = Snake()
snake.reset()
food = Food()
run = True
last_frame = time()
dt = 0  # DeltaTime for framerate independency
while run:
    dt = (time() - last_frame) * 60
    last_frame = time()

    for event in pygame.event.get():
        if event.type == QUIT:
            change_score_data(snake)
            run = False
        if event.type == KEYDOWN:
            if event.key == K_ESCAPE:
                change_score_data(snake)
                if started:
                    started = False
                    game_lost = True
                    fade_direction = 0
                    start_text.set_alpha(0)
                    snake.key_pattern.clear()
                else:
                    run = False
            if event.key == K_SPACE:
                if not started and not play_death_animation:
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

    if not started and not play_death_animation:
        screen.blit(score_text, score_text_rect)
        screen.blit(hs_text, hs_text_rect)
        screen.blit(start_text, start_text_rect)
        change_text_transparency()

    if started or play_death_animation:
        snake.food_collision()
        if not game_lost or play_death_animation:
            food.draw(screen)
            if not play_death_animation:
                snake.move()
            snake.draw(screen)
            draw_score()
            if snake.length > 1 and not play_death_animation:
                snake.tbs = .25 - (snake.length - 2) * .01
                if snake.tbs < .1:
                    snake.tbs = .1

    if play_death_animation:
        if d_a_i == 0:
            d_a_i = 75
        d_a_s = screen.copy()
        screen.fill((0, 0, 0))
        screen.blit(d_a_s, (randint(-d_a_i // 2, d_a_i // 2), randint(-d_a_i // 2, d_a_i // 2)))
        d_a_i -= 1
        if d_a_i == 1:
            d_a_i = 0
            play_death_animation = False

    if food.particles:
        for particle_index, particle in reversed(list(enumerate(food.particles))):
            particle[0][0] += particle[1][0]
            particle[0][1] += particle[1][1]
            pygame.draw.rect(screen, (255, 0, 0), (particle[0][0] - particle[0][2] / 2, particle[0][1] - particle[0][3], particle[0][2], particle[0][3]))
            particle[2] += 1
            particle[1][0] *= 0.9 * dt
            particle[1][1] *= 0.9 * dt
            if particle[2] >= 30:
                particle[0][2] -= .25 * dt
                particle[0][3] -= .25 * dt
            if particle[2] >= 54:
                food.particles.pop(particle_index)
                continue
        # print(food.particles)

    if not run:
        screen.fill((0, 0, 0))

    pygame.display.update()
    clock.tick(60)
pygame.quit()
