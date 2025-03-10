import pygame
import sys
from menu import MainMenu
from game import Game
from scoreboard import Scoreboard


def main():
    pygame.init()
    screen_size = (1024, 1024)
    screen = pygame.display.set_mode(screen_size)
    pygame.display.set_caption("Classmate Chaos")

    scoreboard = Scoreboard("assets/config/scores.json")
    menu = MainMenu(screen)

    while True:
        menu_action = menu.run()

        if menu_action == "start_game":
            game = Game(screen, menu.selected_level, scoreboard)
            game.run()
        elif menu_action == "scoreboard":
            scoreboard.display(screen)
        elif menu_action == "help":
            show_help_screen(screen)
        elif menu_action == "quit":
            pygame.quit()
            sys.exit()


def show_help_screen(screen):
    screen_width, screen_height = screen.get_size()
    help_font = pygame.font.Font(None, 45)
    lines = [
        "How to Play:",
        "- Left-click to shoot classmates",
        "- Complete levels before time runs out",
        "- Higher levels = faster spawn rates",
        "Press ESC to return to menu"
    ]

    screen.fill((0, 0, 0))
    y_offset = screen_height // 3
    for line in lines:
        text_surface = help_font.render(line, True, (255, 255, 255))
        text_rect = text_surface.get_rect(center=(screen_width // 2, y_offset))
        screen.blit(text_surface, text_rect)
        y_offset += 80

    pygame.display.flip()

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return


if __name__ == "__main__":
    main()