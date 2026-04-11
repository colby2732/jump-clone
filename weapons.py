import pygame
import math
from settings import (
    SWORD_COLOR, SWORD_GLOW, SWORD_RANGE, SWORD_DAMAGE, SWORD_COOLDOWN,
    ENERGY_WAVE_COLOR, ENERGY_WAVE_SPEED, ENERGY_WAVE_DAMAGE, ENERGY_WAVE_LIFETIME,
    PISTOL_COLOR, PISTOL_BARREL_COLOR, BULLET_COLOR, BULLET_SPEED, BULLET_DAMAGE,
    PISTOL_COOLDOWN, SCREEN_WIDTH, SCREEN_HEIGHT,
)


class Projectile:
    """Base class for bullets and energy waves."""
    def __init__(self, x, y, direction, speed, damage, color, lifetime):
        self.x = x
        self.y = y
        self.direction = direction  # -1 left, 1 right
        self.speed = speed
        self.damage = damage
        self.color = color
        self.lifetime = lifetime
        self.age = 0
        self.alive = True
        self.width = 8
        self.height = 4

    @property
    def rect(self):
        return pygame.Rect(int(self.x), int(self.y), self.width, self.height)

    def update(self):
        self.x += self.speed * self.direction
        self.age += 1
        if self.age >= self.lifetime:
            self.alive = False

    def draw(self, surface, camera_y):
        dy = int(self.y - camera_y)
        if -10 < dy < SCREEN_HEIGHT + 10:
            pygame.draw.rect(surface, self.color,
                             (int(self.x), dy, self.width, self.height))


class Bullet(Projectile):
    def __init__(self, x, y, direction):
        super().__init__(x, y, direction, BULLET_SPEED, BULLET_DAMAGE,
                         BULLET_COLOR, 90)
        self.width = 6
        self.height = 3

    def draw(self, surface, camera_y):
        dy = int(self.y - camera_y)
        if -10 < dy < SCREEN_HEIGHT + 10:
            dx = int(self.x)
            # Bullet core
            pygame.draw.rect(surface, BULLET_COLOR, (dx, dy, self.width, self.height))
            # Bright tip
            tip_x = dx + (self.width if self.direction == 1 else -2)
            pygame.draw.rect(surface, (255, 255, 200), (tip_x, dy, 2, self.height))


