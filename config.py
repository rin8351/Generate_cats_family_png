"""
Configuration file for Cat Family Generator
Contains paths and generation parameters
"""

from typing import List, Tuple, Dict

from cats_colors import CATS_COLORS  # noqa: F401 — re-exported for convenience

# Color definitions
RGB = Tuple[int, int, int]

# Gray shades used in original cat images (will be replaced with colors)
GRAY_COLORS: List[RGB] = [
    (195, 195, 195), (212, 212, 212), (224, 224, 224),
    (235, 235, 235), (201, 201, 201), (194, 194, 194),
    (189, 189, 189), (181, 181, 181), (171, 171, 171),
    (247, 247, 247), (252, 252, 252)  # (252, 252, 252) is the main body color
]

# Folder paths for cat parts (all under parts/)
CAT_PARTS_FOLDERS: Dict[str, str] = {
    'ear': 'parts/ear',
    'eyes': 'parts/eyes',
    'body': 'parts/body',
    'tail': 'parts/tail',
    'legs': 'parts/legs',
}

# Generation parameters
GENERATION_PARAMS = {
    'background_color': (240, 255, 255),  # Background color for family image
    'font_name': 'arial.ttf',       # Font for cat names
    'font_size': 22,                # Font size (fits name + parents line)
    'text_color': (0, 0, 0),        # Text color
    'text_position': (0, 5),        # Text offset (x: from center, y: from bottom)
    'text_padding_bottom': 60,      # Extra space at bottom for multiline text
    'column_gap': 48,               # Gap between pedigree generation columns
    'connector_color': (80, 80, 80),  # Pedigree link line color
    'connector_width': 2,           # Pedigree link line width
}

# Output settings
OUTPUT_SETTINGS = {
    'default_filename': 'cats_family.png',
    'format': 'PNG',
    'quality': 95,
}

# Names file path
NAMES_FILE = 'cats_name.TXT'

# Logging configuration
LOGGING_CONFIG = {
    'level': 'INFO',
    'format': '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    'filename': 'cat_generator.log',
}
