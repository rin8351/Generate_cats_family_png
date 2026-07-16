#!/usr/bin/env python3
"""
Cat Family Generator - Main Entry Point

"""

import os
import sys
import random
import logging
import argparse
from typing import List, Tuple, Dict, Any, Optional

from cats_colors import CATS_COLORS
from config import (
    OUTPUT_SETTINGS,
    NAMES_FILE, LOGGING_CONFIG, RGB, SEEDS_FILE
)
from image_processing import ImageLoader, CatImageBuilder, FamilyLayoutBuilder
from cat import CatFamily, ParentCat
from seeds import (
    append_seed, get_seed, list_seeds, make_cat_snapshot, format_seed_summary
)


def setup_logging(verbose: bool = False, log_file: str = None) -> None:
    """Setup logging configuration."""
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
    """Load cat names from file."""
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


def _random_gen0_cats(
    family: CatFamily,
    parts_images: Dict[str, Dict],
    colors: List[RGB],
    count: int = 8,
) -> List[Dict[str, Any]]:
    """Create random Gen 0 snapshots (name + color + part refs)."""
    cats = []
    for _ in range(count):
        name = family.get_random_name()
        color = random.choice(colors)
        _parts, refs = CatImageBuilder.choose_random_parts(parts_images)
        cats.append(make_cat_snapshot(name, color, refs))
    return cats


def _build_parents_from_snapshots(
    family: CatFamily,
    parts_images: Dict[str, Dict],
    snapshots: List[Dict[str, Any]],
) -> List[ParentCat]:
    """Materialize ParentCat objects from Gen 0 seed snapshots."""
    if len(snapshots) != 8:
        raise ValueError(f"Gen 0 seed must contain 8 cats, got {len(snapshots)}")

    parents = []
    for snap in snapshots:
        color = tuple(snap['color'])
        parts = CatImageBuilder.resolve_parts(parts_images, snap['parts'])
        # Older seeds may lack names — fall back to a fresh random name
        name = snap.get('name') or family.get_random_name()
        parents.append(family.create_parent(color, parts, name))
    return parents


def generate_cat_family(
    gen0_snapshots: Optional[List[Dict[str, Any]]] = None,
    custom_colors: List[RGB] = None,
    save_new_seed: bool = True,
) -> Tuple[Dict[str, Any], CatFamily, Optional[int]]:
    """
    Generate a complete cat family tree.

    Args:
        gen0_snapshots: Optional Gen 0 cats from a saved seed. If None, random.
        custom_colors: Optional custom color palette (used only when random).
        save_new_seed: If True and Gen 0 was random, append it to seeds.json.

    Returns:
        (pedigree image data, CatFamily, new_seed_id or None)
    """
    names = load_cat_names()
    image_loader = ImageLoader()
    parts_images = image_loader.load_all_parts()
    family = CatFamily(names)
    colors = custom_colors or CATS_COLORS

    new_seed_id: Optional[int] = None
    if gen0_snapshots is None:
        gen0_snapshots = _random_gen0_cats(family, parts_images, colors, count=8)
        if save_new_seed:
            new_seed_id = append_seed(gen0_snapshots)
            logging.info(f"Saved new Gen 0 seed #{new_seed_id} to {SEEDS_FILE}")

    parents = _build_parents_from_snapshots(family, parts_images, gen0_snapshots)
    (
        parent1, parent2, parent3, parent4,
        parent5, parent6, parent7, parent8,
    ) = parents

    logging.info("=" * 50)
    logging.info("Generating Family Tree")
    logging.info("=" * 50)


    logging.info("\n--- First Branch ---")
    kitten1 = family.create_kitten(parent1, parent2, family.get_random_name())
    kitten2 = family.create_kitten(parent3, parent4, family.get_random_name())
    grandkitten1 = family.create_grandkitten(
        kitten1, kitten2, family.get_random_name()
    )


    logging.info("\n--- Second Branch ---")
    kitten3 = family.create_kitten(parent5, parent6, family.get_random_name())
    kitten4 = family.create_kitten(parent7, parent8, family.get_random_name())
    grandkitten2 = family.create_grandkitten(
        kitten3, kitten4, family.get_random_name()
    )


    logging.info("\n--- Great Grandkitten ---")
    great_grandkitten = family.create_grandkitten(
        grandkitten1, grandkitten2, family.get_random_name()
    )

    logging.info("\n--- Generating Images ---")
    parent_imgs = [p.generate_image() for p in parents]
    for kitten in (kitten1, kitten2, kitten3, kitten4):
        kitten.generate_image()
    grandkitten1_img = grandkitten1.generate_image()
    grandkitten2_img = grandkitten2.generate_image()
    great_grandkitten_img = great_grandkitten.generate_image()

    pedigree = {
        'pairs': [
            (parent_imgs[0], parent_imgs[1], kitten1.image),
            (parent_imgs[2], parent_imgs[3], kitten2.image),
            (parent_imgs[4], parent_imgs[5], kitten3.image),
            (parent_imgs[6], parent_imgs[7], kitten4.image),
        ],
        'grandkittens': [grandkitten1_img, grandkitten2_img],
        'great_grandkitten': great_grandkitten_img,
    }

    logging.info(f"\nGenerated {len(family.all_cats)} cats across 4 generations")
    return pedigree, family, new_seed_id


