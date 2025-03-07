import pygame
import random
import json
import os
from pygame.locals import *


class Game:
    def __init__(self, screen, level_name, scoreboard):
        self.screen = screen
        self.scoreboard = scoreboard
        self.level_name = level_name
        self.screen_width, self.screen_height = screen.get_size()
        self.load_config()
        self.load_assets()
        self.init_game_state()

    def load_config(self):
        with open("assets/config/settings.json") as f:
            self.base_settings = json.load(f)

        with open("assets/config/levels.json") as f:
            levels = json.load(f)["levels"]
            self.level_settings = next(lvl for lvl in levels if lvl["name"] == self.level_name)

    def load_assets(self):
        self.background = pygame.image.load("assets/images/background.png")
        self.background = pygame.transform.scale(self.background, (self.screen_width, self.screen_height))

        self.classmate_images = []
        classmates_dir = "assets/images/classmates"
        for filename in os.listdir(classmates_dir):
            if filename.endswith(".png"):
                image = pygame.image.load(os.path.join(classmates_dir, filename))
                self.classmate_images.append(image)

    def init_game_state(self):
        self.score = 0
        self.time_left = self.level_settings["game_time"]
        self.classmates = []
        self.bullets = []
        self.running = True
        self.gun_position = (self.screen_width // 2, self.screen_height - 50)

    def run(self):
        clock = pygame.time.Clock()
        while self.running:
            self.handle_events()
            self.update()
            self.render()
            clock.tick(60)
        self.handle_game_over()

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == QUIT:
                self.running = False
            if event.type == MOUSEBUTTONDOWN and event.button == 1:
                self.handle_shot(pygame.mouse.get_pos())

    def handle_shot(self, target_pos):
        bullet_speed = 15
        start_x, start_y = self.gun_position
        dx = target_pos[0] - start_x
        dy = target_pos[1] - start_y
        distance = max(1, (dx ** 2 + dy ** 2) ** 0.5)

        self.bullets.append({
            'pos': [start_x, start_y],
            'dx': dx / distance * bullet_speed,
            'dy': dy / distance * bullet_speed,
            'rect': pygame.Rect(start_x - 4, start_y - 4, 8, 8)
        })

    def update(self):
        for bullet in self.bullets[:]:
            bullet['pos'][0] += bullet['dx']
            bullet['pos'][1] += bullet['dy']
            bullet['rect'].center = bullet['pos']

            if not (0 < bullet['pos'][0] < self.screen_width and 0 < bullet['pos'][1] < self.screen_height):
                self.bullets.remove(bullet)
                continue

            for classmate in self.classmates[:]:
                if classmate['rect'].colliderect(bullet['rect']):
                    self.classmates.remove(classmate)
                    self.score += 10
                    self.bullets.remove(bullet)
                    break

        for classmate in self.classmates[:]:
            classmate['rect'].x += classmate['speed'] * classmate['direction']
            if classmate['rect'].x < -100 or classmate['rect'].x > self.screen_width + 100:
                self.classmates.remove(classmate)

        if (random.random() < self.level_settings["spawn_rate"] and
                len(self.classmates) < self.level_settings["max_classmates"]):
            self.spawn_classmate()

        self.time_left -= 1 / 60
        if self.time_left <= 0:
            self.running = False

    def spawn_classmate(self):
        side = random.choice(['left', 'right'])
        image = random.choice(self.classmate_images)
        speed = self.level_settings["classmate_speed"]

        new_classmate = {
            'rect': pygame.Rect(-100 if side == 'left' else self.screen_width + 100,
                                random.randint(50, self.screen_height - 50),
                                image.get_width(),
                                image.get_height()),
            'speed': speed,
            'direction': 1 if side == 'left' else -1,
            'image': image
        }
        self.classmates.append(new_classmate)

    def render(self):
        self.screen.blit(self.background, (0, 0))

        for classmate in self.classmates:
            self.screen.blit(classmate['image'], classmate['rect'])

        for bullet in self.bullets:
            pygame.draw.circle(self.screen, (255, 0, 0),
                               (int(bullet['pos'][0]), int(bullet['pos'][1])), 8)

        pygame.draw.circle(self.screen, (100, 100, 100), self.gun_position, 20)

        self.draw_ui()
        pygame.display.flip()

    def draw_ui(self):
        ui_font = pygame.font.Font(None, 36)
        texts = [
            f"Score: {self.score}",
            f"Time: {int(self.time_left)}",
            f"Level: {self.level_name}"
        ]
        for i, text in enumerate(texts):
            self.screen.blit(ui_font.render(text, True, (255, 255, 255)), (10, 10 + i * 40))

    def handle_game_over(self):
        if self.score > self.scoreboard.get_top_score():
            self.show_highscore_dialog()

    def show_highscore_dialog(self):
        player_name = "Player1"
        self.scoreboard.add_score(player_name, self.score)