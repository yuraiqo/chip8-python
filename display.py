import pygame

BLACK = (0, 0, 0)
WHITE = (255, 255, 255)

WIDTH = 64
HEIGHT = 32


class Display:

    def __init__(self, scale) -> None:
        self.scale = scale
        self.display = [[0 for x in range(WIDTH)] for y in range(HEIGHT)]
        self.window = pygame.display.set_mode((WIDTH * self.scale,
                                               HEIGHT * self.scale))
        self.window.fill(BLACK)
        pygame.display.flip()

    def set_pixel(self, x, y) -> bool: 
        x %= WIDTH
        y %= HEIGHT
        self.display[y][x] ^= 1
        return not self.display[y][x]

    def clear(self) -> None:
        self.display = [[0 for x in range(WIDTH)] for y in range(HEIGHT)]
        pygame.display.flip()

    def render(self) -> None:
        for y in range(HEIGHT):
            for x in range(WIDTH):
                color = BLACK
                if self.display[y][x]:
                    color = WHITE
                pygame.draw.rect(self.window, color, (
                    x * self.scale, y * self.scale,
                    self.scale, self.scale
                ), 0)
            pygame.display.flip()
