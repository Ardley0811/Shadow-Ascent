# File paths for saving and loading data
SETTINGS_FILE = "assets/settings/settings.json" # Path to the settings JSON file
SAVE_FILE = "saves/save.json" # Path to the saved game file

# Fonts and text sizes
FONT_NAME = "Arial"
MAIN_TITLE_FONT_SIZE = 72
FONT_SIZE = 28
GAME_OVER_FONT_SIZE = 64
GAME_OVER_OPTIONS_FONT_SIZE = 36

FPS = 60 # Frames per second

# Screen geometry
DISPLAY_WIDTH = 640 # Internal render resolution width
DISPLAY_HEIGHT = 360 # Internal render resolution height
WINDOW_WIDTH = 1280 # Actual window width
WINDOW_HEIGHT = 720 # Actual window height

START_POS= [3, 300] # Starting player position in pixels

TILE_SIZE = 16 # Size of a single tile in pixels

# Maths
FRICTION = 0.8
SPEED = 0.5
SLASH_ARC_START_ANGLE = -0.8
SLASH_ARC_END_ANGLE = 0.8
PI = 3.14

# Colours
PURPLE = (50, 30, 90)
DARK_PURPLE = (40, 0, 60)
LIGHT_PURPLE = (200, 100, 255)
LIGHT_GREY = (150, 150, 150)
YELLOW = (255, 255, 0)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
DARK_BLUE = (60, 80, 120)
DARK_GREY = (30, 30, 30)
LIGHT_RED = (255, 50, 50)
CYAN = (0, 200, 255)
LIGHT_BLUE = (200, 200, 255)
LIGHT_GREEN = (80, 255, 120)
DARK_RED = (50, 0, 0)
RED = (255, 0, 0)
SLATE_BLUE = (120, 120, 200)
LIGHT_PINK = (255, 200, 200)
GREEN = (0, 255, 0)

# Chapters and their starting levels
CHAPTER_LEVELS = {
        1: 0,
        2: 5,
        3: 10,
        4: 15,
        5: 20
    }

# Health
HEALTH_BAR_X = 10 # X-position of health bar
HEALTH_BAR_Y = 10 # Y-position of health bar
HEALTH_BAR_WIDTH = 100 # Width of health bar
HEALTH_BAR_HEIGHT = 10 # Height of health bar


STAMINA_BAR_WIDTH = 100 # Width of stamina bar
STAMINA_BAR_HEIGHT = 8 # Height of stamina bar
STAMINA_X = 10 # X-position of stamina bar
STAMINA_Y = 30 # Y-position of stamina bar

# Tile types that cause hazards
HAZARD_TILES = {'spike', 'ice_spike', 'lava_spike', 'cosmic_spike'}

RENDER_SCALE = 2.0 # Scale factor when rendering the internal display to the window
MAX_MAP_INDEX = 24 # Highest map index in the game