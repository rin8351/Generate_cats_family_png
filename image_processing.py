"""
Image Processing Module for Cat Family Generator
Handles loading, combining, and coloring cat images with optimized performance
"""

import os
import random
import logging
from typing import List, Dict, Tuple
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
    
    def load_images_from_folder(self, folder_path: str) -> List[Image.Image]:
        """
        Load all PNG images from a folder
        
        Args:
            folder_path: Path to folder containing images
            
        Returns:
            List of loaded PIL Images in RGB format
        """
        images = []
        full_path = os.path.join(self.base_path, folder_path)
        
        for filename in sorted(os.listdir(full_path)):
            if filename.lower().endswith('.png'):
                img_path = os.path.join(full_path, filename)
                try:
                    with Image.open(img_path) as img:
                        rgb_img = img.convert('RGB')
                        images.append(rgb_img.copy())
                    logger.debug(f"Loaded image: {filename}")
                except IOError as e:
                    logger.warning(f"Cannot load image {filename}: {e}")
        
        if not images:
            raise ValueError(f"No valid images found in {folder_path}")
        
        logger.info(f"Loaded {len(images)} images from {folder_path}")
        return images
    
    def load_all_parts(self) -> Dict[str, List[Image.Image]]:
        """
        Load all cat parts from configured folders
        
        Returns:
            Dictionary mapping part names to lists of images
        """
        parts_images = {}
        for part_name, folder_path in CAT_PARTS_FOLDERS.items():
            parts_images[part_name] = self.load_images_from_folder(folder_path)
        
        logger.info(f"Loaded all {len(parts_images)} cat parts")
        return parts_images


class CatImageBuilder:
    """Builds cat images by combining parts and applying colors"""
    
    @staticmethod
    def choose_random_parts(parts_images: Dict[str, List[Image.Image]]) -> Dict[str, Image.Image]:
        """
        Select random images for each cat part
        
        Args:
            parts_images: Dictionary of part names to image lists
            
        Returns:
            Dictionary of part names to selected images
        """
        selected = {
            part: random.choice(images) 
            for part, images in parts_images.items()
        }
        logger.debug("Selected random parts for cat")
        return selected
    
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
        
        logger.debug("Combined all cat parts into single image")
        return final_image
    
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
        Add text to image (modifies image in-place)
        
        Args:
            img: Image to modify
            text: Text to add
            position: (x, y) position for text
            font_name: Font file name
            font_size: Font size
            color: Text color
        """
        position = position or GENERATION_PARAMS['text_position']
        font_name = font_name or GENERATION_PARAMS['font_name']
        font_size = font_size or GENERATION_PARAMS['font_size']
        color = color or GENERATION_PARAMS['text_color']
        
        draw = ImageDraw.Draw(img)
        try:
            font = ImageFont.truetype(font_name, size=font_size)
        except IOError:
            logger.warning(f"Font '{font_name}' not found, using default")
            font = ImageFont.load_default()
        
        draw.text(position, text, font=font, fill=color)
        logger.debug(f"Added text: {text}")


class FamilyLayoutBuilder:
    """Builds the final family layout image"""
    
    @staticmethod
    def create_family_image(layout: List[List[Image.Image]], 
                          background_color: RGB = None) -> Image.Image:
        """
        Create a family tree image from a 2D layout of cat images
        
        Args:
            layout: 2D list of cat images (rows and columns)
            background_color: Background color for empty spaces
            
        Returns:
            Combined family image
        """
        background_color = background_color or GENERATION_PARAMS['background_color']
        
        if not layout or not layout[0]:
            raise ValueError("Layout cannot be empty")
        
        # Calculate dimensions
        max_width = max(cat.width for row in layout for cat in row)
        max_height = max(cat.height for row in layout for cat in row)
        total_width = max_width * max(len(row) for row in layout)
        total_height = max_height * len(layout)
        
        # Create canvas
        combined_img = Image.new('RGB', (total_width, total_height), background_color)
        
        # Place cats in the layout
        y_offset = 0
        for row in layout:
            x_offset = 0
            for cat in row:
                combined_img.paste(cat, (x_offset, y_offset))
                x_offset += cat.width
            y_offset += max_height
        
        logger.info(f"Created family image: {total_width}x{total_height} pixels")
        return combined_img

