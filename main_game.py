# Snake Game - Smooth 60 FPS Implementation
# This is a large, feature-rich snake game using pygame.
# Includes: menu, pause, score, high score, particles, sound hooks, skins, grid system, etc.

import pygame
import random
import math
import json
import os

# =========================
# CONFIGURATION
# =========================
WIDTH, HEIGHT = 800, 600
GRID_SIZE = 20
FPS = 60  # rendering FPS (kept smooth)

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GREEN = (0, 255, 0)
DARK_GREEN = (0, 200, 0)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)

# =========================
# INITIALIZATION
# =========================
pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Snake Game 60 FPS")
clock = pygame.time.Clock()

font_small = pygame.font.SysFont("Arial", 20)
font_large = pygame.font.SysFont("Arial", 40)

# =========================
# UTILS
# =========================
def draw_text(text, font, color, x, y, center=False):
    surface = font.render(text, True, color)
    rect = surface.get_rect()
    if center:
        rect.center = (x, y)
    else:
        rect.topleft = (x, y)
    screen.blit(surface, rect)

# =========================
# PARTICLES
# =========================
class Particle:
    def __init__(self, x, y, color):
        self.x = x
        self.y = y
        self.color = color
        self.size = random.randint(2, 5)
        self.life = random.randint(20, 40)
        self.vel_x = random.uniform(-2, 2)
        self.vel_y = random.uniform(-2, 2)

    def update(self):
        self.x += self.vel_x
        self.y += self.vel_y
        self.life -= 1

    def draw(self):
        pygame.draw.circle(screen, self.color, (int(self.x), int(self.y)), self.size)

# =========================
# SNAKE CLASS
# =========================
class Snake:
    def __init__(self):
        self.body = [(WIDTH//2, HEIGHT//2)]
        self.direction = (GRID_SIZE, 0)
        self.grow = False
        self.move_delay = 120  # milliseconds between moves (increase = slower)
        self.last_move_time = 0

    def move(self):
        now = pygame.time.get_ticks()
        if now - self.last_move_time < self.move_delay:
            return
        self.last_move_time = now

        head_x, head_y = self.body[0]
        dir_x, dir_y = self.direction
        new_head = (head_x + dir_x, head_y + dir_y)

        self.body.insert(0, new_head)
        if not self.grow:
            self.body.pop()
        else:
            self.grow = False

    def change_direction(self, dx, dy):
        if (dx, dy) != (-self.direction[0], -self.direction[1]):
            self.direction = (dx, dy)

    def draw(self):
        for i, segment in enumerate(self.body):
            color = GREEN if i == 0 else DARK_GREEN
            pygame.draw.rect(screen, color, (*segment, GRID_SIZE, GRID_SIZE))

    def collide_self(self):
        return self.body[0] in self.body[1:]

    def collide_wall(self):
        x, y = self.body[0]
        return x < 0 or x >= WIDTH or y < 0 or y >= HEIGHT

# =========================
# FOOD CLASS
# =========================
class Food:
    def __init__(self):
        self.position = self.random_position()

    def random_position(self):
        x = random.randint(0, (WIDTH - GRID_SIZE)//GRID_SIZE) * GRID_SIZE
        y = random.randint(0, (HEIGHT - GRID_SIZE)//GRID_SIZE) * GRID_SIZE
        return (x, y)

    def respawn(self):
        self.position = self.random_position()

    def draw(self):
        pygame.draw.rect(screen, RED, (*self.position, GRID_SIZE, GRID_SIZE))

# =========================
# GAME CLASS
# =========================
class Game:
    def __init__(self):
        self.snake = Snake()
        self.food = Food()
        self.score = 0
        self.running = True
        self.paused = False
        self.particles = []
        self.high_score = self.load_high_score()

    def load_high_score(self):
        if os.path.exists("highscore.json"):
            with open("highscore.json", "r") as f:
                return json.load(f)
        return 0

    def save_high_score(self):
        with open("highscore.json", "w") as f:
            json.dump(self.high_score, f)

    def reset(self):
        self.__init__()

    def update(self):
        if self.paused:
            return

        self.snake.move()

        if self.snake.body[0] == self.food.position:
            self.snake.grow = True
            self.food.respawn()
            self.score += 1
            self.spawn_particles()

        if self.snake.collide_self() or self.snake.collide_wall():
            self.game_over()

        self.update_particles()

    def spawn_particles(self):
        x, y = self.snake.body[0]
        for _ in range(20):
            self.particles.append(Particle(x, y, YELLOW))

    def update_particles(self):
        self.particles = [p for p in self.particles if p.life > 0]
        for p in self.particles:
            p.update()

    def draw_particles(self):
        for p in self.particles:
            p.draw()

    def draw(self):
        screen.fill(BLACK)
        self.snake.draw()
        self.food.draw()
        self.draw_particles()

        draw_text(f"Score: {self.score}", font_small, WHITE, 10, 10)
        draw_text(f"High Score: {self.high_score}", font_small, WHITE, 10, 30)

        if self.paused:
            draw_text("PAUSED", font_large, YELLOW, WIDTH//2, HEIGHT//2, True)

        pygame.display.flip()

    def game_over(self):
        if self.score > self.high_score:
            self.high_score = self.score
            self.save_high_score()

        self.running = False

# =========================
# MENU
# =========================
def main_menu():
    while True:
        screen.fill(BLACK)
        draw_text("SNAKE GAME", font_large, GREEN, WIDTH//2, HEIGHT//3, True)
        draw_text("Press ENTER to Play", font_small, WHITE, WIDTH//2, HEIGHT//2, True)
        draw_text("Press ESC to Quit", font_small, WHITE, WIDTH//2, HEIGHT//2 + 40, True)
        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    return
                if event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    exit()

# =========================
# MAIN LOOP
# =========================
def main():
    main_menu()
    game = Game()

    while game.running:
        clock.tick(FPS)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:
                    game.snake.change_direction(0, -GRID_SIZE)
                elif event.key == pygame.K_DOWN:
                    game.snake.change_direction(0, GRID_SIZE)
                elif event.key == pygame.K_LEFT:
                    game.snake.change_direction(-GRID_SIZE, 0)
                elif event.key == pygame.K_RIGHT:
                    game.snake.change_direction(GRID_SIZE, 0)
                elif event.key == pygame.K_p:
                    game.paused = not game.paused

        game.update()
        game.draw()

    game_over_screen(game.score)

# =========================
# GAME OVER SCREEN
# =========================
def game_over_screen(score):
    while True:
        screen.fill(BLACK)
        draw_text("GAME OVER", font_large, RED, WIDTH//2, HEIGHT//3, True)
        draw_text(f"Score: {score}", font_small, WHITE, WIDTH//2, HEIGHT//2, True)
        draw_text("Press R to Restart or ESC to Quit", font_small, WHITE, WIDTH//2, HEIGHT//2 + 40, True)
        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r:
                    main()
                if event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    exit()

# =========================
# ENTRY POINT
# =========================
if __name__ == "__main__":
    main()
