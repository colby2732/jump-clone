# --- Display ---
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
FPS = 60
TITLE = "Jump Clone"

# --- Colors ---
BG_COLOR = (15, 15, 25)
PLATFORM_COLOR = (80, 80, 100)
PLATFORM_EDGE_COLOR = (100, 100, 120)
PLAYER_COLOR = (220, 50, 50)
PLAYER_OUTLINE = (160, 30, 30)
CHARGE_BAR_BG = (40, 40, 50)
CHARGE_BAR_FG = (50, 220, 80)
CHARGE_BAR_MAX = (220, 50, 50)
TEXT_COLOR = (200, 200, 210)
GROUND_COLOR = (60, 70, 60)
WALL_COLOR = (50, 50, 65)
PEAK_COLOR = (255, 215, 0)
CAPE_COLOR = (180, 30, 30)

# --- Cyberpunk Background ---
CYBER_GREEN = (0, 255, 100)
CYBER_PURPLE = (150, 0, 255)
CYBER_BLUE = (0, 100, 255)
CYBER_RED = (255, 50, 50)

# --- Physics ---
GRAVITY = 0.55
MAX_FALL_SPEED = 16

# --- Jump Charge ---
CHARGE_RATE = 1.2          # How fast the bar fills per frame
MAX_CHARGE = 100           # Full charge value
MIN_JUMP_POWER = 4         # Minimum jump velocity (tap)
MAX_JUMP_POWER = 17        # Maximum jump velocity (full charge)
HORIZONTAL_JUMP_SPEED = 4  # Horizontal speed during jump (left/right on launch)

# --- Player ---
PLAYER_WIDTH = 20
PLAYER_HEIGHT = 28
PLAYER_GROUND_SPEED = 3    # Walk speed on ground only

# --- World ---
WORLD_WIDTH = SCREEN_WIDTH
WORLD_HEIGHT = 8000        # Total vertical height
WALL_THICKNESS = 20        # Side walls

# --- Weapons ---
SWORD_COLOR = (0, 220, 255)        # Cyan cyber blade
SWORD_GLOW = (0, 180, 255)
SWORD_RANGE = 40                   # Melee range in pixels
SWORD_DAMAGE = 1
SWORD_COOLDOWN = 20                # Frames between swings
ENERGY_WAVE_COLOR = (0, 255, 220)  # Teal energy wave
ENERGY_WAVE_SPEED = 7
ENERGY_WAVE_DAMAGE = 2
ENERGY_WAVE_LIFETIME = 60          # Frames before it fades

PISTOL_COLOR = (180, 180, 190)
PISTOL_BARREL_COLOR = (120, 120, 130)
BULLET_COLOR = (255, 200, 50)
BULLET_SPEED = 10
BULLET_DAMAGE = 1
PISTOL_COOLDOWN = 15               # Frames between shots

# --- Enemies ---
ROBOT_COLOR = (160, 160, 180)
ROBOT_EYE_COLOR = (255, 50, 50)
ROBOT_ACCENT = (0, 200, 255)
ROBOT_HP = 3
ROBOT_SPEED = 1.2
ROBOT_WIDTH = 24
ROBOT_HEIGHT = 28

# --- Pickups ---
PICKUP_GLOW = (255, 255, 100)
PICKUP_SIZE = 16
