import pygame
import sys
from menu import MainMenu
from game import Game
from scoreboard import Scoreboard


def main():
    # Initialize Pygame
    pygame.init()
    screen = pygame.display.set_mode((800, 600))
    pygame.display.set_caption("Campus Frenzy")

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
    help_font = pygame.font.Font(None, 36)
    lines = [
        "How to Play:",
        "- Left-click to shoot classmates",
        "- Avoid shooting innocent items",
        "- Complete levels before time runs out",
        "- Higher levels = faster spawn rates",
        "Press ESC to return to menu"
    ]

    screen.fill((0, 0, 0))
    y_offset = 100
    for line in lines:
        text_surface = help_font.render(line, True, (255, 255, 255))
        screen.blit(text_surface, (50, y_offset))
        y_offset += 40

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