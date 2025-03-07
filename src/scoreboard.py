import json
import sys

import pygame


class Scoreboard:
    def __init__(self, filename):
        self.filename = filename
        self.scores = self.load_scores()

    def load_scores(self):
        try:
            with open(self.filename, 'r') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return []

    def save_scores(self):
        with open(self.filename, 'w') as f:
            json.dump(self.scores, f, indent=2)

    def add_score(self, name, score):
        self.scores.append({"name": name, "score": score})
        self.scores.sort(key=lambda x: x["score"], reverse=True)
        self.scores = self.scores[:10]  # Keep top 10
        self.save_scores()

    def get_top_score(self):
        return self.scores[0]["score"] if self.scores else 0

    def display(self, screen):
        screen.fill((0, 0, 0))
        title_font = pygame.font.Font(None, 64)
        item_font = pygame.font.Font(None, 48)

        title = title_font.render("High Scores", True, (255, 255, 255))
        screen.blit(title, (250, 50))

        y_offset = 150
        for idx, entry in enumerate(self.scores[:10]):
            text = f"{idx + 1}. {entry['name']} - {entry['score']}"
            text_surface = item_font.render(text, True, (255, 255, 255))
            screen.blit(text_surface, (200, y_offset))
            y_offset += 50

        pygame.display.flip()

        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        return