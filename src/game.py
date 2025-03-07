import pygame
import random
import json
from pygame.locals import *


class Game:
    def __init__(self, screen, level_name, scoreboard):
        self.screen = screen
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
        self.classmate_img = pygame.image.load("assets/images/classmate.png")
        self.player_img = pygame.image.load("assets/images/player.png")

        pygame.mixer.music.load("assets/sounds/background.mp3")
        self.shoot_sound = pygame.mixer.Sound("assets/sounds/shoot.wav")
        self.hit_sound = pygame.mixer.Sound("assets/sounds/hit.wav")

    def init_game_state(self):
        self.score = 0
        self.time_left = self.level_settings["game_time"]
        self.player_rect = self.player_img.get_rect(center=(400, 300))
        self.classmates = []
        self.bullets = []
        self.running = True

    def run(self):
        pygame.mixer.music.play(-1)
        clock = pygame.time.Clock()

        while self.running:
            self.handle_events()
            self.update()
            self.render()
            clock.tick(60)

        pygame.mixer.music.stop()
        self.handle_game_over()

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == QUIT:
                self.running = False
            if event.type == MOUSEBUTTONDOWN and event.button == 1:
                self.handle_shot(event.pos)

    def handle_shot(self, mouse_pos):
        self.bullets.append({
            'start': self.player_rect.center,
            'target': mouse_pos,
            'position': list(self.player_rect.center)
        })
        self.shoot_sound.play()

    def update(self):
        for bullet in self.bullets[:]:
            dx = bullet['target'][0] - bullet['position'][0]
            dy = bullet['target'][1] - bullet['position'][1]
            distance = max(abs(dx), abs(dy))

            if distance < 5:
                self.bullets.remove(bullet)
                continue

            bullet['position'][0] += dx * 0.1
            bullet['position'][1] += dy * 0.1

        if (random.random() < self.level_settings["spawn_rate"] and
                len(self.classmates) < self.level_settings["max_classmates"]):
            self.spawn_classmate()

        self.time_left -= 1 / 60
        if self.time_left <= 0:
            self.running = False

    def spawn_classmate(self):
        spawn_x = random.choice([-50, 850])
        spawn_y = random.randint(50, 550)
        new_classmate = {
            'rect': pygame.Rect(spawn_x, spawn_y, 50, 50),
            'speed': self.level_settings["classmate_speed"]
        }
        self.classmates.append(new_classmate)

    def render(self):
        self.screen.blit(self.background, (0, 0))

        self.screen.blit(self.player_img, self.player_rect)

        for classmate in self.classmates:
            self.screen.blit(self.classmate_img, classmate['rect'])

        for bullet in self.bullets:
            pygame.draw.circle(self.screen, (255, 0, 0), bullet['position'], 4)

        self.draw_ui()
        pygame.display.flip()

    def draw_ui(self):
        ui_font = pygame.font.Font(None, 36)

        score_text = ui_font.render(f"Score: {self.score}", True, (255, 255, 255))
        self.screen.blit(score_text, (10, 10))

        timer_text = ui_font.render(f"Time: {int(self.time_left)}", True, (255, 255, 255))
        self.screen.blit(timer_text, (10, 50))

        level_text = ui_font.render(f"Level: {self.level_name}", True, (255, 255, 255))
        self.screen.blit(level_text, (10, 90))

    def handle_game_over(self):
        if self.score > self.scoreboard.get_top_score():
            self.show_highscore_dialog()

    def show_highscore_dialog(self):
        player_name = "Player1"
        self.scoreboard.add_score(player_name, self.score)