def save_family_image(pedigree: Dict[str, Any],
                      output_path: str = None) -> str:
    """Save the pedigree family image to a file."""
    output_path = output_path or OUTPUT_SETTINGS['default_filename']

    output_dir = os.path.dirname(output_path)
    if output_dir and not os.path.exists(output_dir):
        os.makedirs(output_dir)

    family_img = FamilyLayoutBuilder.create_pedigree_image(pedigree)
    family_img.save(
        output_path,
        format=OUTPUT_SETTINGS['format'],
        quality=OUTPUT_SETTINGS['quality']
    )

    file_size = os.path.getsize(output_path) / 1024  # KB
    logging.info(f"Saved family image to: {output_path} ({file_size:.1f} KB)")
    return output_path


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description="Generate a family tree of cats with genetic color inheritance",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=f"""
Examples:
  %(prog)s                       # Random Gen 0 (auto-saved to {SEEDS_FILE})
  %(prog)s --load-seed 3         # Replay Gen 0 from seed #3 (kids re-rolled)
  %(prog)s --list-seeds          # Show all saved Gen 0 seeds
  %(prog)s -o my_cats.png        # Custom output filename
  %(prog)s -v                    # Verbose logging
        """
    )

    parser.add_argument(
        '-o', '--output',
        default=OUTPUT_SETTINGS['default_filename'],
        help=f"Output filename (default: {OUTPUT_SETTINGS['default_filename']})"
    )

    parser.add_argument(
        '--load-seed',
        type=int,
        metavar='ID',
        help=f"Load Gen 0 from {SEEDS_FILE} by id (later gens still random)"
    )

    parser.add_argument(
        '--list-seeds',
        action='store_true',
        help=f"List saved Gen 0 seeds from {SEEDS_FILE} and exit"
    )

    parser.add_argument(
        '--no-save-seed',
        action='store_true',
        help="Do not append a new random Gen 0 to the seeds file"
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
    setup_logging(verbose=args.verbose, log_file=args.log)

    try:
        if args.list_seeds:
            seeds = list_seeds()
            if not seeds:
                print(f"No seeds saved yet in {SEEDS_FILE}")
            else:
                print(f"Saved Gen 0 seeds in {SEEDS_FILE}:")
                for seed in seeds:
                    print(f"  {format_seed_summary(seed)}")
            return 0

        logging.info("Cat Family Generator Started")
        logging.info(f"Output: {args.output}")

        gen0_snapshots = None
        if args.load_seed is not None:
            seed = get_seed(args.load_seed)
            gen0_snapshots = seed['cats']
            logging.info(
                f"Loaded Gen 0 seed #{args.load_seed} "
                f"({len(gen0_snapshots)} cats) from {SEEDS_FILE}"
            )

        pedigree, family, new_seed_id = generate_cat_family(
            gen0_snapshots=gen0_snapshots,
            save_new_seed=not args.no_save_seed and gen0_snapshots is None,
        )

        output_path = save_family_image(pedigree, args.output)

        print(f"\nSuccess! Generated family with {len(family.all_cats)} cats")
        print(f"Saved to: {output_path}")
        if new_seed_id is not None:
            print(f"Gen 0 seed saved as #{new_seed_id} in {SEEDS_FILE}")
        elif args.load_seed is not None:
            print(f"Used Gen 0 seed #{args.load_seed} (later generations re-rolled)")

        return 0

    except KeyError as e:
        logging.error(str(e))
        print(f"\nError: {e}", file=sys.stderr)
        return 1

    except FileNotFoundError as e:
        logging.error(f"File not found: {e}")
        print(f"\nError: Required file not found - {e}", file=sys.stderr)
        return 1

    except Exception as e:
        logging.exception("Unexpected error occurred")
        print(f"\nError: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
