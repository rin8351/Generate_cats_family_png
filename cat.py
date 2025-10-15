"""
Cat Genetics Module
Handles cat generation, genetics, and color inheritance
"""

import random
import logging
from typing import List, Dict, Optional
from PIL import Image

from config import GRAY_COLORS, RGB
from image_processing import CatImageBuilder

logger = logging.getLogger(__name__)


class Cat:
    """Represents a cat with genetic information"""
    
    def __init__(self, name: str, color: RGB, parts: Dict[str, Image.Image]):
        """
        Initialize a cat
        
        Args:
            name: Cat's name
            color: Primary color (RGB tuple)
            parts: Dictionary of body parts (ear, eyes, body, tail, legs)
        """
        self.name = name
        self.color = color
        self.parts = parts
        self.image: Optional[Image.Image] = None
        logger.debug(f"Created cat: {name} with color {color}")
    
    def __repr__(self) -> str:
        return f"Cat(name='{self.name}', color={self.color})"


class ParentCat(Cat):
    """Represents a parent cat with single color"""
    
    def __init__(self, name: str, color: RGB, parts: Dict[str, Image.Image]):
        super().__init__(name, color, parts)
        self.generation = 0
    
    def generate_image(self) -> Image.Image:
        """
        Generate monotone colored cat image
        
        Returns:
            Colored cat image
        """
        # Combine parts into cat shape
        img = CatImageBuilder.combine_parts(self.parts)
        
        # Create color map: all gray colors -> cat's color
        color_map = {gray: self.color for gray in GRAY_COLORS}
        
        # Apply coloring
        img = CatImageBuilder.apply_color_numpy(img, color_map)
        
        # Add name with generation info
        display_name = f"{self.name} (Gen {self.generation})"
        CatImageBuilder.add_text(img, display_name)
        
        self.image = img
        logger.info(f"Generated image for parent cat: {self.name}")
        return img


class KittenCat(Cat):
    """Represents a kitten with inherited traits from two parents"""
    
    def __init__(self, name: str, parent1: Cat, parent2: Cat, 
                 parts: Dict[str, Image.Image]):
        """
        Initialize a kitten
        
        Args:
            name: Kitten's name
            parent1: First parent
            parent2: Second parent
            parts: Body parts (inherited from parents)
        """
        # Kitten doesn't have a single color yet (will be multi-colored)
        super().__init__(name, parent1.color, parts)
        self.parent1 = parent1
        self.parent2 = parent2
        self.colors_used: List[RGB] = []
        self.generation = 1
        logger.debug(f"Created kitten: {name} from parents {parent1.name} and {parent2.name}")
    
    @staticmethod
    def inherit_parts(parent1: Cat, parent2: Cat) -> Dict[str, Image.Image]:
        """
        Inherit body parts from two parents (Mendelian genetics)
        
        Each part has 50% chance to come from either parent
        
        Args:
            parent1: First parent
            parent2: Second parent
            
        Returns:
            Dictionary of inherited parts
        """
        parts = {}
        for part_name in ['ear', 'eyes', 'body', 'tail', 'legs']:
            parts[part_name] = random.choice([
                parent1.parts[part_name],
                parent2.parts[part_name]
            ])
        
        logger.debug("Inherited parts from parents")
        return parts
    
    def generate_image(self) -> Image.Image:
        """
        Generate kitten image with inherited colors
        
        Each gray shade gets randomly one of the parent colors
        
        Returns:
            Colored kitten image
        """
        # Combine parts
        img = CatImageBuilder.combine_parts(self.parts)
        
        # Create color map: each gray gets random parent color
        color_map = {}
        self.colors_used = []
        
        for gray_color in GRAY_COLORS:
            chosen_color = random.choice([self.parent1.color, self.parent2.color])
            color_map[gray_color] = chosen_color
            self.colors_used.append(chosen_color)
        
        # Apply coloring
        img = CatImageBuilder.apply_color_numpy(img, color_map)
        
        # Add name with generation info
        display_name = f"{self.name} (Gen {self.generation})"
        CatImageBuilder.add_text(img, display_name)
        
        self.image = img
        logger.info(f"Generated image for kitten: {self.name}")
        return img


