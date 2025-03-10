import sys
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

        self.camera_offset_x = 0
        self.camera_offset_y = 0
        self.camera_speed = 8

        self.background_width = 1800
        self.background_height = 1200
        self.camera_max_x = self.background_width - self.screen_width
        self.camera_max_y = self.background_height - self.screen_height

        self.bullets_count = 8
        self.max_bullets = 8
        self.reload_time = 1.5
        self.last_shot_time = 0
        self.is_reloading = False

    def load_config(self):
        with open("assets/config/settings.json") as f:
            self.base_settings = json.load(f)

        with open("assets/config/levels.json") as f:
            levels = json.load(f)["levels"]
            level_data = next(lvl for lvl in levels if lvl["name"] == self.level_name)
            self.level_settings = level_data
            self.required_score = level_data["required_score"]

    def load_assets(self):
        self.background = pygame.image.load("assets/images/background.png")
        self.background = pygame.transform.scale(self.background, (1800, 1200))
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
        self.running = True
        self.victory = False
        self.spawn_timer = 0
        self.max_targets = self.level_settings["max_classmates"]
        self.wave_angle = 0

    def run(self):
        clock = pygame.time.Clock()
        while self.running:
            delta_time = clock.tick(60)
            self.handle_events()
            self.update_camera()
            self.update(delta_time)
            self.render()

            if self.score >= self.required_score:
                self.victory = True
                self.running = False

        self.handle_game_over()

    def update_camera(self):
        mouse_x, mouse_y = pygame.mouse.get_pos()

        if mouse_x < 100:
            self.camera_offset_x += self.camera_speed
        elif mouse_x > self.screen_width - 100:
            self.camera_offset_x -= self.camera_speed

        self.camera_offset_y = 0

        self.camera_offset_x = max(-self.camera_max_x, min(0, self.camera_offset_x))

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == QUIT:
                self.running = False
            if event.type == MOUSEBUTTONDOWN and event.button == 1:
                self.handle_shot(pygame.mouse.get_pos())

    def handle_shot(self, mouse_pos):
        current_time = pygame.time.get_ticks() / 1000

        if self.bullets_count <= 0:
            if current_time - self.last_shot_time >= self.reload_time:
                self.bullets_count = self.max_bullets
                self.is_reloading = False
            else:
                return

        if not self.is_reloading:
            self.bullets_count -= 1
            self.last_shot_time = current_time
            if self.bullets_count <= 0:
                self.is_reloading = True

            hit = False
            adjusted_pos = (
                mouse_pos[0] - self.camera_offset_x,
                mouse_pos[1]
            )

            for target in self.targets[:]:
                if target['rect'].collidepoint(adjusted_pos):
                    self.targets.remove(target)
                    self.score += 10 + int(10 * (1 - target['scale']))
                    hit = True
                    break

            if not hit:
                self.score = max(0, self.score - 5)

    def spawn_target(self):
        scale = random.uniform(0.4, 1.0)
        is_moving = random.random() > 0.06

        # Новые параметры генерации
        min_y = 50  # Минимальная высота появления
        max_y = int(self.background_height * 0.6)  # Максимальная высота (60% от высоты фона)
        x = random.randint(-200, self.background_width + 200)
        y = random.randint(min_y, max_y)

        image = random.choice(self.classmate_images)
        orig_width = image.get_width()
        orig_height = image.get_height()

        min_size = 50
        scaled_width = max(min_size, int(orig_width * scale))
        scaled_height = max(min_size, int(orig_height * scale))

        scaled_image = pygame.transform.scale(image, (scaled_width, scaled_height))

        base_speed = random.uniform(0.5, 2.0)
        speed = base_speed * (1.5 - scale)

        new_target = {
            'rect': pygame.Rect(x, y, scaled_width, scaled_height),
            'speed': speed if is_moving else 0,
            'direction': random.choice([-1, 1]),
            'scale': scale,
            'image': scaled_image,
            'is_moving': is_moving,
            'wave_phase': random.uniform(0, 2 * math.pi)
        }
        self.targets.append(new_target)

    def update(self, delta_time):
        current_time = pygame.time.get_ticks() / 1000
        if self.is_reloading and current_time - self.last_shot_time >= self.reload_time:
            self.bullets_count = self.max_bullets
            self.is_reloading = False

        self.spawn_timer += delta_time
        if self.spawn_timer > self.level_settings["spawn_interval"]:
            self.spawn_timer = 0
            if len(self.targets) < self.max_targets:
                self.spawn_target()

        for target in self.targets:
            if target['is_moving']:
                target['rect'].x += target['speed'] * target['direction']

                if target['rect'].x < -300 or target['rect'].x > self.background_width + 300:
                    target['direction'] *= -1

        self.time_left -= delta_time / 1000
        if self.time_left <= 0:
            self.running = False

    def render(self):
        self.screen.blit(self.background, (self.camera_offset_x, self.camera_offset_y))

        for target in self.targets:
            pos = (
                target['rect'].x + self.camera_offset_x,
                target['rect'].y + self.camera_offset_y
            )
            self.screen.blit(target['image'], pos)

        crosshair_rect = self.crosshair.get_rect(center=pygame.mouse.get_pos())
        self.screen.blit(self.crosshair, crosshair_rect)

        self.draw_ui()
        pygame.display.flip()

    def draw_ui(self):
        ui_font = pygame.font.Font(None, 36)

        score_text = f"Score: {self.score}/{self.required_score}"
        self.screen.blit(ui_font.render(score_text, True, (255, 255, 255)), (10, 10))

        bar_width = 200
        bar_height = 20
        progress = min(self.score / self.required_score, 1.0)
        pygame.draw.rect(self.screen, (50, 50, 50), (10, 50, bar_width, bar_height))
        pygame.draw.rect(self.screen, (0, 200, 0), (10, 50, bar_width * progress, bar_height))

        time_text = f"Time: {int(self.time_left)}"
        self.screen.blit(ui_font.render(time_text, True, (255, 255, 255)), (10, 80))

        level_text = f"Level: {self.level_name}"
        self.screen.blit(ui_font.render(level_text, True, (255, 255, 255)), (10, 110))

        bullets_text = f"Ammo: {self.bullets_count}/{self.max_bullets}"
        text_surface = ui_font.render(bullets_text, True, (255, 255, 255))
        self.screen.blit(text_surface, (self.screen_width - 150, 10))

        if self.is_reloading:
            reload_progress = (pygame.time.get_ticks() / 1000 - self.last_shot_time) / self.reload_time
            pygame.draw.rect(self.screen, (200, 0, 0), (self.screen_width - 150, 40, 100, 10))
            pygame.draw.rect(self.screen, (0, 200, 0), (self.screen_width - 150, 40, 100 * reload_progress, 10))

    def handle_game_over(self):
        if self.victory:
            self.show_victory_screen()
        elif self.score > self.scoreboard.get_top_score():
            self.show_highscore_dialog()

    def show_victory_screen(self):
        victory_font = pygame.font.Font(None, 72)
        small_font = pygame.font.Font(None, 36)

        self.screen.fill((0, 50, 0))

        victory_text = victory_font.render("LEVEL COMPLETE!", True, (255, 255, 255))
        text_rect = victory_text.get_rect(center=(self.screen_width // 2, self.screen_height // 2 - 50))
        self.screen.blit(victory_text, text_rect)

        score_text = small_font.render(f"Final Score: {self.score}", True, (255, 255, 255))
        score_rect = score_text.get_rect(center=(self.screen_width // 2, self.screen_height // 2 + 50))
        self.screen.blit(score_text, score_rect)

        continue_text = small_font.render("Click to continue...", True, (200, 200, 200))
        continue_rect = continue_text.get_rect(center=(self.screen_width // 2, self.screen_height - 100))
        self.screen.blit(continue_text, continue_rect)

        pygame.display.flip()

        waiting = True
        while waiting:
            for event in pygame.event.get():
                if event.type == QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == MOUSEBUTTONDOWN:
                    waiting = False

    def show_highscore_dialog(self):
        player_name = "Player1"
        self.scoreboard.add_score(player_name, self.score)