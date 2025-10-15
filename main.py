#!/usr/bin/env python3
"""
Cat Family Generator - Main Entry Point

Generates a family tree of cats with genetic inheritance of colors and body parts.
Each generation inherits traits from parents following simplified genetic rules.

"""

import os
import sys
import random
import logging
import argparse
from typing import List, Tuple

from PIL import Image

from config import (
    CATS_COLORS, OUTPUT_SETTINGS, 
    NAMES_FILE, LOGGING_CONFIG, RGB
)
from image_processing import ImageLoader, CatImageBuilder, FamilyLayoutBuilder
from cat import CatFamily


def setup_logging(verbose: bool = False, log_file: str = None) -> None:
    """
    Setup logging configuration
    
    Args:
        verbose: If True, set level to DEBUG
        log_file: Optional log file path
    """
    level = logging.DEBUG if verbose else getattr(
        logging, LOGGING_CONFIG['level']
    )
    
    handlers = [logging.StreamHandler()]
    if log_file:
        handlers.append(logging.FileHandler(log_file))
    
    logging.basicConfig(
        level=level,
        format=LOGGING_CONFIG['format'],
        handlers=handlers
    )


def load_cat_names(filepath: str = NAMES_FILE) -> List[str]:
    """
    Load cat names from file
    
    Args:
        filepath: Path to names file
        
    Returns:
        List of cat names
    """
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            names = f.read().splitlines()
        logging.info(f"Loaded {len(names)} cat names from {filepath}")
        return names
    except FileNotFoundError:
        logging.error(f"Names file not found: {filepath}")
        raise
    except Exception as e:
        logging.error(f"Error loading names: {e}")
        raise


def generate_cat_family(
    seed: int = None,
    custom_colors: List[RGB] = None
) -> Tuple[List[List[Image.Image]], CatFamily]:
    """
    Generate a complete cat family tree
    
    Args:
        seed: Random seed for reproducibility
        custom_colors: Optional custom color palette
        
    Returns:
        Tuple of (layout of cat images, CatFamily object)
    """
    if seed is not None:
        random.seed(seed)
        logging.info(f"Using random seed: {seed}")
    
    # Setup
    names = load_cat_names()
    image_loader = ImageLoader()
    parts_images = image_loader.load_all_parts()
    family = CatFamily(names)
    
    colors = custom_colors or CATS_COLORS
    
    # Track main colors for grandkittens
    main_colors_pool = []
    
    # Generate first pair of families
    logging.info("=" * 50)
    logging.info("Generating Family Tree")
    logging.info("=" * 50)
    
    # === FIRST BRANCH ===
    logging.info("\n--- First Branch ---")
    
    # First parent pair and their kitten
    color1, color2 = random.sample(colors, 2)
    parts1 = CatImageBuilder.choose_random_parts(parts_images)
    parts2 = CatImageBuilder.choose_random_parts(parts_images)
    
    parent1 = family.create_parent(color1, parts1, family.get_random_name())
    parent2 = family.create_parent(color2, parts2, family.get_random_name())
    kitten1 = family.create_kitten(parent1, parent2, family.get_random_name())
    
    # Second parent pair and their kitten
    color3, color4 = random.sample(colors, 2)
    parts3 = CatImageBuilder.choose_random_parts(parts_images)
    parts4 = CatImageBuilder.choose_random_parts(parts_images)
    
    parent3 = family.create_parent(color3, parts3, family.get_random_name())
    parent4 = family.create_parent(color4, parts4, family.get_random_name())
    kitten2 = family.create_kitten(parent3, parent4, family.get_random_name())
    
    # First grandkitten
    grandkitten1 = family.create_grandkitten(
        kitten1, kitten2, 
        family.get_random_name()
    )
    
    # === SECOND BRANCH ===
    logging.info("\n--- Second Branch ---")
    
    # Third parent pair and their kitten
    color5, color6 = random.sample(colors, 2)
    parts5 = CatImageBuilder.choose_random_parts(parts_images)
    parts6 = CatImageBuilder.choose_random_parts(parts_images)
    
    parent5 = family.create_parent(color5, parts5, family.get_random_name())
    parent6 = family.create_parent(color6, parts6, family.get_random_name())
    kitten3 = family.create_kitten(parent5, parent6, family.get_random_name())
    
    # Fourth parent pair and their kitten
    color7, color8 = random.sample(colors, 2)
    parts7 = CatImageBuilder.choose_random_parts(parts_images)
    parts8 = CatImageBuilder.choose_random_parts(parts_images)
    
    parent7 = family.create_parent(color7, parts7, family.get_random_name())
    parent8 = family.create_parent(color8, parts8, family.get_random_name())
    kitten4 = family.create_kitten(parent7, parent8, family.get_random_name())
    
    # Second grandkitten
    grandkitten2 = family.create_grandkitten(
        kitten3, kitten4,
        family.get_random_name()
    )
    
    # === GREAT GRANDKITTEN ===
    logging.info("\n--- Great Grandkitten ---")
    
    # Generate images for kittens to get their colors
    kitten1.generate_image()
    kitten2.generate_image()
    kitten3.generate_image()
    kitten4.generate_image()
    
    # Collect main colors
    main_colors_pool = []
    
    # Generate grandkittens to get main colors
    grandkitten1_img = grandkitten1.generate_image(main_colors_pool)
    if grandkitten1.main_color:
        main_colors_pool.append(grandkitten1.main_color)
    
    grandkitten2_img = grandkitten2.generate_image(main_colors_pool[:1] if main_colors_pool else [])
    if grandkitten2.main_color:
        main_colors_pool.append(grandkitten2.main_color)
    
    # Create great-grandkitten
    great_grandkitten = family.create_grandkitten(
        grandkitten1, grandkitten2,
        family.get_random_name()
    )
    
    # Generate all images
    logging.info("\n--- Generating Images ---")
    
    parent1_img = parent1.generate_image()
    parent2_img = parent2.generate_image()
    parent3_img = parent3.generate_image()
    parent4_img = parent4.generate_image()
    parent5_img = parent5.generate_image()
    parent6_img = parent6.generate_image()
    parent7_img = parent7.generate_image()
    parent8_img = parent8.generate_image()
    
    great_grandkitten_img = great_grandkitten.generate_image(main_colors_pool)
    
    # Create layout
    layout = [
        [parent1_img, parent2_img, kitten1.image, grandkitten1_img, great_grandkitten_img],
        [parent3_img, parent4_img, kitten2.image],
        [parent5_img, parent6_img, kitten3.image, grandkitten2_img],
        [parent7_img, parent8_img, kitten4.image],
    ]
    
    logging.info(f"\n✓ Generated {len(family.all_cats)} cats across {len(layout)} rows")
    
    return layout, family


