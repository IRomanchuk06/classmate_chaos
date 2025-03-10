import pygame
import random
import json
import os
import math
from pygame.locals import *


class Game:
    def __init__(self, screen, level_name, scoreboard):
        self.screen = screen
        self.screen_width, self.screen_height = screen.get_size()
        self.scoreboard = scoreboard
        self.level_name = level_name
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
        self.crosshair = pygame.image.load("assets/images/crosshair.png")
        self.classmate_images = []

        classmates_dir = "assets/images/classmates"
        for filename in os.listdir(classmates_dir):
            if filename.endswith(".png"):
                image = pygame.image.load(os.path.join(classmates_dir, filename))
                self.classmate_images.append(image)

    def init_game_state(self):
        self.score = 0
        self.time_left = self.level_settings["game_time"]
        self.targets = []
        self.bullets = []
        self.running = True
        self.spawn_timer = 0
        self.max_targets = self.level_settings["max_classmates"]
        self.wave_angle = 0
        self.gun_position = (self.screen_width // 2, self.screen_height - 50)

    def run(self):
        clock = pygame.time.Clock()
        while self.running:
            delta_time = clock.tick(60)
            self.handle_events()
            self.update(delta_time)
            self.render()
        self.handle_game_over()

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == QUIT:
                self.running = False
            if event.type == MOUSEBUTTONDOWN and event.button == 1:
                self.handle_shot(pygame.mouse.get_pos())

    def handle_shot(self, target_pos):
        start_pos = self.gun_position
        distance = math.hypot(target_pos[0] - start_pos[0], target_pos[1] - start_pos[1])
        if distance == 0: return

        speed = 15
        dx = (target_pos[0] - start_pos[0]) / distance
        dy = (target_pos[1] - start_pos[1]) / distance

        self.bullets.append({
            'pos': list(start_pos),
            'target': target_pos,
            'dx': dx * speed,
            'dy': dy * speed,
            'reached': False
        })

    def update_bullets(self, delta_time):
        for bullet in self.bullets[:]:
            bullet['pos'][0] += bullet['dx'] * delta_time / 16.667
            bullet['pos'][1] += bullet['dy'] * delta_time / 16.667

            target_dist = math.hypot(bullet['pos'][0] - bullet['target'][0],
                                     bullet['pos'][1] - bullet['target'][1])

            if target_dist < 5 and not bullet['reached']:
                bullet['reached'] = True
                hit = False
                for target in self.targets[:]:
                    if target['rect'].collidepoint(bullet['target']):
                        self.targets.remove(target)
                        self.score += 10
                        hit = True
                        break
                if not hit:
                    self.score = max(0, self.score - 2)
                self.bullets.remove(bullet)

    def update_targets(self, delta_time):
        self.spawn_timer += delta_time
        self.wave_angle += 0.02

        if self.spawn_timer > self.level_settings["spawn_interval"]:
            self.spawn_timer = 0
            if len(self.targets) < self.max_targets:
                self.spawn_target()

        for target in self.targets[:]:
            target['x'] += math.cos(target['angle']) * target['speed'] * delta_time / 16.667
            target['y'] += math.sin(target['angle']) * target['speed'] * 0.5 * delta_time / 16.667
            target['rect'].center = (target['x'], target['y'])

            if target['x'] < -100 or target['x'] > self.screen_width + 100:
                self.targets.remove(target)

    def update(self, delta_time):
        self.update_bullets(delta_time)
        self.update_targets(delta_time)

        self.time_left -= delta_time / 1000
        if self.time_left <= 0:
            self.running = False

    def spawn_target(self):
        start_side = random.choice(['left', 'right'])
        image = random.choice(self.classmate_images)
        speed = self.level_settings["classmate_speed"]
        y_base = random.randint(50, self.screen_height // 3)

        if start_side == 'left':
            x = -50
            angle = random.uniform(-0.5, 0.5)
        else:
            x = self.screen_width + 50
            angle = random.uniform(math.pi - 0.5, math.pi + 0.5)

        new_target = {
            'rect': pygame.Rect(0, 0, image.get_width(), image.get_height()),
            'x': x,
            'y': y_base + math.sin(self.wave_angle) * 50,
            'angle': angle,
            'speed': speed,
            'image': image
        }
        self.targets.append(new_target)

    def render(self):
        self.screen.blit(self.background, (0, 0))

        for target in self.targets:
            rotated_image = pygame.transform.rotate(target['image'], math.degrees(-target['angle']))
            self.screen.blit(rotated_image, target['rect'])

        for bullet in self.bullets:
            pygame.draw.circle(self.screen, (255, 0, 0),
                               (int(bullet['pos'][0]), int(bullet['pos'][1])), 6)

        crosshair_rect = self.crosshair.get_rect(center=pygame.mouse.get_pos())
        self.screen.blit(self.crosshair, crosshair_rect)

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