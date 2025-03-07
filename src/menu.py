import json
import sys

import pygame


class MainMenu:
    def __init__(self, screen):
        self.screen = screen
        self.font = pygame.font.Font(None, 48)
        self.levels = self.load_levels()
        self.selected_level = "Easy"
        self.menu_state = "main"
        self.selected_index = 0

    def load_levels(self):
        with open("assets/config/levels.json") as f:
            return [level["name"] for level in json.load(f)["levels"]]

    def draw_menu(self, options):
        self.screen.fill((0, 0, 0))
        for index, option in enumerate(options):
            color = (255, 255, 255) if index == self.selected_index else (100, 100, 100)
            text = self.font.render(option, True, color)
            self.screen.blit(text, (250, 200 + index * 80))
        pygame.display.flip()

    def run(self):
        global options
        while True:
            if self.menu_state == "main":
                options = ["Start Game", "Scoreboard", "Help", "Quit"]
                self.draw_menu(options)
            elif self.menu_state == "level_select":
                self.draw_menu(self.levels)

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_DOWN:
                        self.selected_index = (self.selected_index + 1) % len(options)
                    elif event.key == pygame.K_UP:
                        self.selected_index = (self.selected_index - 1) % len(options)
                    elif event.key == pygame.K_RETURN:
                        return self.handle_menu_selection()
                    elif event.key == pygame.K_ESCAPE:
                        if self.menu_state == "level_select":
                            self.menu_state = "main"
                            self.selected_index = 0

    def handle_menu_selection(self):
        if self.menu_state == "main":
            if self.selected_index == 0:
                self.menu_state = "level_select"
                self.selected_index = 0
                return None
            elif self.selected_index == 1:
                return "scoreboard"
            elif self.selected_index == 2:
                return "help"
            else:
                return "quit"
        elif self.menu_state == "level_select":
            self.selected_level = self.levels[self.selected_index]
            self.menu_state = "main"
            return "start_game"