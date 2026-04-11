import pygame
import math
from settings import (
    ROBOT_COLOR, ROBOT_EYE_COLOR, ROBOT_ACCENT, ROBOT_HP,
    ROBOT_SPEED, ROBOT_WIDTH, ROBOT_HEIGHT, SCREEN_HEIGHT,
    GRAVITY, MAX_FALL_SPEED, WORLD_WIDTH, WALL_THICKNESS,
)


class Robot:
    """Cyberpunk robot enemy that patrols on platforms."""

    def __init__(self, x, y, patrol_left, patrol_right):
        self.x = x
        self.y = y
        self.width = ROBOT_WIDTH
        self.height = ROBOT_HEIGHT
        self.hp = ROBOT_HP
        self.max_hp = ROBOT_HP
        self.alive = True

        # Patrol bounds
        self.patrol_left = patrol_left
        self.patrol_right = patrol_right
        self.direction = 1  # 1 right, -1 left
        self.speed = ROBOT_SPEED

        # Animation
        self.anim_timer = 0.0
        self.hit_flash = 0  # Frames of white flash when hit
        self.death_timer = 0  # Explosion animation

        # Physics
        self.vel_y = 0.0
        self.on_ground = False

    @property
    def rect(self):
        return pygame.Rect(int(self.x), int(self.y), self.width, self.height)

    def take_damage(self, amount):
        self.hp -= amount
        self.hit_flash = 6
        if self.hp <= 0:
            self.hp = 0
            self.alive = False
            self.death_timer = 20

    def update(self, platforms):
        if not self.alive:
            self.death_timer -= 1
            return

        # Patrol movement
        self.x += self.speed * self.direction
        self.anim_timer += 0.1

        # Reverse at patrol bounds
        if self.x <= self.patrol_left:
            self.x = self.patrol_left
            self.direction = 1
        elif self.x + self.width >= self.patrol_right:
            self.x = self.patrol_right - self.width
            self.direction = -1

        # Gravity
        self.vel_y += GRAVITY
        if self.vel_y > MAX_FALL_SPEED:
            self.vel_y = MAX_FALL_SPEED
        self.y += self.vel_y

        # Collision with platforms
        self.on_ground = False
        my_rect = self.rect
        for plat in platforms:
            if my_rect.colliderect(plat.rect):
                if self.vel_y > 0 and my_rect.bottom > plat.rect.top and my_rect.top < plat.rect.top:
                    self.y = plat.rect.top - self.height
                    self.vel_y = 0
                    self.on_ground = True

        # Hit flash countdown
        if self.hit_flash > 0:
            self.hit_flash -= 1

    def draw(self, surface, camera_y):
        dy = int(self.y - camera_y)
        if dy < -50 or dy > SCREEN_HEIGHT + 50:
            return

        dx = int(self.x)

        if not self.alive:
            # Death explosion
            self._draw_explosion(surface, dx, dy)
            return

        # Flash white when hit
        body_color = (255, 255, 255) if self.hit_flash > 0 else ROBOT_COLOR
        accent = (255, 255, 255) if self.hit_flash > 0 else ROBOT_ACCENT

        # Legs (walk animation)
        leg_offset = int(math.sin(self.anim_timer * 3) * 3)
        pygame.draw.rect(surface, body_color, (dx + 3 + leg_offset, dy + 20, 5, 8))
        pygame.draw.rect(surface, body_color, (dx + 16 - leg_offset, dy + 20, 5, 8))

        # Feet
        pygame.draw.rect(surface, accent, (dx + 2 + leg_offset, dy + 26, 7, 3))
        pygame.draw.rect(surface, accent, (dx + 15 - leg_offset, dy + 26, 7, 3))

        # Body (boxy robot torso)
        pygame.draw.rect(surface, body_color, (dx + 2, dy + 8, 20, 14))
        # Chest panel
        pygame.draw.rect(surface, accent, (dx + 6, dy + 10, 12, 4))
        # Core light (pulsing)
        pulse = int(abs(math.sin(self.anim_timer * 2)) * 50)
        core_color = (min(255, ROBOT_EYE_COLOR[0] + pulse), 20, 20)
        pygame.draw.rect(surface, core_color, (dx + 10, dy + 15, 4, 3))

        # Head
        pygame.draw.rect(surface, body_color, (dx + 5, dy, 14, 10))
        # Visor / eyes
        eye_x_offset = 2 if self.direction == 1 else 0
        pygame.draw.rect(surface, ROBOT_EYE_COLOR, (dx + 7 + eye_x_offset, dy + 3, 8, 3))
        # Antenna
        pygame.draw.line(surface, accent, (dx + 12, dy), (dx + 12, dy - 5), 1)
        pygame.draw.circle(surface, ROBOT_EYE_COLOR, (dx + 12, dy - 6), 2)

        # Arms
        arm_swing = int(math.sin(self.anim_timer * 3) * 2)
        pygame.draw.rect(surface, body_color, (dx - 2, dy + 10 + arm_swing, 4, 10))
        pygame.draw.rect(surface, body_color, (dx + 22, dy + 10 - arm_swing, 4, 10))

        # HP bar
        if self.hp < self.max_hp:
            bar_w = self.width
            bar_h = 3
            bar_x = dx
            bar_y = dy - 6
            pygame.draw.rect(surface, (60, 0, 0), (bar_x, bar_y, bar_w, bar_h))
            fill = int(bar_w * (self.hp / self.max_hp))
            pygame.draw.rect(surface, ROBOT_EYE_COLOR, (bar_x, bar_y, fill, bar_h))

    def _draw_explosion(self, surface, dx, dy):
        """Simple pixel explosion on death."""
        t = (20 - self.death_timer) / 20  # 0 to 1
        radius = int(t * 25)
        alpha = int((1 - t) * 200)

        # Expanding rings
        for i in range(3):
            r = radius - i * 5
            if r > 0:
                color = ROBOT_ACCENT if i % 2 == 0 else ROBOT_EYE_COLOR
                pygame.draw.circle(surface, color,
                                   (dx + self.width // 2, dy + self.height // 2), r, 2)

        # Debris pixels
        import random
        random.seed(int(self.x * 100 + self.y))
        for _ in range(8):
            ox = random.randint(-radius, radius)
            oy = random.randint(-radius, radius)
            size = random.randint(2, 4)
            pygame.draw.rect(surface, ROBOT_COLOR,
                             (dx + self.width // 2 + ox, dy + self.height // 2 + oy, size, size))
