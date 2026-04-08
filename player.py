import pygame
from settings import (
    GRAVITY, MAX_FALL_SPEED, CHARGE_RATE, MAX_CHARGE,
    MIN_JUMP_POWER, MAX_JUMP_POWER, HORIZONTAL_JUMP_SPEED,
    PLAYER_WIDTH, PLAYER_HEIGHT, PLAYER_GROUND_SPEED,
    PLAYER_COLOR, PLAYER_OUTLINE, CHARGE_BAR_BG, CHARGE_BAR_FG,
    CHARGE_BAR_MAX, WORLD_WIDTH, WALL_THICKNESS,
)


class Player:
    def __init__(self, x: float, y: float):
        self.x = x
        self.y = y
        self.width = PLAYER_WIDTH
        self.height = PLAYER_HEIGHT

        self.vel_x = 0.0
        self.vel_y = 0.0
        self.on_ground = False

        # Jump charge state
        self.charging = False
        self.charge = 0.0
        self.facing = 0  # -1 left, 0 none, 1 right

        # Track highest point reached
        self.highest_y = y

    @property
    def rect(self) -> pygame.Rect:
        return pygame.Rect(int(self.x), int(self.y), self.width, self.height)

    def update(self, keys, platforms):
        if self.on_ground:
            self._handle_ground(keys)
        else:
            self._handle_air()

        # Apply gravity
        self.vel_y += GRAVITY
        if self.vel_y > MAX_FALL_SPEED:
            self.vel_y = MAX_FALL_SPEED

        # Move horizontally
        self.x += self.vel_x
        self._clamp_to_walls()
        self._collide_horizontal(platforms)

        # Move vertically
        self.y += self.vel_y
        self._collide_vertical(platforms)

        # Track highest point (lower y = higher)
        if self.y < self.highest_y:
            self.highest_y = self.y

    def _handle_ground(self, keys):
        if self.charging:
            # Currently charging — can't move
            self.vel_x = 0

            # Track facing direction during charge
            if keys[pygame.K_LEFT] or keys[pygame.K_a]:
                self.facing = -1
            elif keys[pygame.K_RIGHT] or keys[pygame.K_d]:
                self.facing = 1

            # Increase charge
            self.charge += CHARGE_RATE
            if self.charge > MAX_CHARGE:
                self.charge = MAX_CHARGE

            # Check if space released
            if not keys[pygame.K_SPACE]:
                self._jump()
        else:
            # Walk on ground
            self.vel_x = 0
            if keys[pygame.K_LEFT] or keys[pygame.K_a]:
                self.vel_x = -PLAYER_GROUND_SPEED
                self.facing = -1
            elif keys[pygame.K_RIGHT] or keys[pygame.K_d]:
                self.vel_x = PLAYER_GROUND_SPEED
                self.facing = 1

            # Start charging
            if keys[pygame.K_SPACE]:
                self.charging = True
                self.charge = 0
                self.vel_x = 0

    def _handle_air(self):
        # No air control — committed to the jump direction
        pass

    def _jump(self):
        # Calculate jump power based on charge
        charge_pct = self.charge / MAX_CHARGE
        jump_power = MIN_JUMP_POWER + (MAX_JUMP_POWER - MIN_JUMP_POWER) * charge_pct

        self.vel_y = -jump_power
        self.vel_x = self.facing * HORIZONTAL_JUMP_SPEED
        self.on_ground = False
        self.charging = False
        self.charge = 0

    def _clamp_to_walls(self):
        if self.x < WALL_THICKNESS:
            self.x = WALL_THICKNESS
            self.vel_x = 0
        if self.x + self.width > WORLD_WIDTH - WALL_THICKNESS:
            self.x = WORLD_WIDTH - WALL_THICKNESS - self.width
            self.vel_x = 0

    def _collide_horizontal(self, platforms):
        player_rect = self.rect
        for plat in platforms:
            if player_rect.colliderect(plat.rect):
                if self.vel_x > 0:
                    self.x = plat.rect.left - self.width
                elif self.vel_x < 0:
                    self.x = plat.rect.right
                self.vel_x = 0

    def _collide_vertical(self, platforms):
        player_rect = self.rect
        self.on_ground = False
        for plat in platforms:
            if player_rect.colliderect(plat.rect):
                if self.vel_y > 0:
                    # Landing on top
                    self.y = plat.rect.top - self.height
                    self.vel_y = 0
                    self.vel_x = 0
                    self.on_ground = True
                elif self.vel_y < 0:
                    # Bonking head on bottom
                    self.y = plat.rect.bottom
                    self.vel_y = 0

    def draw(self, surface: pygame.Surface, camera_y: float):
        draw_x = int(self.x)
        draw_y = int(self.y - camera_y)

        # Body
        body_rect = pygame.Rect(draw_x, draw_y, self.width, self.height)
        pygame.draw.rect(surface, PLAYER_COLOR, body_rect)
        pygame.draw.rect(surface, PLAYER_OUTLINE, body_rect, 2)

        # Eyes (direction indicator)
        eye_y = draw_y + 8
        if self.facing >= 0:
            eye_x = draw_x + 12
        else:
            eye_x = draw_x + 5
        pygame.draw.rect(surface, (255, 255, 255), (eye_x, eye_y, 5, 4))
        pygame.draw.rect(surface, (0, 0, 0), (eye_x + 2, eye_y + 1, 2, 2))

    def draw_charge_bar(self, surface: pygame.Surface):
        if not self.charging:
            return

        bar_width = 60
        bar_height = 10
        x = (surface.get_width() - bar_width) // 2
        y = surface.get_height() - 40

        # Background
        pygame.draw.rect(surface, CHARGE_BAR_BG, (x, y, bar_width, bar_height))

        # Fill
        fill_pct = self.charge / MAX_CHARGE
        fill_width = int(bar_width * fill_pct)
        color = CHARGE_BAR_FG if fill_pct < 0.9 else CHARGE_BAR_MAX
        pygame.draw.rect(surface, color, (x, y, fill_width, bar_height))

        # Border
        pygame.draw.rect(surface, (120, 120, 130), (x, y, bar_width, bar_height), 1)
