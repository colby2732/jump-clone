import pygame
import random
from settings import (
    WORLD_WIDTH, WORLD_HEIGHT, WALL_THICKNESS,
    PLATFORM_COLOR, PLATFORM_EDGE_COLOR, GROUND_COLOR,
    WALL_COLOR, PEAK_COLOR, SCREEN_HEIGHT,
)

# Alleyway colors
BRICK_COLOR = (90, 45, 38)
BRICK_DARK = (70, 35, 28)
BRICK_LINE = (55, 30, 22)
DUMPSTER_COLOR = (45, 80, 50)
DUMPSTER_DARK = (35, 60, 38)
PIPE_COLOR = (110, 100, 90)
PUDDLE_COLOR = (30, 35, 55)
GRAFFITI_COLORS = [(200, 50, 70), (50, 180, 220), (220, 180, 40)]


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
        self.alley_props: list[dict] = []  # Decorative elements
        self._generate()

    def _generate(self):
        playable_width = WORLD_WIDTH - WALL_THICKNESS * 2

        # Ground floor — safe starting area
        self.platforms.append(
            Platform(WALL_THICKNESS, WORLD_HEIGHT - 20, playable_width, 20, GROUND_COLOR)
        )

        # --- Alleyway props at the bottom ---
        self._generate_alleyway()

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

    def _generate_alleyway(self):
        """Generate decorative props for the alleyway starting area."""
        ground_y = WORLD_HEIGHT - 20

        # Dumpster on the left
        self.alley_props.append({
            "type": "dumpster",
            "x": WALL_THICKNESS + 30,
            "y": ground_y - 40,
            "w": 55, "h": 40,
        })

        # Dumpster on the right (lid open)
        self.alley_props.append({
            "type": "dumpster_open",
            "x": WORLD_WIDTH - WALL_THICKNESS - 100,
            "y": ground_y - 40,
            "w": 55, "h": 40,
        })

        # Puddles
        self.alley_props.append({
            "type": "puddle",
            "x": WORLD_WIDTH // 2 - 30, "y": ground_y - 3,
            "w": 60, "h": 4,
        })
        self.alley_props.append({
            "type": "puddle",
            "x": WALL_THICKNESS + 120, "y": ground_y - 2,
            "w": 35, "h": 3,
        })

        # Pipe running down left wall
        self.alley_props.append({
            "type": "pipe",
            "x": WALL_THICKNESS,
            "y": ground_y - 300,
            "h": 300,
        })

        # Graffiti tags on walls
        self.alley_props.append({
            "type": "graffiti",
            "x": WALL_THICKNESS + 2,
            "y": ground_y - 150,
            "text": "JUMP",
        })
        self.alley_props.append({
            "type": "graffiti",
            "x": WORLD_WIDTH - WALL_THICKNESS - 55,
            "y": ground_y - 200,
            "text": "UP!",
        })

        # Brick pattern on walls (bottom 600px)
        self.alley_props.append({
            "type": "bricks",
            "y_start": ground_y - 580,
            "y_end": ground_y,
        })

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
        # Draw alleyway decorations behind everything
        self._draw_alleyway(surface, camera_y)

        for wall in self.walls:
            wall.draw(surface, camera_y)
        for plat in self.platforms:
            plat.draw(surface, camera_y)

    def _draw_alleyway(self, surface: pygame.Surface, camera_y: float):
        """Render all alleyway decorative props."""
        sh = surface.get_height()

        for prop in self.alley_props:
            ptype = prop["type"]

            if ptype == "bricks":
                self._draw_bricks(surface, camera_y, prop["y_start"], prop["y_end"])

            elif ptype == "dumpster":
                dy = int(prop["y"] - camera_y)
                if -60 < dy < sh + 10:
                    x, w, h = prop["x"], prop["w"], prop["h"]
                    # Body
                    pygame.draw.rect(surface, DUMPSTER_COLOR, (x, dy, w, h))
                    pygame.draw.rect(surface, DUMPSTER_DARK, (x, dy, w, h), 2)
                    # Lid (closed)
                    pygame.draw.rect(surface, DUMPSTER_DARK, (x - 2, dy - 4, w + 4, 5))
                    # Handle
                    pygame.draw.rect(surface, PIPE_COLOR, (x + w // 2 - 6, dy + 8, 12, 3))

            elif ptype == "dumpster_open":
                dy = int(prop["y"] - camera_y)
                if -60 < dy < sh + 10:
                    x, w, h = prop["x"], prop["w"], prop["h"]
                    # Body
                    pygame.draw.rect(surface, DUMPSTER_COLOR, (x, dy, w, h))
                    pygame.draw.rect(surface, DUMPSTER_DARK, (x, dy, w, h), 2)
                    # Lid (open, tilted back)
                    pygame.draw.rect(surface, DUMPSTER_DARK, (x + w - 5, dy - 20, 5, 22))
                    pygame.draw.rect(surface, DUMPSTER_DARK, (x + 5, dy - 20, w - 5, 4))
                    # Trash poking out
                    pygame.draw.rect(surface, (150, 140, 100), (x + 10, dy - 5, 8, 8))
                    pygame.draw.rect(surface, (120, 130, 110), (x + 25, dy - 8, 10, 10))

            elif ptype == "puddle":
                dy = int(prop["y"] - camera_y)
                if 0 < dy < sh:
                    pygame.draw.ellipse(surface, PUDDLE_COLOR,
                                        (prop["x"], dy, prop["w"], prop["h"]))
                    # Subtle reflection highlight
                    pygame.draw.ellipse(surface, (40, 45, 70),
                                        (prop["x"] + 5, dy, prop["w"] // 3, prop["h"]))

            elif ptype == "pipe":
                dy = int(prop["y"] - camera_y)
                h = prop["h"]
                if dy + h > 0 and dy < sh:
                    x = prop["x"]
                    pygame.draw.rect(surface, PIPE_COLOR, (x + 3, dy, 8, h))
                    pygame.draw.rect(surface, (90, 82, 74), (x + 3, dy, 8, h), 1)
                    # Pipe brackets every 60px
                    for by in range(0, h, 60):
                        bracket_y = dy + by
                        if 0 < bracket_y < sh:
                            pygame.draw.rect(surface, (80, 72, 64), (x + 1, bracket_y, 12, 4))

            elif ptype == "graffiti":
                dy = int(prop["y"] - camera_y)
                if 0 < dy < sh:
                    font = pygame.font.SysFont("monospace", 22, bold=True)
                    color = GRAFFITI_COLORS[hash(prop["text"]) % len(GRAFFITI_COLORS)]
                    text_surf = font.render(prop["text"], True, color)
                    surface.blit(text_surf, (prop["x"], dy))

    def _draw_bricks(self, surface, camera_y, y_start, y_end):
        """Draw brick pattern on both walls in the alleyway zone."""
        sh = surface.get_height()
        brick_h = 12
        brick_w = 20

        for y in range(y_start, y_end, brick_h):
            dy = int(y - camera_y)
            if dy > sh + brick_h or dy < -brick_h:
                continue

            row = (y - y_start) // brick_h
            offset = (brick_w // 2) if row % 2 else 0

            # Left wall bricks
            for bx in range(0, WALL_THICKNESS, brick_w):
                pygame.draw.rect(surface, BRICK_COLOR,
                                 (bx, dy, brick_w - 1, brick_h - 1))
                pygame.draw.rect(surface, BRICK_LINE,
                                 (bx, dy, brick_w, brick_h), 1)

            # Right wall bricks
            rw_x = WORLD_WIDTH - WALL_THICKNESS
            for bx in range(rw_x, WORLD_WIDTH, brick_w):
                pygame.draw.rect(surface, BRICK_COLOR,
                                 (bx, dy, brick_w - 1, brick_h - 1))
                pygame.draw.rect(surface, BRICK_LINE,
                                 (bx, dy, brick_w, brick_h), 1)
