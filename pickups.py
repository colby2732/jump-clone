import pygame
import math
from settings import (
    PICKUP_GLOW, PICKUP_SIZE, SCREEN_HEIGHT,
    SWORD_COLOR, SWORD_GLOW, PISTOL_COLOR, ENERGY_WAVE_COLOR,
)


class Pickup:
    """Base pickup item that floats on platforms."""

    def __init__(self, x, y, pickup_type):
        self.x = x
        self.y = y
        self.pickup_type = pickup_type  # "sword", "pistol", "wave_upgrade"
        self.collected = False
        self.size = PICKUP_SIZE
        self.bob_timer = 0.0

    @property
    def rect(self):
        return pygame.Rect(int(self.x) - self.size // 2, int(self.y) - self.size // 2,
                           self.size, self.size)

    def update(self):
        self.bob_timer += 0.05

    def draw(self, surface, camera_y):
        if self.collected:
            return

        dy = int(self.y - camera_y + math.sin(self.bob_timer) * 4)
        dx = int(self.x)

        if dy < -20 or dy > SCREEN_HEIGHT + 20:
            return

        s = self.size
        hs = s // 2

        # Glow ring
        glow_radius = hs + 4 + int(abs(math.sin(self.bob_timer * 2)) * 3)
        glow_surf = pygame.Surface((glow_radius * 2, glow_radius * 2), pygame.SRCALPHA)
        pygame.draw.circle(glow_surf, (*PICKUP_GLOW, 40), (glow_radius, glow_radius), glow_radius)
        surface.blit(glow_surf, (dx - glow_radius, dy - glow_radius))

        if self.pickup_type == "sword":
            # Miniature cyber sword icon
            pygame.draw.line(surface, SWORD_GLOW, (dx, dy + hs), (dx, dy - hs), 4)
            pygame.draw.line(surface, SWORD_COLOR, (dx, dy + hs), (dx, dy - hs), 2)
            # Hilt
            pygame.draw.rect(surface, (80, 70, 60), (dx - 3, dy + hs - 2, 7, 3))

        elif self.pickup_type == "pistol":
            # Miniature pistol icon
            pygame.draw.rect(surface, PISTOL_COLOR, (dx - 5, dy - 2, 10, 5))
            pygame.draw.rect(surface, (100, 100, 110), (dx + 4, dy - 1, 3, 3))
            # Grip
            pygame.draw.rect(surface, (80, 70, 60), (dx - 3, dy + 2, 4, 4))

        elif self.pickup_type == "wave_upgrade":
            # Energy wave crystal
            points = [
                (dx, dy - hs),
                (dx + hs, dy),
                (dx, dy + hs),
                (dx - hs, dy),
            ]
            pygame.draw.polygon(surface, ENERGY_WAVE_COLOR, points)
            # Inner glow
            inner = hs - 3
            if inner > 0:
                inner_pts = [
                    (dx, dy - inner),
                    (dx + inner, dy),
                    (dx, dy + inner),
                    (dx - inner, dy),
                ]
                pygame.draw.polygon(surface, (200, 255, 240), inner_pts)