class GrandKittenCat(Cat):
    """Represents a grandkitten with more complex color inheritance"""
    
    def __init__(self, name: str, parent1, parent2,
                 parts: Dict[str, Image.Image]):
        """
        Initialize a grandkitten
        
        Args:
            name: Grandkitten's name
            parent1: First parent (kitten or grandkitten)
            parent2: Second parent (kitten or grandkitten)
            parts: Body parts (inherited)
        """
        super().__init__(name, parent1.color, parts)
        self.parent1 = parent1
        self.parent2 = parent2
        self.colors_used: List[RGB] = []
        self.main_color: Optional[RGB] = None
        # Determine generation based on parents
        # If both parents are GrandKittenCat, this is generation 3
        if isinstance(parent1, GrandKittenCat) and isinstance(parent2, GrandKittenCat):
            self.generation = 3
        else:
            self.generation = 2
        logger.debug(f"Created grandkitten: {name} (Generation {self.generation})")
    
    def generate_image(self, main_colors_pool: List[RGB]) -> Image.Image:
        """
        Generate grandkitten image with complex color inheritance
        
        Combines colors from both parents with variation
        
        Args:
            main_colors_pool: Pool of main colors to choose from
            
        Returns:
            Colored grandkitten image
        """
        # Combine parts
        img = CatImageBuilder.combine_parts(self.parts)
        
        # Collect unique colors from both parents
        unique_colors = list(set(
            self.parent1.colors_used + self.parent2.colors_used
        ))
        
        # Choose how many colors to use (2, 3, or all)
        if len(unique_colors) > 3:
            num_colors = random.choice([2, 3, len(unique_colors)])
            selected_colors = random.sample(unique_colors, num_colors)
        else:
            selected_colors = unique_colors
        
        # Choose main color for primary body parts
        self.main_color = random.choice(main_colors_pool) if main_colors_pool else selected_colors[0]
        
        # Create color map
        color_map = {}
        for i, gray_color in enumerate(GRAY_COLORS):
            if gray_color == (252, 252, 252):  # Main body color
                color_map[gray_color] = self.main_color
            else:
                # Distribute other colors
                color_map[gray_color] = selected_colors[i % len(selected_colors)]
        
        self.colors_used = selected_colors
        
        # Apply coloring
        img = CatImageBuilder.apply_color_numpy(img, color_map)
        
        # Add name with generation info
        display_name = f"{self.name} (Gen {self.generation})"
        CatImageBuilder.add_text(img, display_name)
        
        self.image = img
        logger.info(f"Generated image for grandkitten: {self.name}")
        return img


class CatFamily:
    """Manages a family tree of cats"""
    
    def __init__(self, names_list: List[str]):
        """
        Initialize cat family generator
        
        Args:
            names_list: List of available cat names
        """
        self.names_list = names_list.copy()
        self.all_cats: List[Cat] = []
        self.parents: List[ParentCat] = []
        self.kittens: List[KittenCat] = []
        self.grandkittens: List[GrandKittenCat] = []
        logger.info("Initialized CatFamily")
    
    def get_random_name(self, prefix: str = "") -> str:
        """
        Get a random name from the list
        
        Args:
            prefix: Optional prefix for the name
            
        Returns:
            Random name (with prefix if provided)
        """
        if not self.names_list:
            logger.warning("Ran out of names, generating random ID")
            return f"{prefix}Cat_{random.randint(1000, 9999)}"
        
        full_name = random.choice(self.names_list)
        # Extract just the name part (after number)
        name = full_name.split(' ')[-1]
        
        return f"{prefix}{name}" if prefix else name
    
    def create_parent(self, color: RGB, parts: Dict[str, Image.Image],
                     name: str = None) -> ParentCat:
        """
        Create a parent cat
        
        Args:
            color: Cat's color
            parts: Body parts
            name: Optional name (will be generated if not provided)
            
        Returns:
            Created parent cat
        """
        if name is None:
            name = self.get_random_name()
        
        parent = ParentCat(name, color, parts)
        self.parents.append(parent)
        self.all_cats.append(parent)
        
        logger.info(f"Created parent: {name}")
        return parent
    
    def create_kitten(self, parent1: ParentCat, parent2: ParentCat,
                     name: str = None) -> KittenCat:
        """
        Create a kitten from two parents
        
        Args:
            parent1: First parent
            parent2: Second parent
            name: Optional name
            
        Returns:
            Created kitten
        """
        if name is None:
            name = self.get_random_name()
        
        parts = KittenCat.inherit_parts(parent1, parent2)
        kitten = KittenCat(name, parent1, parent2, parts)
        
        self.kittens.append(kitten)
        self.all_cats.append(kitten)
        
        logger.info(f"Created kitten: {name}")
        return kitten
    
    def create_grandkitten(self, parent1: KittenCat, parent2: KittenCat,
                          name: str = None) -> GrandKittenCat:
        """
        Create a grandkitten from two kittens
        
        Args:
            parent1: First parent (kitten)
            parent2: Second parent (kitten)
            name: Optional name
            
        Returns:
            Created grandkitten
        """
        if name is None:
            name = self.get_random_name("GrandKitten ")
        
        parts = KittenCat.inherit_parts(parent1, parent2)
        grandkitten = GrandKittenCat(name, parent1, parent2, parts)
        
        self.grandkittens.append(grandkitten)
        self.all_cats.append(grandkitten)
        
        logger.info(f"Created grandkitten: {name}")
        return grandkitten

