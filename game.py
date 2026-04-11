import pygame
import sys
import random
from settings import (
    SCREEN_WIDTH, SCREEN_HEIGHT, FPS, TITLE, BG_COLOR,
    TEXT_COLOR, WORLD_HEIGHT, PEAK_COLOR, CYBER_GREEN,
    CYBER_PURPLE, CYBER_BLUE, CYBER_RED,
    WALL_THICKNESS, WORLD_WIDTH, SWORD_COLOR, ENERGY_WAVE_COLOR,
)
from player import Player
from level import Level
from camera import Camera
from weapons import CyberSword, Pistol
from enemies import Robot
from pickups import Pickup


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

        # Combat systems
        self.weapons = []          # Available weapons [CyberSword, Pistol, ...]
        self.current_weapon = 0    # Index into self.weapons
        self.projectiles = []      # Active bullets / energy waves
        self.enemies = []
        self.pickups = []
        self.kills = 0

        self._spawn_pickups()
        self._spawn_enemies()

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
                if event.key == pygame.K_z and not self.won:
                    self._attack()
                if event.key == pygame.K_x and not self.won:
                    self._switch_weapon()

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

        # Update weapons
        for w in self.weapons:
            w.update()

        # Update projectiles
        for proj in self.projectiles:
            proj.update()
        self.projectiles = [p for p in self.projectiles if p.alive]

        # Update enemies
        nearby_plats = self.level.get_nearby_platforms(self.player.y, margin=SCREEN_HEIGHT * 2)
        for enemy in self.enemies:
            enemy.update(nearby_plats)
        # Remove dead enemies whose explosion finished
        self.enemies = [e for e in self.enemies if e.alive or e.death_timer > 0]

        # Projectile-enemy collisions
        for proj in self.projectiles:
            if not proj.alive:
                continue
            for enemy in self.enemies:
                if not enemy.alive:
                    continue
                if proj.rect.colliderect(enemy.rect):
                    enemy.take_damage(proj.damage)
                    proj.alive = False
                    if not enemy.alive:
                        self.kills += 1
                    break

        # Pickup collisions
        player_rect = self.player.rect
        for pickup in self.pickups:
            if pickup.collected:
                continue
            if player_rect.colliderect(pickup.rect):
                self._collect_pickup(pickup)

        # Update pickups (bob animation)
        for pickup in self.pickups:
            pickup.update()

    def _draw(self):
        self.screen.fill(BG_COLOR)

        # Draw background depth lines for atmosphere
        self._draw_background()

        # Level
        self.level.draw(self.screen, self.camera.y)

        # Pickups
        for pickup in self.pickups:
            pickup.draw(self.screen, self.camera.y)

        # Enemies
        for enemy in self.enemies:
            enemy.draw(self.screen, self.camera.y)

        # Projectiles
        for proj in self.projectiles:
            proj.draw(self.screen, self.camera.y)

        # Player
        self.player.draw(self.screen, self.camera.y)

        # Current weapon on player
        if self.weapons:
            weapon = self.weapons[self.current_weapon]
            cx = int(self.player.x) + self.player.width // 2
            base_y = self.player.y + self.player.height
            weapon.draw(self.screen, cx, base_y, self.player.facing, self.camera.y)

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

        # Kill counter
        if self.kills > 0:
            kill_text = f"Kills: {self.kills}"
            kill_surf = self.font.render(kill_text, True, CYBER_GREEN)
            self.screen.blit(kill_surf, (10, 70))

        # Weapon indicator
        if self.weapons:
            weapon = self.weapons[self.current_weapon]
            wname = type(weapon).__name__
            label = "Cyber Sword" if wname == "CyberSword" else "Pistol"
            if wname == "CyberSword" and weapon.upgraded:
                label += " [WAVE]"
            weapon_surf = self.font.render(f"[Z] {label}  [X] Switch", True, SWORD_COLOR)
            self.screen.blit(weapon_surf, (SCREEN_WIDTH // 2 - weapon_surf.get_width() // 2, SCREEN_HEIGHT - 25))
        else:
            hint_surf = self.font.render("Find a weapon!", True, (120, 120, 140))
            self.screen.blit(hint_surf, (SCREEN_WIDTH // 2 - hint_surf.get_width() // 2, SCREEN_HEIGHT - 25))

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

        falls_text = self.med_font.render(f"Falls: {self.fall_count}  |  Kills: {self.kills}", True, TEXT_COLOR)
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
        self.weapons = []
        self.current_weapon = 0
        self.projectiles = []
        self.enemies = []
        self.pickups = []
        self.kills = 0
        self._spawn_pickups()
        self._spawn_enemies()

    def _attack(self):
        """Handle Z key — attack with current weapon."""
        if not self.weapons:
            return
        weapon = self.weapons[self.current_weapon]
        if not weapon.can_attack():
            return

        hit_rect, proj = weapon.attack(
            self.player.x, self.player.y,
            self.player.width, self.player.height,
            self.player.facing,
        )

        # Melee hit check (sword)
        if hit_rect is not None:
            for enemy in self.enemies:
                if enemy.alive and hit_rect.colliderect(enemy.rect):
                    from settings import SWORD_DAMAGE
                    enemy.take_damage(SWORD_DAMAGE)
                    if not enemy.alive:
                        self.kills += 1

        # Projectile (bullet or energy wave)
        if proj is not None:
            self.projectiles.append(proj)

    def _switch_weapon(self):
        """Handle X key — cycle weapons."""
        if len(self.weapons) > 1:
            self.current_weapon = (self.current_weapon + 1) % len(self.weapons)

    def _collect_pickup(self, pickup):
        """Handle collecting a pickup item."""
        pickup.collected = True

        if pickup.pickup_type == "sword":
            # Only add if we don't already have one
            if not any(isinstance(w, CyberSword) for w in self.weapons):
                self.weapons.append(CyberSword())
                self.current_weapon = len(self.weapons) - 1

        elif pickup.pickup_type == "pistol":
            if not any(isinstance(w, Pistol) for w in self.weapons):
                self.weapons.append(Pistol())
                self.current_weapon = len(self.weapons) - 1

        elif pickup.pickup_type == "wave_upgrade":
            # Upgrade existing sword, or give sword + upgrade
            sword = None
            for w in self.weapons:
                if isinstance(w, CyberSword):
                    sword = w
                    break
            if sword is None:
                sword = CyberSword()
                self.weapons.append(sword)
            sword.upgraded = True
            # Switch to sword to show off
            self.current_weapon = self.weapons.index(sword)

    def _spawn_pickups(self):
        """Place weapon pickups and upgrades on specific platforms."""
        plats = [p for p in self.level.platforms
                 if p.rect.width >= 60 and p.rect.y < WORLD_HEIGHT - 50]

        if len(plats) < 5:
            return

        random.seed(99)  # Deterministic placement
        random.shuffle(plats)

        # Sword near bottom (easy to find early)
        bottom_plats = [p for p in plats if p.rect.y > WORLD_HEIGHT * 0.7]
        if bottom_plats:
            p = bottom_plats[0]
            self.pickups.append(Pickup(
                p.rect.centerx, p.rect.top - 12, "sword"
            ))

        # Pistol in mid-section
        mid_plats = [p for p in plats if WORLD_HEIGHT * 0.35 < p.rect.y < WORLD_HEIGHT * 0.65]
        if mid_plats:
            p = mid_plats[0]
            self.pickups.append(Pickup(
                p.rect.centerx, p.rect.top - 12, "pistol"
            ))

        # Energy wave upgrade higher up (reward for climbing)
        high_plats = [p for p in plats if WORLD_HEIGHT * 0.15 < p.rect.y < WORLD_HEIGHT * 0.35]
        if high_plats:
            p = high_plats[0]
            self.pickups.append(Pickup(
                p.rect.centerx, p.rect.top - 12, "wave_upgrade"
            ))

    def _spawn_enemies(self):
        """Place robot enemies on platforms throughout the level."""
        plats = [p for p in self.level.platforms
                 if p.rect.width >= 80 and 200 < p.rect.y < WORLD_HEIGHT - 200]

        random.seed(77)  # Deterministic
        random.shuffle(plats)

        # Place a robot on ~every 5th suitable platform
        count = 0
        for i, plat in enumerate(plats):
            if i % 5 != 0:
                continue
            r = plat.rect
            robot = Robot(
                x=r.x + 10,
                y=r.top - 30,
                patrol_left=r.left + 2,
                patrol_right=r.right - 2,
            )
            self.enemies.append(robot)
            count += 1
            if count >= 12:
                break


if __name__ == "__main__":
    game = Game()
    game.run()
