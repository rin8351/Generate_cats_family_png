"""
Image Processing Module for Cat Family Generator
Handles loading, combining, and coloring cat images with optimized performance
"""

import os
import random
import logging
from typing import List, Dict, Tuple, Any, Sequence
from PIL import Image, ImageDraw, ImageFont
import numpy as np

from config import (
    CAT_PARTS_FOLDERS, GENERATION_PARAMS, RGB
)

logger = logging.getLogger(__name__)


class ImageLoader:
    """Loads and manages cat part images from folders"""
    
    def __init__(self, base_path: str = "."):
        """
        Initialize the image loader
        
        Args:
            base_path: Base directory containing cat part folders
        """
        self.base_path = base_path
        self._validate_folders()
    
    def _validate_folders(self) -> None:
        """Validate that all required folders exist"""
        for folder_name, folder_path in CAT_PARTS_FOLDERS.items():
            full_path = os.path.join(self.base_path, folder_path)
            if not os.path.exists(full_path):
                raise FileNotFoundError(
                    f"Required folder '{folder_path}' not found at {full_path}"
                )
            if not os.listdir(full_path):
                raise ValueError(f"Folder '{folder_path}' is empty")
        logger.info("All cat part folders validated successfully")
    
    def load_images_from_folder(self, folder_path: str) -> Dict[str, Image.Image]:
        """
        Load all PNG images from a folder, keyed by filename stem.

        Example: parts/body/3.png -> {"3": <Image>}

        Args:
            folder_path: Path to folder containing images

        Returns:
            Mapping of part file id -> PIL Image (RGB)
        """
        images: Dict[str, Image.Image] = {}
        full_path = os.path.join(self.base_path, folder_path)

        for filename in sorted(os.listdir(full_path)):
            if filename.lower().endswith('.png'):
                img_path = os.path.join(full_path, filename)
                file_id = os.path.splitext(filename)[0]
                try:
                    with Image.open(img_path) as img:
                        images[file_id] = img.convert('RGB').copy()
                    logger.debug(f"Loaded image: {filename}")
                except IOError as e:
                    logger.warning(f"Cannot load image {filename}: {e}")

        if not images:
            raise ValueError(f"No valid images found in {folder_path}")

        logger.info(f"Loaded {len(images)} images from {folder_path}")
        return images

    def load_all_parts(self) -> Dict[str, Dict[str, Image.Image]]:
        """
        Load all cat parts from configured folders

        Returns:
            Mapping of part name -> {file_id: Image}
            e.g. {"body": {"1": <img>, "2": <img>}, ...}
        """
        parts_images = {}
        for part_name, folder_path in CAT_PARTS_FOLDERS.items():
            parts_images[part_name] = self.load_images_from_folder(folder_path)

        logger.info(f"Loaded all {len(parts_images)} cat parts")
        return parts_images


