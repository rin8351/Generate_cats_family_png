"""
Configuration file for Cat Family Generator
Contains all color palettes, paths, and generation parameters
"""

from typing import List, Tuple, Dict

# Color definitions
RGB = Tuple[int, int, int]

# Gray shades used in original cat images (will be replaced with colors)
GRAY_COLORS: List[RGB] = [
    (195, 195, 195), (212, 212, 212), (224, 224, 224),
    (235, 235, 235), (201, 201, 201), (194, 194, 194),
    (189, 189, 189), (181, 181, 181), (171, 171, 171),
    (247, 247, 247), (252, 252, 252)  # (252, 252, 252) is the main body color
]

# Cat color palette - vibrant and pastel colors
CATS_COLORS: List[RGB] = [
    # Vibrant colors
    (255, 0, 0),      # Red
    (0, 0, 255),      # Blue
    (0, 128, 0),      # Green
    (255, 255, 0),    # Yellow
    (255, 165, 0),    # Orange
    (255, 192, 203),  # Pink
    (128, 0, 128),    # Purple
    (165, 42, 42),    # Brown
    (128, 128, 128),  # Gray
    (50, 205, 50),    # Lime
    (0, 255, 255),    # Cyan
    (255, 0, 255),    # Magenta
    (128, 128, 0),    # Olive
    # Pastel colors
    (230, 230, 250),  # Lavender
    (135, 206, 250),  # Light Sky Blue
    (152, 251, 152),  # Pale Green
    (255, 218, 185),  # Peach
    (255, 182, 193),  # Light Pink
    (240, 128, 128),  # Light Coral
    (255, 255, 224),  # Light Yellow
    (216, 191, 216),  # Thistle
    (245, 245, 220),  # Beige
    (175, 238, 238),  # Pale Turquoise
    (255, 228, 225),  # Misty Rose
    (250, 250, 210),  # Light Goldenrod
    (255, 229, 180),  # Peach Puff
    (245, 255, 250),  # Mint Cream
]

# Folder paths for cat parts
CAT_PARTS_FOLDERS: Dict[str, str] = {
    'ear': 'ear',
    'eyes': 'eyes',
    'body': 'body',
    'tail': 'tail',
    'legs': 'legs',
}

# Generation parameters
GENERATION_PARAMS = {
    'background_color': (240, 255, 255),  # Background color for family image
    'font_name': 'arial.ttf',       # Font for cat names
    'font_size': 26,                # Font size (reduced for longer names with Gen info)
    'text_color': (0, 0, 0),        # Text color
    'text_position': (10, 5),       # Text position on cat image (x: left offset, y: top offset)
    'text_padding_bottom': 35,      # Extra space at bottom for text
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

