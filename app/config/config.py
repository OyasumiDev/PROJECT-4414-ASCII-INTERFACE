import os
from dotenv import load_dotenv

load_dotenv()

CAM_INDEX       = int(os.getenv("CAM_INDEX", 0))
DEFAULT_COLS    = int(os.getenv("DEFAULT_COLS", 100))
DEFAULT_FPS     = int(os.getenv("DEFAULT_FPS", 15))
DEFAULT_FONT_SIZE = int(os.getenv("DEFAULT_FONT_SIZE", 8))
DEFAULT_INVERT  = os.getenv("DEFAULT_INVERT", "false").lower() == "true"
DEFAULT_CHARSET = os.getenv("DEFAULT_CHARSET", "SIMPLE")
DEFAULT_BRIGHTNESS = int(os.getenv("DEFAULT_BRIGHTNESS", 115))  # 100 = neutro, >100 aclara

APP_TITLE = "ASCII Cam"
APP_WIDTH = 1200
APP_HEIGHT = 750