class CatImageBuilder:
    """Builds cat images by combining parts and applying colors"""

    @staticmethod
    def part_ref(part_name: str, file_id: str) -> str:
        """Build a stable part reference like 'body_1' or 'ear_2'."""
        return f"{part_name}_{file_id}"

    @staticmethod
    def parse_part_ref(ref: str) -> Tuple[str, str]:
        """Parse 'body_1' into ('body', '1')."""
        if '_' not in ref:
            raise ValueError(f"Invalid part reference: {ref!r}")
        part_name, file_id = ref.rsplit('_', 1)
        return part_name, file_id

    @staticmethod
    def choose_random_parts(
        parts_images: Dict[str, Dict[str, Image.Image]]
    ) -> Tuple[Dict[str, Image.Image], Dict[str, str]]:
        """
        Select random images for each cat part.

        Returns:
            (parts, refs) where parts maps locus -> Image and
            refs maps locus -> string like 'body_1'
        """
        parts: Dict[str, Image.Image] = {}
        refs: Dict[str, str] = {}
        for part_name, by_id in parts_images.items():
            file_id = random.choice(list(by_id.keys()))
            parts[part_name] = by_id[file_id]
            refs[part_name] = CatImageBuilder.part_ref(part_name, file_id)
        logger.debug("Selected random parts for cat")
        return parts, refs

    @staticmethod
    def resolve_parts(
        parts_images: Dict[str, Dict[str, Image.Image]],
        refs: Dict[str, str],
    ) -> Dict[str, Image.Image]:
        """Resolve part references (body_1, ear_2, ...) to loaded images."""
        parts: Dict[str, Image.Image] = {}
        for part_name, ref in refs.items():
            expected_name, file_id = CatImageBuilder.parse_part_ref(ref)
            if expected_name != part_name:
                raise ValueError(
                    f"Part ref {ref!r} does not match locus {part_name!r}"
                )
            if part_name not in parts_images or file_id not in parts_images[part_name]:
                raise KeyError(f"Unknown part reference: {ref}")
            parts[part_name] = parts_images[part_name][file_id]
        return parts
    
    @staticmethod
    def combine_parts(parts: Dict[str, Image.Image]) -> Image.Image:
        """
        Combine cat parts into a single image
        
        Parts are arranged as:
        - Ear (top)
        - Eyes
        - Body (with tail on the right side)
        - Legs (bottom)
        
        Args:
            parts: Dictionary with keys: 'ear', 'eyes', 'body', 'tail', 'legs'
            
        Returns:
            Combined cat image
        """
        ear = parts['ear']
        eyes = parts['eyes']
        body = parts['body']
        tail = parts['tail']
        legs = parts['legs']
        
        # Create vertical combination of ear, eyes, and body
        vertical_height = ear.height + eyes.height + body.height
        vertical_width = max(ear.width, eyes.width, body.width)
        vertical_image = Image.new('RGB', (vertical_width, vertical_height))
        
        # Paste ear, eyes, and body one below the other (centered)
        current_height = 0
        vertical_image.paste(ear, ((vertical_width - ear.width) // 2, current_height))
        current_height += ear.height
        vertical_image.paste(eyes, ((vertical_width - eyes.width) // 2, current_height))
        current_height += eyes.height
        vertical_image.paste(body, ((vertical_width - body.width) // 2, current_height))
        
        # Attach tail to the right of the body
        final_width = vertical_width + tail.width
        combined_image = Image.new('RGB', (final_width, vertical_height))
        combined_image.paste(vertical_image, (0, 0))
        
        # Position tail at body level
        body_start_height = ear.height + eyes.height
        tail_top_position = body_start_height + (body.height - tail.height)
        combined_image.paste(tail, (vertical_width, tail_top_position))
        
        # Add legs below everything
        final_image = Image.new('RGB', (final_width, vertical_height + legs.height))
        final_image.paste(combined_image, (0, 0))
        final_image.paste(legs, ((final_width - legs.width) // 2, vertical_height))
        
        # Add padding at bottom for text (name + generation)
        text_padding = GENERATION_PARAMS.get('text_padding_bottom', 35)
        final_height = vertical_height + legs.height + text_padding
        padded_image = Image.new('RGB', (final_width, final_height), (255, 255, 255))
        padded_image.paste(final_image, (0, 0))
        
        logger.debug("Combined all cat parts into single image")
        return padded_image
    
    @staticmethod
    def apply_color_numpy(img: Image.Image, color_map: Dict[RGB, RGB]) -> Image.Image:
        """
        Apply color mapping to image using NumPy for better performance
        
        Args:
            img: Input image
            color_map: Dictionary mapping gray colors to replacement colors
            
        Returns:
            Colored image
        """
        # Convert to numpy array for faster pixel manipulation
        img_array = np.array(img)
        
        # Create output array
        output = img_array.copy()
        
        # Replace each gray color with its mapped color
        for gray_color, new_color in color_map.items():
            # Create mask where all three channels match the gray color
            mask = np.all(img_array == gray_color, axis=-1)
            # Apply new color where mask is True
            output[mask] = new_color
        
        logger.debug(f"Applied {len(color_map)} color mappings")
        return Image.fromarray(output)
    
    @staticmethod
    def add_text(img: Image.Image, text: str, 
                 position: Tuple[int, int] = None,
                 font_name: str = None,
                 font_size: int = None,
                 color: RGB = None) -> None:
        """
        Add text to image (modifies image in-place).
        Supports multiline text separated by \\n.
        
        Args:
            img: Image to modify
            text: Text to add
            position: (x, y) position for text (if None, places at bottom)
            font_name: Font file name
            font_size: Font size
            color: Text color
        """
        font_name = font_name or GENERATION_PARAMS['font_name']
        font_size = font_size or GENERATION_PARAMS['font_size']
        color = color or GENERATION_PARAMS['text_color']
        
        draw = ImageDraw.Draw(img)
        try:
            font = ImageFont.truetype(font_name, size=font_size)
        except IOError:
            logger.warning(f"Font '{font_name}' not found, using default")
            font = ImageFont.load_default()
        
        # If position not specified, place text at bottom center
        if position is None:
            bbox = draw.multiline_textbbox((0, 0), text, font=font, align='center')
            text_width = bbox[2] - bbox[0]
            text_height = bbox[3] - bbox[1]
            
            # Calculate position: centered horizontally, near bottom
            x_offset, y_offset = GENERATION_PARAMS['text_position']
            x = (img.width - text_width) // 2 + x_offset
            y = img.height - text_height - y_offset - 5  # 5 pixels from bottom
            position = (x, y)
        
        draw.multiline_text(position, text, font=font, fill=color, align='center')
        logger.debug(f"Added text: {text.replace(chr(10), ' | ')}")

    @staticmethod
    def _load_font(font_name: str, font_size: int) -> ImageFont.ImageFont:
        try:
            return ImageFont.truetype(font_name, size=font_size)
        except IOError:
            logger.warning(f"Font '{font_name}' not found, using default")
            return ImageFont.load_default()

    @staticmethod
    def add_cat_label(
        img: Image.Image,
        title: str,
        color_strengths: Sequence[Tuple[RGB, float]],
    ) -> None:
        """
        Draw name/generation and a color-strength legend under the cat.

        ``color_strengths`` should already be sorted strongest-first.
        Each entry is drawn as a color swatch + strength value.
        """
        font_name = GENERATION_PARAMS['font_name']
        title_font = CatImageBuilder._load_font(
            font_name, GENERATION_PARAMS['font_size']
        )
        gene_font = CatImageBuilder._load_font(
            font_name, GENERATION_PARAMS.get('gene_font_size', 14)
        )
        text_color = GENERATION_PARAMS['text_color']
        swatch = GENERATION_PARAMS.get('swatch_size', 12)
        x_offset, y_offset = GENERATION_PARAMS['text_position']
        gap = 4
        row_gap = 3

        draw = ImageDraw.Draw(img)
        title_bbox = draw.textbbox((0, 0), title, font=title_font)
        title_w = title_bbox[2] - title_bbox[0]
        title_h = title_bbox[3] - title_bbox[1]

        strength_labels = [f"{strength:.1f}" for _color, strength in color_strengths]
        gene_widths = []
        gene_heights = []
        for label in strength_labels:
            bbox = draw.textbbox((0, 0), label, font=gene_font)
            gene_widths.append(bbox[2] - bbox[0])
            gene_heights.append(bbox[3] - bbox[1])

        gene_row_h = max([swatch] + gene_heights) if color_strengths else 0
        gene_row_w = (
            max((swatch + gap + w for w in gene_widths), default=0)
            if color_strengths else 0
        )

        block_w = max(title_w, gene_row_w)
        block_h = title_h
        if color_strengths:
            block_h += gap + len(color_strengths) * gene_row_h
            if len(color_strengths) > 1:
                block_h += (len(color_strengths) - 1) * row_gap

        x0 = (img.width - block_w) // 2 + x_offset
        y = img.height - block_h - y_offset - 5

        draw.text(
            (x0 + (block_w - title_w) // 2, y),
            title,
            font=title_font,
            fill=text_color,
        )
        y += title_h + gap

        for (color, _strength), label, label_w, label_h in zip(
            color_strengths, strength_labels, gene_widths, gene_heights
        ):
            row_w = swatch + gap + label_w
            row_x = x0 + (block_w - row_w) // 2
            swatch_y = y + (gene_row_h - swatch) // 2
            label_y = y + (gene_row_h - label_h) // 2
            draw.rectangle(
                [row_x, swatch_y, row_x + swatch - 1, swatch_y + swatch - 1],
                fill=color,
                outline=(80, 80, 80),
            )
            draw.text(
                (row_x + swatch + gap, label_y),
                label,
                font=gene_font,
                fill=text_color,
            )
            y += gene_row_h + row_gap

        logger.debug(f"Added cat label: {title} ({len(color_strengths)} colors)")


class FamilyLayoutBuilder:
    """Builds the final family pedigree image"""

    @staticmethod
    def _cell_box(
        img: Image.Image,
        cell_x: int,
        center_y: float,
        cell_w: int,
    ) -> Tuple[int, int, int, int]:
        """Compute centered paste box (x, y, w, h) inside a column cell."""
        x = cell_x + (cell_w - img.width) // 2
        y = int(center_y - img.height / 2)
        return (x, y, img.width, img.height)

    @staticmethod
    def _draw_bracket(
        draw: ImageDraw.ImageDraw,
        parent_a: Tuple[int, int, int, int],
        parent_b: Tuple[int, int, int, int],
        child: Tuple[int, int, int, int],
        color: RGB,
        line_width: int,
        stem_x: int = None,
    ) -> None:
        """Draw a pedigree bracket from two parents to their child."""
        ax, ay, aw, ah = parent_a
        bx, by, bw, bh = parent_b
        cx, cy, _cw, ch = child

        a_right = (ax + aw, ay + ah // 2)
        b_right = (bx + bw, by + bh // 2)
        child_left = (cx, cy + ch // 2)
        if stem_x is None:
            stem_x = (a_right[0] + child_left[0]) // 2
        mid_y = (a_right[1] + b_right[1]) // 2

        draw.line([a_right, (stem_x, a_right[1])], fill=color, width=line_width)
        draw.line([b_right, (stem_x, b_right[1])], fill=color, width=line_width)
        draw.line(
            [(stem_x, a_right[1]), (stem_x, b_right[1])],
            fill=color,
            width=line_width,
        )
        draw.line([(stem_x, mid_y), child_left], fill=color, width=line_width)

    @staticmethod
    def create_pedigree_image(pedigree: Dict[str, Any],
                              background_color: RGB = None) -> Image.Image:
        """
        Create a left-to-right pedigree tree with connector lines.

        Expected pedigree keys:
            pairs: list of (parent1_img, parent2_img, kitten_img) x4
            grandkittens: [gk1_img, gk2_img]
            great_grandkitten: ggk_img
        """
        background_color = background_color or GENERATION_PARAMS['background_color']
        column_gap = GENERATION_PARAMS.get('column_gap', 48)
        connector_color = GENERATION_PARAMS.get('connector_color', (80, 80, 80))
        connector_width = GENERATION_PARAMS.get('connector_width', 2)

        pairs = pedigree['pairs']
        grandkittens = pedigree['grandkittens']
        great_grandkitten = pedigree['great_grandkitten']

        if len(pairs) != 4 or len(grandkittens) != 2:
            raise ValueError("Pedigree must have 4 parent pairs and 2 grandkittens")

        all_images = []
        for p1, p2, kitten in pairs:
            all_images.extend([p1, p2, kitten])
        all_images.extend(grandkittens)
        all_images.append(great_grandkitten)

        cell_w = max(img.width for img in all_images)
        cell_h = max(img.height for img in all_images)
        num_slots = 8
        num_columns = 4

        total_width = num_columns * cell_w + (num_columns - 1) * column_gap
        total_height = num_slots * cell_h

        canvas = Image.new('RGB', (total_width, total_height), background_color)
        draw = ImageDraw.Draw(canvas)

        def col_x(col: int) -> int:
            return col * (cell_w + column_gap)

        def gap_stem_x(after_col: int) -> int:
            """X in the middle of the gap after the given column."""
            return col_x(after_col) + cell_w + column_gap // 2

        def slot_center_y(slot: float) -> float:
            return (slot + 0.5) * cell_h

        # Compute boxes for all cats (Gen 0 parents in slots 0..7)
        parent_boxes = []
        for pair_idx, (p1, p2, _kitten) in enumerate(pairs):
            slot_a = pair_idx * 2
            slot_b = slot_a + 1
            box_a = FamilyLayoutBuilder._cell_box(
                p1, col_x(0), slot_center_y(slot_a), cell_w
            )
            box_b = FamilyLayoutBuilder._cell_box(
                p2, col_x(0), slot_center_y(slot_b), cell_w
            )
            parent_boxes.append((box_a, box_b))

        kitten_boxes = []
        for pair_idx, (_p1, _p2, kitten) in enumerate(pairs):
            slot_mid = pair_idx * 2 + 0.5
            kitten_boxes.append(
                FamilyLayoutBuilder._cell_box(
                    kitten, col_x(1), slot_center_y(slot_mid), cell_w
                )
            )

        # GK1 from kittens 0+1, GK2 from 2+3
        gk_boxes = []
        gk_parent_slots = [(0.5, 2.5), (4.5, 6.5)]
        for gk_idx, gk_img in enumerate(grandkittens):
            s1, s2 = gk_parent_slots[gk_idx]
            center = (slot_center_y(s1) + slot_center_y(s2)) / 2
            gk_boxes.append(
                FamilyLayoutBuilder._cell_box(gk_img, col_x(2), center, cell_w)
            )

        ggk_center = (slot_center_y(1.5) + slot_center_y(5.5)) / 2
        ggk_box = FamilyLayoutBuilder._cell_box(
            great_grandkitten, col_x(3), ggk_center, cell_w
        )

        # Draw connectors first (in gaps), then paste cats on top
        for pair_idx, (box_a, box_b) in enumerate(parent_boxes):
            FamilyLayoutBuilder._draw_bracket(
                draw, box_a, box_b, kitten_boxes[pair_idx],
                connector_color, connector_width, gap_stem_x(0),
            )
        FamilyLayoutBuilder._draw_bracket(
            draw, kitten_boxes[0], kitten_boxes[1], gk_boxes[0],
            connector_color, connector_width, gap_stem_x(1),
        )
        FamilyLayoutBuilder._draw_bracket(
            draw, kitten_boxes[2], kitten_boxes[3], gk_boxes[1],
            connector_color, connector_width, gap_stem_x(1),
        )
        FamilyLayoutBuilder._draw_bracket(
            draw, gk_boxes[0], gk_boxes[1], ggk_box,
            connector_color, connector_width, gap_stem_x(2),
        )

        placements = []
        for (p1, p2, kitten), (box_a, box_b), k_box in zip(
            pairs, parent_boxes, kitten_boxes
        ):
            placements.extend([(p1, box_a), (p2, box_b), (kitten, k_box)])
        for gk_img, gk_box in zip(grandkittens, gk_boxes):
            placements.append((gk_img, gk_box))
        placements.append((great_grandkitten, ggk_box))

        for img, (x, y, _w, _h) in placements:
            canvas.paste(img, (x, y))

        logger.info(f"Created pedigree image: {total_width}x{total_height} pixels")
        return canvas

