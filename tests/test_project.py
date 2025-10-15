"""
Simplified tests for the Cat Family Generator project
Tests only the essential requirements for the project to work correctly
"""
import pytest
from pathlib import Path
from config import CATS_COLORS, GRAY_COLORS, CAT_PARTS_FOLDERS, NAMES_FILE


class TestProjectStructure:
    """Test essential project structure and configuration"""
    
    def test_required_folders_exist_and_not_empty(self):
        """Test that required body part folders exist and contain images"""
        required_folders = ['ear', 'eyes', 'body', 'tail', 'legs']
        
        # Check there are at least 5 folders configured
        assert len(CAT_PARTS_FOLDERS) >= 5, "Should have at least 5 body part folders"
        
        # Check each required folder exists and is not empty
        for folder_name in required_folders:
            folder_path = Path(folder_name)
            assert folder_path.exists(), f"Folder '{folder_name}' does not exist"
            assert folder_path.is_dir(), f"'{folder_name}' is not a directory"
            
            # Check folder is not empty
            files = list(folder_path.glob('*.png'))
            assert len(files) > 0, f"Folder '{folder_name}' is empty"
    
    def test_cats_colors_not_empty_and_valid_format(self):
        """Test that CATS_COLORS list is not empty and contains valid RGB tuples"""
        # Check not empty
        assert len(CATS_COLORS) > 0, "CATS_COLORS should not be empty"
        
        # Check format: list of RGB tuples
        for color in CATS_COLORS:
            assert isinstance(color, tuple), f"Color {color} should be a tuple"
            assert len(color) == 3, f"Color {color} should have 3 values (R, G, B)"
            for value in color:
                assert isinstance(value, int), f"RGB value {value} should be an integer"
                assert 0 <= value <= 255, f"RGB value {value} should be between 0 and 255"
    
    def test_gray_colors_not_empty_and_valid_format(self):
        """Test that GRAY_COLORS list is not empty and contains valid RGB tuples"""
        # Check not empty
        assert len(GRAY_COLORS) > 0, "GRAY_COLORS should not be empty"
        
        # Check format: list of RGB tuples
        for color in GRAY_COLORS:
            assert isinstance(color, tuple), f"Gray color {color} should be a tuple"
            assert len(color) == 3, f"Gray color {color} should have 3 values (R, G, B)"
            for value in color:
                assert isinstance(value, int), f"RGB value {value} should be an integer"
                assert 0 <= value <= 255, f"RGB value {value} should be between 0 and 255"
    
    def test_gray_colors_exact_values(self):
        """Test that GRAY_COLORS has exact values (critical for correct cat coloring)"""
        expected_gray_colors = [
            (195, 195, 195), (212, 212, 212), (224, 224, 224),
            (235, 235, 235), (201, 201, 201), (194, 194, 194),
            (189, 189, 189), (181, 181, 181), (171, 171, 171),
            (247, 247, 247), (252, 252, 252)
        ]
        
        assert GRAY_COLORS == expected_gray_colors, (
            "GRAY_COLORS must have exact values as specified. "
            "Changing these values will cause incorrect cat coloring."
        )
    
    def test_names_file_exists_and_not_empty(self):
        """Test that cats_name.TXT file exists and contains names"""
        names_file_path = Path(NAMES_FILE)
        
        # Check file exists
        assert names_file_path.exists(), f"Names file '{NAMES_FILE}' does not exist"
        assert names_file_path.is_file(), f"'{NAMES_FILE}' is not a file"
        
        # Check file is not empty
        with open(names_file_path, 'r', encoding='utf-8') as f:
            content = f.read().strip()
            assert len(content) > 0, f"Names file '{NAMES_FILE}' is empty"

