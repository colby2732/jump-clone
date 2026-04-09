import pygame
import sys
from settings import (
    SCREEN_WIDTH, SCREEN_HEIGHT, FPS, TITLE, BG_COLOR,
    TEXT_COLOR, WORLD_HEIGHT, PEAK_COLOR, CYBER_GREEN,
    CYBER_PURPLE, CYBER_BLUE, CYBER_RED,
)
from player import Player
from level import Level
from camera import Camera


class Game:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption(TITLE)
        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont("monospace", 16)
        self.big_font = pygame.font.SysFont("monospace", 48, bold=True)
        self.med_font = pygame.font.SysFont("monospace", 24)

        self.level = Level()
        self.camera = Camera()
        self.player = Player(
            SCREEN_WIDTH // 2 - 10,
            WORLD_HEIGHT - 60,
        )

        self.won = False
        self.fall_count = 0
        self._prev_y = self.player.y

    def run(self):
        while True:
            self._handle_events()
            if not self.won:
                self._update()
            self._draw()
            self.clock.tick(FPS)

    def _handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    sys.exit()
                if event.key == pygame.K_r:
                    self._reset()

    def _update(self):
        keys = pygame.key.get_pressed()
        collidables = self.level.get_all_collidables(self.player.y)
        self.player.update(keys, collidables)
        self.camera.update(self.player.y)

        # Track big falls (fell more than 200px)
        if self.player.on_ground:
            if self.player.y - self._prev_y > 200:
                self.fall_count += 1
            self._prev_y = self.player.y

        # Check victory — reached the gold platform at y=100
        if self.player.y < 150 and self.player.on_ground:
            self.won = True

    def _draw(self):
        self.screen.fill(BG_COLOR)

        # Draw background depth lines for atmosphere
        self._draw_background()

        # Level
        self.level.draw(self.screen, self.camera.y)

        # Player
        self.player.draw(self.screen, self.camera.y)

        # Charge bar
        self.player.draw_charge_bar(self.screen)

        # HUD
        self._draw_hud()

        # Win screen
        if self.won:
            self._draw_win()

        pygame.display.flip()

    def _draw_background(self):
        # Cyberpunk cityscape background
        # Fill with dark gradient
        for y in range(SCREEN_HEIGHT):
            depth = y / SCREEN_HEIGHT
            shade = int(15 + depth * 10)
            pygame.draw.line(self.screen, (shade, shade // 2, shade + 10), (0, y), (SCREEN_WIDTH, y))

        # Distant buildings (parallax)
        building_colors = [CYBER_GREEN, CYBER_PURPLE, CYBER_BLUE, CYBER_RED]
        for i in range(10):
            x = (i * 120 + self.camera.y * 0.1) % (SCREEN_WIDTH + 100) - 50
            height = 100 + (i % 3) * 50
            color = building_colors[i % len(building_colors)]
            pygame.draw.rect(self.screen, color, (x, SCREEN_HEIGHT - height, 80, height))
            # Glow effect
            pygame.draw.rect(self.screen, (color[0]//4, color[1]//4, color[2]//4), (x-2, SCREEN_HEIGHT - height - 2, 84, height + 4), 2)

        # Neon grid lines
        for i in range(0, SCREEN_WIDTH, 100):
            pygame.draw.line(self.screen, CYBER_GREEN, (i, 0), (i, SCREEN_HEIGHT), 1)
        for i in range(0, SCREEN_HEIGHT, 100):
            y_world = self.camera.y + i
            alpha = max(50, 150 - int((y_world / WORLD_HEIGHT) * 100))
            color = (CYBER_PURPLE[0], CYBER_PURPLE[1], CYBER_PURPLE[2], alpha) if alpha < 255 else CYBER_PURPLE
            # Pygame doesn't support alpha in draw.line directly, so use solid
            pygame.draw.line(self.screen, CYBER_PURPLE, (0, i), (SCREEN_WIDTH, i), 1)

        # Floating particles
        import random
        random.seed(42)
        for i in range(20):
            x = (random.randint(0, SCREEN_WIDTH) + self.camera.y * 0.05) % SCREEN_WIDTH
            y = random.randint(0, SCREEN_HEIGHT)
            pygame.draw.circle(self.screen, CYBER_BLUE, (x, y), 1)

    def _draw_hud(self):
        # Height indicator
        height_pct = 1 - (self.player.y / WORLD_HEIGHT)
        height_text = f"Height: {int(height_pct * 100)}%"
        text_surf = self.font.render(height_text, True, TEXT_COLOR)
        self.screen.blit(text_surf, (10, 10))

        # Fall counter
        if self.fall_count > 0:
            fall_text = f"Falls: {self.fall_count}"
            fall_surf = self.font.render(fall_text, True, (220, 80, 80))
            self.screen.blit(fall_surf, (10, 30))

        # Peak height
        peak_pct = 1 - (self.player.highest_y / WORLD_HEIGHT)
        peak_text = f"Peak: {int(peak_pct * 100)}%"
        peak_surf = self.font.render(peak_text, True, PEAK_COLOR)
        self.screen.blit(peak_surf, (10, 50))

        # Height bar on right side
        bar_x = SCREEN_WIDTH - 20
        bar_height = SCREEN_HEIGHT - 40
        bar_y = 20
        pygame.draw.rect(self.screen, (30, 30, 40), (bar_x, bar_y, 10, bar_height))
        fill_h = int(bar_height * height_pct)
        pygame.draw.rect(self.screen, (50, 180, 80), (bar_x, bar_y + bar_height - fill_h, 10, fill_h))
        # Peak marker
        peak_fill = int(bar_height * peak_pct)
        pygame.draw.rect(self.screen, PEAK_COLOR, (bar_x - 2, bar_y + bar_height - peak_fill, 14, 2))

    def _draw_win(self):
        # Dim overlay
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 150))
        self.screen.blit(overlay, (0, 0))

        # Victory text
        win_text = self.big_font.render("YOU MADE IT!", True, PEAK_COLOR)
        self.screen.blit(
            win_text,
            (SCREEN_WIDTH // 2 - win_text.get_width() // 2, SCREEN_HEIGHT // 3)
        )

        falls_text = self.med_font.render(f"Falls: {self.fall_count}", True, TEXT_COLOR)
        self.screen.blit(
            falls_text,
            (SCREEN_WIDTH // 2 - falls_text.get_width() // 2, SCREEN_HEIGHT // 2)
        )

        restart_text = self.font.render("Press R to restart  |  ESC to quit", True, TEXT_COLOR)
        self.screen.blit(
            restart_text,
            (SCREEN_WIDTH // 2 - restart_text.get_width() // 2, SCREEN_HEIGHT // 2 + 50)
        )

    def _reset(self):
        self.player = Player(
            SCREEN_WIDTH // 2 - 10,
            WORLD_HEIGHT - 60,
        )
        self.camera = Camera()
        self.won = False
        self.fall_count = 0
        self._prev_y = self.player.y


if __name__ == "__main__":
    game = Game()
    game.run()
