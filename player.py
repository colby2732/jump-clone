import pygame
import math
from settings import (
    GRAVITY, MAX_FALL_SPEED, CHARGE_RATE, MAX_CHARGE,
    MIN_JUMP_POWER, MAX_JUMP_POWER, HORIZONTAL_JUMP_SPEED,
    PLAYER_WIDTH, PLAYER_HEIGHT, PLAYER_GROUND_SPEED,
    PLAYER_COLOR, PLAYER_OUTLINE, CHARGE_BAR_BG, CHARGE_BAR_FG,
    CHARGE_BAR_MAX, WORLD_WIDTH, WALL_THICKNESS,
)

# Character colors
SKIN_COLOR = (225, 185, 145)
HAIR_COLOR = (60, 40, 25)
SHIRT_COLOR = (50, 90, 170)
PANTS_COLOR = (60, 60, 75)
SHOE_COLOR = (40, 35, 30)
EYE_COLOR = (255, 255, 255)
PUPIL_COLOR = (30, 30, 30)


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
        self.facing = 1  # -1 left, 1 right (default facing right)

        # Animation
        self.anim_timer = 0.0  # Walk cycle timer
        self.walk_frame = 0

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
            self.anim_timer = 0

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
                self.anim_timer += 0.15
            elif keys[pygame.K_RIGHT] or keys[pygame.K_d]:
                self.vel_x = PLAYER_GROUND_SPEED
                self.facing = 1
                self.anim_timer += 0.15
            else:
                self.anim_timer = 0

            # Start charging
            if keys[pygame.K_SPACE]:
                self.charging = True
                self.charge = 0
                self.vel_x = 0
                self.anim_timer = 0

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
        cx = int(self.x) + self.width // 2  # Center X
        base_y = int(self.y - camera_y) + self.height  # Feet Y

        if self.charging:
            self._draw_crouching(surface, cx, base_y)
        elif not self.on_ground:
            self._draw_airborne(surface, cx, base_y)
        elif abs(self.vel_x) > 0.1:
            self._draw_walking(surface, cx, base_y)
        else:
            self._draw_standing(surface, cx, base_y)

    def _draw_standing(self, surface, cx, base_y):
        f = self.facing
        # Shoes
        pygame.draw.rect(surface, SHOE_COLOR, (cx - 6, base_y - 4, 5, 4))
        pygame.draw.rect(surface, SHOE_COLOR, (cx + 1, base_y - 4, 5, 4))
        # Legs
        pygame.draw.rect(surface, PANTS_COLOR, (cx - 5, base_y - 12, 4, 8))
        pygame.draw.rect(surface, PANTS_COLOR, (cx + 1, base_y - 12, 4, 8))
        # Torso
        pygame.draw.rect(surface, SHIRT_COLOR, (cx - 6, base_y - 22, 12, 10))
        # Head
        pygame.draw.rect(surface, SKIN_COLOR, (cx - 5, base_y - 30, 10, 8))
        # Hair
        pygame.draw.rect(surface, HAIR_COLOR, (cx - 5, base_y - 32, 10, 3))
        # Eye
        eye_x = cx + (2 * f)
        pygame.draw.rect(surface, EYE_COLOR, (eye_x, base_y - 28, 3, 3))
        pygame.draw.rect(surface, PUPIL_COLOR, (eye_x + 1, base_y - 27, 1, 1))

    def _draw_walking(self, surface, cx, base_y):
        f = self.facing
        # Leg animation — swing based on timer
        leg_swing = int(math.sin(self.anim_timer * 2) * 4)

        # Left leg
        l_leg_x = cx - 5 + leg_swing
        pygame.draw.rect(surface, PANTS_COLOR, (l_leg_x, base_y - 12, 4, 8))
        pygame.draw.rect(surface, SHOE_COLOR, (l_leg_x - 1, base_y - 4, 5, 4))

        # Right leg (opposite swing)
        r_leg_x = cx + 1 - leg_swing
        pygame.draw.rect(surface, PANTS_COLOR, (r_leg_x, base_y - 12, 4, 8))
        pygame.draw.rect(surface, SHOE_COLOR, (r_leg_x, base_y - 4, 5, 4))

        # Torso (slight bob)
        bob = int(abs(math.sin(self.anim_timer * 2)) * 1)
        pygame.draw.rect(surface, SHIRT_COLOR, (cx - 6, base_y - 22 - bob, 12, 10))

        # Arm swing
        arm_swing = int(math.sin(self.anim_timer * 2) * 3)
        pygame.draw.rect(surface, SHIRT_COLOR, (cx - 8, base_y - 20 - bob + arm_swing, 3, 7))
        pygame.draw.rect(surface, SHIRT_COLOR, (cx + 5, base_y - 20 - bob - arm_swing, 3, 7))

        # Head
        pygame.draw.rect(surface, SKIN_COLOR, (cx - 5, base_y - 30 - bob, 10, 8))
        pygame.draw.rect(surface, HAIR_COLOR, (cx - 5, base_y - 32 - bob, 10, 3))
        # Eye
        eye_x = cx + (2 * f)
        pygame.draw.rect(surface, EYE_COLOR, (eye_x, base_y - 28 - bob, 3, 3))
        pygame.draw.rect(surface, PUPIL_COLOR, (eye_x + 1, base_y - 27 - bob, 1, 1))

    def _draw_crouching(self, surface, cx, base_y):
        f = self.facing
        charge_pct = self.charge / MAX_CHARGE
        crouch = int(charge_pct * 6)  # Crouch deeper with more charge

        # Shoes (wider stance)
        pygame.draw.rect(surface, SHOE_COLOR, (cx - 7, base_y - 4, 5, 4))
        pygame.draw.rect(surface, SHOE_COLOR, (cx + 2, base_y - 4, 5, 4))
        # Bent legs
        pygame.draw.rect(surface, PANTS_COLOR, (cx - 6, base_y - 10 + crouch, 5, 6 - crouch // 2))
        pygame.draw.rect(surface, PANTS_COLOR, (cx + 1, base_y - 10 + crouch, 5, 6 - crouch // 2))
        # Torso (lowered)
        pygame.draw.rect(surface, SHIRT_COLOR, (cx - 6, base_y - 18 + crouch, 12, 8))
        # Arms tucked
        pygame.draw.rect(surface, SHIRT_COLOR, (cx - 8, base_y - 16 + crouch, 3, 5))
        pygame.draw.rect(surface, SHIRT_COLOR, (cx + 5, base_y - 16 + crouch, 3, 5))
        # Head (lowered)
        pygame.draw.rect(surface, SKIN_COLOR, (cx - 5, base_y - 26 + crouch, 10, 8))
        pygame.draw.rect(surface, HAIR_COLOR, (cx - 5, base_y - 28 + crouch, 10, 3))
        # Eye — focused look
        eye_x = cx + (2 * f)
        pygame.draw.rect(surface, EYE_COLOR, (eye_x, base_y - 24 + crouch, 3, 2))
        pygame.draw.rect(surface, PUPIL_COLOR, (eye_x + 1, base_y - 24 + crouch, 1, 1))

    def _draw_airborne(self, surface, cx, base_y):
        f = self.facing
        going_up = self.vel_y < 0

        if going_up:
            # Legs tucked up
            pygame.draw.rect(surface, PANTS_COLOR, (cx - 5, base_y - 10, 4, 6))
            pygame.draw.rect(surface, PANTS_COLOR, (cx + 1, base_y - 10, 4, 6))
            pygame.draw.rect(surface, SHOE_COLOR, (cx - 5, base_y - 4, 5, 4))
            pygame.draw.rect(surface, SHOE_COLOR, (cx + 1, base_y - 4, 5, 4))
            # Arms up
            pygame.draw.rect(surface, SHIRT_COLOR, (cx - 8, base_y - 24, 3, 6))
            pygame.draw.rect(surface, SHIRT_COLOR, (cx + 5, base_y - 24, 3, 6))
        else:
            # Legs dangling
            pygame.draw.rect(surface, PANTS_COLOR, (cx - 5, base_y - 11, 4, 7))
            pygame.draw.rect(surface, PANTS_COLOR, (cx + 1, base_y - 11, 4, 7))
            pygame.draw.rect(surface, SHOE_COLOR, (cx - 6, base_y - 4, 5, 4))
            pygame.draw.rect(surface, SHOE_COLOR, (cx + 2, base_y - 4, 5, 4))
            # Arms flailing
            flail = int(math.sin(pygame.time.get_ticks() * 0.01) * 2)
            pygame.draw.rect(surface, SHIRT_COLOR, (cx - 9, base_y - 19 + flail, 3, 6))
            pygame.draw.rect(surface, SHIRT_COLOR, (cx + 6, base_y - 19 - flail, 3, 6))

        # Torso
        pygame.draw.rect(surface, SHIRT_COLOR, (cx - 6, base_y - 22, 12, 10))
        # Head
        pygame.draw.rect(surface, SKIN_COLOR, (cx - 5, base_y - 30, 10, 8))
        pygame.draw.rect(surface, HAIR_COLOR, (cx - 5, base_y - 32, 10, 3))
        # Eye
        eye_x = cx + (2 * f)
        if going_up:
            pygame.draw.rect(surface, EYE_COLOR, (eye_x, base_y - 28, 3, 3))
            pygame.draw.rect(surface, PUPIL_COLOR, (eye_x + 1, base_y - 28, 1, 1))  # Looking up
        else:
            pygame.draw.rect(surface, EYE_COLOR, (eye_x, base_y - 27, 3, 4))  # Wide eyes falling
            pygame.draw.rect(surface, PUPIL_COLOR, (eye_x + 1, base_y - 26, 1, 1))

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
