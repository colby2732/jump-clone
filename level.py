import pygame
import random
from settings import (
    WORLD_WIDTH, WORLD_HEIGHT, WALL_THICKNESS,
    PLATFORM_COLOR, PLATFORM_EDGE_COLOR, GROUND_COLOR,
    WALL_COLOR, PEAK_COLOR, SCREEN_HEIGHT,
)


class Platform:
    def __init__(self, x: int, y: int, width: int, height: int = 12, color=None):
        self.rect = pygame.Rect(x, y, width, height)
        self.color = color or PLATFORM_COLOR

    def draw(self, surface: pygame.Surface, camera_y: float):
        draw_rect = self.rect.move(0, -camera_y)
        # Only draw if visible
        if draw_rect.bottom < -20 or draw_rect.top > surface.get_height() + 20:
            return
        pygame.draw.rect(surface, self.color, draw_rect)
        pygame.draw.rect(surface, PLATFORM_EDGE_COLOR, draw_rect, 1)


class Level:
    def __init__(self):
        self.platforms: list[Platform] = []
        self.walls: list[Platform] = []
        self._generate()

    def _generate(self):
        playable_width = WORLD_WIDTH - WALL_THICKNESS * 2

        # Ground floor — safe starting area
        self.platforms.append(
            Platform(WALL_THICKNESS, WORLD_HEIGHT - 20, playable_width, 20, GROUND_COLOR)
        )

        # Generate platforms going upward
        y = WORLD_HEIGHT - 100
        min_gap_y = 70   # Min vertical gap between platforms
        max_gap_y = 130  # Max vertical gap — keeps it possible but punishing
        min_width = 50
        max_width = 160

        random.seed(42)  # Fixed seed so the level is always the same

        while y > 200:
            gap = random.randint(min_gap_y, max_gap_y)
            y -= gap

            width = random.randint(min_width, max_width)
            x = random.randint(WALL_THICKNESS, WORLD_WIDTH - WALL_THICKNESS - width)

            # Make it harder as you go up
            height_pct = y / WORLD_HEIGHT  # 0 = top, 1 = bottom
            if height_pct < 0.3:
                # Top section — narrower platforms, bigger gaps
                width = random.randint(min_width, min_width + 40)
                y -= random.randint(0, 20)
            elif height_pct < 0.6:
                # Mid section — moderate
                width = random.randint(min_width, 120)

            self.platforms.append(Platform(x, y, width))

        # Victory platform at the top
        self.platforms.append(
            Platform(
                WORLD_WIDTH // 2 - 50, 100, 100, 14, PEAK_COLOR
            )
        )

        # Side walls (full height)
        self.walls.append(
            Platform(0, 0, WALL_THICKNESS, WORLD_HEIGHT, WALL_COLOR)
        )
        self.walls.append(
            Platform(WORLD_WIDTH - WALL_THICKNESS, 0, WALL_THICKNESS, WORLD_HEIGHT, WALL_COLOR)
        )

    def get_nearby_platforms(self, y: float, margin: float = SCREEN_HEIGHT) -> list[Platform]:
        """Return platforms near the given y for collision checks."""
        return [
            p for p in self.platforms
            if abs(p.rect.centery - y) < margin
        ]

    def get_all_collidables(self, y: float) -> list[Platform]:
        """Return platforms + walls near the player for collision."""
        nearby = self.get_nearby_platforms(y)
        return nearby + self.walls

    def draw(self, surface: pygame.Surface, camera_y: float):
        for wall in self.walls:
            wall.draw(surface, camera_y)
        for plat in self.platforms:
            plat.draw(surface, camera_y)