def save_family_image(layout: List[List[Image.Image]], 
                     output_path: str = None) -> str:
    """
    Save the family layout to a file
    
    Args:
        layout: 2D layout of cat images
        output_path: Output file path
        
    Returns:
        Path where image was saved
    """
    output_path = output_path or OUTPUT_SETTINGS['default_filename']
    
    # Create output directory if needed
    output_dir = os.path.dirname(output_path)
    if output_dir and not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    # Generate family image
    family_img = FamilyLayoutBuilder.create_family_image(layout)
    
    # Save
    family_img.save(
        output_path,
        format=OUTPUT_SETTINGS['format'],
        quality=OUTPUT_SETTINGS['quality']
    )
    
    file_size = os.path.getsize(output_path) / 1024  # KB
    logging.info(f"✓ Saved family image to: {output_path} ({file_size:.1f} KB)")
    
    return output_path


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description="Generate a family tree of cats with genetic color inheritance",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s                          # Generate with default settings
  %(prog)s -o my_cats.png           # Custom output filename
  %(prog)s --seed 42                # Reproducible generation
  %(prog)s -v                       # Verbose logging
  %(prog)s --log cats.log           # Save logs to file
        """
    )
    
    parser.add_argument(
        '-o', '--output',
        default=OUTPUT_SETTINGS['default_filename'],
        help=f"Output filename (default: {OUTPUT_SETTINGS['default_filename']})"
    )
    
    parser.add_argument(
        '--seed',
        type=int,
        help="Random seed for reproducibility"
    )
    
    parser.add_argument(
        '-v', '--verbose',
        action='store_true',
        help="Enable verbose logging (DEBUG level)"
    )
    
    parser.add_argument(
        '--log',
        help="Save logs to file"
    )
    
    args = parser.parse_args()
    
    # Setup logging
    setup_logging(verbose=args.verbose, log_file=args.log)
    
    try:
        logging.info("🐱 Cat Family Generator Started")
        logging.info(f"Output: {args.output}")
        
        # Generate family
        layout, family = generate_cat_family(
            seed=args.seed
        )
        
        # Save image
        output_path = save_family_image(layout, args.output)
        
        print(f"\n✨ Success! Generated family with {len(family.all_cats)} cats")
        print(f"📁 Saved to: {output_path}")
        
        return 0
        
    except FileNotFoundError as e:
        logging.error(f"File not found: {e}")
        print(f"\n❌ Error: Required file not found - {e}", file=sys.stderr)
        return 1
        
    except Exception as e:
        logging.exception("Unexpected error occurred")
        print(f"\n❌ Error: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())

