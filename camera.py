from settings import SCREEN_HEIGHT, WORLD_HEIGHT


class Camera:
    def __init__(self):
        self.y = WORLD_HEIGHT - SCREEN_HEIGHT  # Start at bottom

    def update(self, player_y: float):
        """Follow player vertically, keeping them in the middle-lower area."""
        target = player_y - SCREEN_HEIGHT * 0.55
        # Smooth follow
        self.y += (target - self.y) * 0.1

        # Clamp to world bounds
        if self.y < 0:
            self.y = 0
        if self.y > WORLD_HEIGHT - SCREEN_HEIGHT:
            self.y = WORLD_HEIGHT - SCREEN_HEIGHT
