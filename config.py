"""
Configuration file for Cat Family Generator
Contains paths and generation parameters
"""

from typing import List, Tuple, Dict

# How many colors a child inherits — probabilities as % (out of 100)
# Edit the numbers freely. They are normalized if the sum is not exactly 100.
# Set a weight to 0 to disable that count.

CHILD_COLOR_COUNT_WEIGHTS: Dict[int, float] = {
    2: 10,   # 10%
    3: 25,   # 25%
    4: 40,   # 40%
    5: 20,   # 20%
    6: 5,    # 5%
}

GENERATION_PARAMS = {
    'background_color': (240, 255, 255),  # Background color for family image
    'font_name': 'arial.ttf',       # Font for cat names
    'font_size': 28,                # Font size for name + generation
    'gene_font_size': 22,           # Font size for color-strength lines
    'text_color': (0, 0, 0),        # Text color
    'text_position': (0, 8),        # Text offset (x: from center, y: from bottom)
    'text_padding_bottom': 200,     # Space for name + up to 5 color strength lines
    'swatch_size': 18,              # Color swatch side length (px)
    'column_gap': 48,               # Gap between pedigree generation columns
    'connector_color': (80, 80, 80),  # Pedigree link line color
    'connector_width': 2,           # Pedigree link line width
}


# Genetics parameters (gene "strength" system)
GENETICS_PARAMS = {
    'base_strength': 1.0,         
    'match_bonus': 1.0,           
    'win_bonus': 0.5,              
    # Extra strength when a color claims the main body gray (252, 252, 252).
    # Stacks across generations so main colors dominate by Gen 2–3.
    'main_body_bonus': 1.0,
    'random_innate_jitter': 0.0,  # +/- random spread of innate strength (0 = off)
    'child_color_count_weights': CHILD_COLOR_COUNT_WEIGHTS,
    # From this generation onward, child colors are the top-N by strength
    # (no lottery for weak accent colors). Gen 1 stays weighted-random.
    'strict_color_from_generation': 2,
    # Sometimes also take the next color by strength (e.g. 5th after top-4).
    # Not a mutation — just a chance the runner-up allele sneaks in.
    'spillover_chance': 0.25,
    # Rare: add one extra weak gene from Gen 0/1 lineage colors (heritable)
    'mutation_chance': 0.1,
    'mutation_strength': 0.5,
}


RGB = Tuple[int, int, int]

# Gray shades used in original cat images (will be replaced with colors)
GRAY_COLORS: List[RGB] = [
    (195, 195, 195), (212, 212, 212), (224, 224, 224),
    (235, 235, 235), (201, 201, 201), (194, 194, 194),
    (189, 189, 189), (181, 181, 181), (171, 171, 171),
    (247, 247, 247), (252, 252, 252)  # (252, 252, 252) is the main body color
]

CAT_PARTS_FOLDERS: Dict[str, str] = {
    'ear': 'parts/ear',
    'eyes': 'parts/eyes',
    'body': 'parts/body',
    'tail': 'parts/tail',
    'legs': 'parts/legs',
}


OUTPUT_SETTINGS = {
    'default_filename': 'cats_family.png',
    'format': 'PNG',
    'quality': 95,
}

NAMES_FILE = 'cats_name.TXT'

SEEDS_FILE = 'seeds.json'

LOGGING_CONFIG = {
    'level': 'INFO',
    'format': '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    'filename': 'cat_generator.log',
}
