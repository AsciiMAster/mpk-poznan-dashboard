from pathlib import Path
from dotenv import load_dotenv
import os

load_dotenv()

# Ścieżki
BASE_DIR = Path(__file__).parent

# Ustawienie mapy
MAP_CENTER = [52.4064, 16.9252]
MAP_ZOOM = 13
EPSG_LOCAL = 2180