class EnergyWave(Projectile):
    def __init__(self, x, y, direction):
        super().__init__(x, y, direction, ENERGY_WAVE_SPEED, ENERGY_WAVE_DAMAGE,
                         ENERGY_WAVE_COLOR, ENERGY_WAVE_LIFETIME)
        self.width = 20
        self.height = 10

    def draw(self, surface, camera_y):
        dy = int(self.y - camera_y)
        if -20 < dy < SCREEN_HEIGHT + 20:
            dx = int(self.x)
            # Fade as it ages
            fade = max(0.3, 1.0 - (self.age / self.lifetime))
            r = int(ENERGY_WAVE_COLOR[0] * fade)
            g = int(ENERGY_WAVE_COLOR[1] * fade)
            b = int(ENERGY_WAVE_COLOR[2] * fade)

            # Outer glow
            glow_surf = pygame.Surface((self.width + 8, self.height + 8), pygame.SRCALPHA)
            glow_surf.fill((r // 3, g // 3, b // 3, int(80 * fade)))
            surface.blit(glow_surf, (dx - 4, dy - 4))

            # Core wave shape
            points = [
                (dx, dy + self.height // 2),
                (dx + self.width // 3, dy),
                (dx + self.width * 2 // 3, dy + self.height // 4),
                (dx + self.width, dy + self.height // 2),
                (dx + self.width * 2 // 3, dy + self.height * 3 // 4),
                (dx + self.width // 3, dy + self.height),
            ]
            pygame.draw.polygon(surface, (r, g, b), points)
            # Bright center line
            pygame.draw.line(surface, (min(255, r + 80), min(255, g + 80), min(255, b + 80)),
                             (dx + 2, dy + self.height // 2),
                             (dx + self.width - 2, dy + self.height // 2), 2)


class CyberSword:
    def __init__(self):
        self.cooldown = 0
        self.swing_timer = 0  # >0 when swinging (visual)
        self.upgraded = False  # When True, attacks fire energy waves

    def can_attack(self):
        return self.cooldown <= 0

    def attack(self, player_x, player_y, player_w, player_h, facing):
        """Returns (hit_rect, projectile_or_None)."""
        self.cooldown = SWORD_COOLDOWN
        self.swing_timer = 10

        # Melee hitbox
        if facing == 1:
            hit_rect = pygame.Rect(player_x + player_w, player_y, SWORD_RANGE, player_h)
        else:
            hit_rect = pygame.Rect(player_x - SWORD_RANGE, player_y, SWORD_RANGE, player_h)

        # Energy wave if upgraded
        proj = None
        if self.upgraded:
            wave_x = player_x + player_w + 5 if facing == 1 else player_x - 25
            wave_y = player_y + player_h // 2 - 5
            proj = EnergyWave(wave_x, wave_y, facing)

        return hit_rect, proj

    def update(self):
        if self.cooldown > 0:
            self.cooldown -= 1
        if self.swing_timer > 0:
            self.swing_timer -= 1

    def draw(self, surface, player_cx, player_base_y, facing, camera_y):
        """Draw the sword on the player."""
        dy = int(player_base_y - camera_y)
        cx = player_cx

        if self.swing_timer > 0:
            # Swing animation — arc the blade
            t = self.swing_timer / 10
            angle = -60 + (1 - t) * 120  # Sweep from -60 to +60 degrees
            rad = math.radians(angle * facing)
            blade_len = 22
            sx = cx + facing * 8
            sy = dy - 16
            ex = sx + int(math.cos(rad) * blade_len * facing)
            ey = sy + int(math.sin(rad) * blade_len)
            # Glow
            pygame.draw.line(surface, SWORD_GLOW, (sx, sy), (ex, ey), 5)
            # Blade
            pygame.draw.line(surface, SWORD_COLOR, (sx, sy), (ex, ey), 2)
        else:
            # Held at side
            sx = cx + facing * 7
            sy = dy - 18
            pygame.draw.line(surface, SWORD_GLOW, (sx, sy), (sx, sy + 14), 3)
            pygame.draw.line(surface, SWORD_COLOR, (sx, sy), (sx, sy + 14), 1)
            # Hilt
            pygame.draw.rect(surface, (80, 70, 60), (sx - 2, sy + 14, 5, 3))


class Pistol:
    def __init__(self):
        self.cooldown = 0

    def can_attack(self):
        return self.cooldown <= 0

    def attack(self, player_x, player_y, player_w, player_h, facing):
        """Returns (None, bullet_projectile)."""
        self.cooldown = PISTOL_COOLDOWN

        bx = player_x + player_w + 2 if facing == 1 else player_x - 8
        by = player_y + player_h // 2 - 2
        bullet = Bullet(bx, by, facing)

        return None, bullet

    def update(self):
        if self.cooldown > 0:
            self.cooldown -= 1

    def draw(self, surface, player_cx, player_base_y, facing, camera_y):
        """Draw the pistol on the player."""
        dy = int(player_base_y - camera_y)
        cx = player_cx

        # Gun body
        gx = cx + facing * 8
        gy = dy - 16
        pygame.draw.rect(surface, PISTOL_COLOR, (gx, gy, 8 * facing, 5) if facing == 1 else (gx - 8, gy, 8, 5))
        # Barrel
        bx = gx + (8 * facing) if facing == 1 else gx - 12
        pygame.draw.rect(surface, PISTOL_BARREL_COLOR, (bx, gy + 1, 4 * facing, 3) if facing == 1 else (bx, gy + 1, 4, 3))
