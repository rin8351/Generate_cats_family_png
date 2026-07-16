"""
Simplified tests for the Cat Family Generator project
Tests only the essential requirements for the project to work correctly
"""
from pathlib import Path
from cats_colors import CATS_COLORS
from config import (
    GRAY_COLORS, CAT_PARTS_FOLDERS, NAMES_FILE, GENETICS_PARAMS,
    CHILD_COLOR_COUNT_WEIGHTS,
)
from cat import Gene, build_color_map, MAIN_BODY_GRAY


class TestProjectStructure:
    """Test essential project structure and configuration"""
    
    def test_required_folders_exist_and_not_empty(self):
        """Test that required body part folders exist and contain images"""
        # Check there are at least 5 folders configured
        assert len(CAT_PARTS_FOLDERS) >= 5, "Should have at least 5 body part folders"

        # Check each configured folder exists and is not empty
        for part_name, folder_name in CAT_PARTS_FOLDERS.items():
            folder_path = Path(folder_name)
            assert folder_path.exists(), f"Folder '{folder_name}' ({part_name}) does not exist"
            assert folder_path.is_dir(), f"'{folder_name}' is not a directory"

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


class TestGeneStrength:
    """Test the gene 'strength' system"""

    def test_genetics_params_present(self):
        """GENETICS_PARAMS must expose the strength tuning knobs"""
        for key in (
            'base_strength', 'match_bonus', 'win_bonus', 'main_body_bonus',
            'child_color_count_weights', 'strict_color_from_generation',
            'spillover_chance', 'mutation_chance', 'mutation_strength',
        ):
            assert key in GENETICS_PARAMS, f"GENETICS_PARAMS missing '{key}'"
        assert set(CHILD_COLOR_COUNT_WEIGHTS) == {2, 3, 4, 5, 6}
        assert all(w >= 0 for w in CHILD_COLOR_COUNT_WEIGHTS.values())

    def test_strict_color_picks_strongest(self):
        """Gen 2+ must take top colors by strength, not weak accents"""
        from cat import Cat, Gene, inherit_color_genes
        from unittest.mock import MagicMock, patch

        def fake_parent(colors_with_strength):
            cat = MagicMock(spec=Cat)
            cat.color_genes = [
                Gene(color, strength) for color, strength in colors_with_strength
            ]
            return cat

        purple, yellow, blue = (200, 100, 200), (255, 255, 0), (100, 150, 255)
        p1 = fake_parent([(purple, 5.0), (blue, 1.0)])
        p2 = fake_parent([(yellow, 5.0)])

        # Force child to carry exactly 2 colors so the weak one is excluded
        with patch('cat.pick_child_color_count', return_value=2):
            with patch('cat.random.random', return_value=1.0):  # no spillover
                genes = inherit_color_genes(p1, p2, generation=2)
        colors = {g.value for g in genes}
        assert blue not in colors, "Weak blue must not enter Gen 2+ genome"
        assert purple in colors and yellow in colors
        assert max(genes, key=lambda g: g.strength).value in (purple, yellow)

    def test_parent_main_colors_always_inherited(self):
        """Both parents' main (strongest) colors must survive into the child"""
        from cat import Cat, Gene, inherit_color_genes
        from unittest.mock import MagicMock, patch

        def fake_parent(colors_with_strength):
            cat = MagicMock(spec=Cat)
            cat.color_genes = [
                Gene(color, strength) for color, strength in colors_with_strength
            ]
            return cat

        teal, pink, weak_a, weak_b, weak_c = (
            (114, 207, 190), (255, 182, 193),
            (10, 10, 10), (20, 20, 20), (30, 30, 30),
        )
        # Teal is Oscar's main; pink is the other GK's main.
        # Extra mid-strength accents must not push teal out.
        p1 = fake_parent([
            (teal, 8.0), (weak_a, 3.0), (weak_b, 3.0), (weak_c, 3.0),
        ])
        p2 = fake_parent([(pink, 7.0), (weak_a, 4.0), (weak_b, 4.0)])

        with patch('cat.pick_child_color_count', return_value=4):
            with patch('cat.random.random', return_value=1.0):  # no spillover
                genes = inherit_color_genes(p1, p2, generation=3)
        colors = {g.value for g in genes}
        assert teal in colors, "Parent main (teal) must not vanish"
        assert pink in colors, "Parent main (pink) must not vanish"

    def test_main_body_bonus_reinforces_strongest(self):
        """Claiming (252,252,252) adds main_body_bonus to that gene"""
        from cat import Gene, reinforce_main_body_gene

        strong = (114, 207, 190)
        weak = (255, 182, 193)
        bonus = GENETICS_PARAMS['main_body_bonus']
        genes = reinforce_main_body_gene([
            Gene(strong, 5.0), Gene(weak, 2.0),
        ])
        by_color = {g.value: g.strength for g in genes}
        assert by_color[strong] == 5.0 + bonus
        assert by_color[weak] == 2.0

    def test_gen3_main_is_one_of_gen2_mains(self):
        """After reinforce, child's main color is one of the two parent mains"""
        from cat import Cat, Gene, inherit_color_genes, reinforce_main_body_gene
        from unittest.mock import MagicMock, patch

        def fake_parent(colors_with_strength):
            cat = MagicMock(spec=Cat)
            cat.color_genes = [
                Gene(color, strength) for color, strength in colors_with_strength
            ]
            return cat

        teal, pink, accent = (114, 207, 190), (255, 182, 193), (200, 200, 50)
        p1 = fake_parent([(teal, 6.0), (accent, 2.0)])
        p2 = fake_parent([(pink, 5.5)])

        with patch('cat.pick_child_color_count', return_value=3):
            with patch('cat.random.random', return_value=1.0):  # no spillover
                genes = reinforce_main_body_gene(
                    inherit_color_genes(p1, p2, generation=3)
                )
        main = max(genes, key=lambda g: g.strength).value
        assert main in (teal, pink)

    def test_main_gray_is_strongest_across_whole_cat(self):
        """(252,252,252) is strongest; other grays use weaker genes only"""
        strong = (10, 20, 30)
        weak = (200, 210, 220)
        color_map = build_color_map([Gene(strong, 10.0), Gene(weak, 1.0)])

        assert color_map[MAIN_BODY_GRAY] == strong
        other = [v for g, v in color_map.items() if g != MAIN_BODY_GRAY]
        assert other, "Expected other gray shades to be mapped"
        assert all(v == weak for v in other), "Weaker grays must not use strongest"

    def test_single_color_paints_all_grays(self):
        """A cat with one color gene maps every gray to that color"""
        only = (123, 45, 67)
        color_map = build_color_map([Gene(only, 1.0)])
        assert all(v == only for v in color_map.values())
        assert set(color_map.keys()) == set(GRAY_COLORS)

    def test_every_allele_paints_at_least_one_gray(self):
        """Even a tiny mutation gene must appear on at least one accent gray"""
        cream = (245, 245, 220)
        peach = (255, 228, 181)
        pink = (255, 182, 193)
        mut = (153, 247, 230)
        color_map = build_color_map([
            Gene(cream, 6.5),
            Gene(peach, 5.5),
            Gene(pink, 4.5),
            Gene(mut, 0.5),
        ])
        assert color_map[MAIN_BODY_GRAY] == cream
        painted = set(color_map.values())
        assert mut in painted, "Mutation listed in genome must show on the cat"
        assert cream in painted and peach in painted and pink in painted

    def test_spillover_adds_next_color_by_strength(self):
        """With spillover, the 5th-strongest merged color may enter the genome"""
        from cat import Cat, Gene, inherit_color_genes
        from unittest.mock import MagicMock, patch

        def fake_parent(colors_with_strength):
            cat = MagicMock(spec=Cat)
            cat.color_genes = [
                Gene(color, strength) for color, strength in colors_with_strength
            ]
            return cat

        # 5 distinct colors; quota 4 → 5th is spillover candidate
        c1, c2, c3, c4, c5 = (
            (10, 0, 0), (20, 0, 0), (30, 0, 0), (40, 0, 0), (50, 0, 0),
        )
        p1 = fake_parent([(c1, 8.0), (c3, 4.0), (c5, 1.0)])
        p2 = fake_parent([(c2, 7.0), (c4, 3.0)])

        with patch('cat.pick_child_color_count', return_value=4):
            with patch('cat.random.random', return_value=0.0):  # force spillover
                genes = inherit_color_genes(p1, p2, generation=2)

        colors = {g.value for g in genes}
        assert len(colors) == 5
        assert c5 in colors, "5th by strength should spill over"
        assert {c1, c2, c3, c4, c5} == colors

    def test_mutation_adds_weak_gene_from_lineage(self):
        """Mutation appends one weak Gen0/Gen1 color into the genome"""
        from cat import Cat, Gene, maybe_add_mutation_gene
        from unittest.mock import MagicMock, patch

        teal = (114, 207, 190)
        pink = (255, 182, 193)
        throwback = (153, 247, 230)  # Gen 0 color not in child genome

        def fake_cat(generation, colors, parent1=None, parent2=None):
            cat = MagicMock(spec=Cat)
            cat.generation = generation
            cat.color_genes = [Gene(c, 1.0) for c in colors]
            cat.parent1 = parent1
            cat.parent2 = parent2
            return cat

        # Lineage: Gen0 throwback -> Gen1 pink parent
        g0 = fake_cat(0, [throwback])
        p1 = fake_cat(1, [pink], parent1=g0)
        p2 = fake_cat(1, [teal])
        child_genes = [Gene(pink, 3.5), Gene(teal, 3.5)]

        with patch('cat.random.random', return_value=0.0):
            with patch('cat.random.choice', return_value=throwback):
                result = maybe_add_mutation_gene(child_genes, p1, p2)

        assert len(result) == 3
        assert result[-1].value == throwback
        assert result[-1].strength == GENETICS_PARAMS['mutation_strength']
        assert max(result, key=lambda g: g.strength).value in (pink, teal)

    def test_mutation_pool_includes_gen0_and_gen1(self):
        """Mutation pool gathers colors from Gen 0 and Gen 1 only"""
        from cat import Cat, Gene, mutation_color_pool
        from unittest.mock import MagicMock

        def fake_cat(generation, colors, parent1=None, parent2=None):
            cat = MagicMock(spec=Cat)
            cat.generation = generation
            cat.color_genes = [Gene(c, 1.0) for c in colors]
            cat.parent1 = parent1
            cat.parent2 = parent2
            return cat

        c0a, c0b, c1, c2 = (
            (1, 1, 1), (2, 2, 2), (3, 3, 3), (4, 4, 4),
        )
        g0a = fake_cat(0, [c0a])
        g0b = fake_cat(0, [c0b])
        g1 = fake_cat(1, [c1], parent1=g0a, parent2=g0b)
        g2 = fake_cat(2, [c2], parent1=g1)  # Gen2 color must NOT enter pool

        other = fake_cat(1, [(9, 9, 9)])
        pool = mutation_color_pool(g2, other)
        assert c0a in pool and c0b in pool and c1 in pool
        assert (9, 9, 9) in pool
        assert c2 not in pool, "Gen 2 colors must not be mutation sources"


class TestSeeds:
    """Test Gen 0 seed save/load helpers"""

    def test_part_ref_roundtrip(self):
        from image_processing import CatImageBuilder
        ref = CatImageBuilder.part_ref('body', '3')
        assert ref == 'body_3'
        assert CatImageBuilder.parse_part_ref(ref) == ('body', '3')

    def test_append_and_get_seed(self, tmp_path):
        from seeds import append_seed, get_seed, make_cat_snapshot

        path = str(tmp_path / 'seeds.json')
        cats = [
            make_cat_snapshot(
                f'Cat{i}',
                (10, 20, 30),
                {
                    'ear': 'ear_1', 'eyes': 'eyes_2', 'body': 'body_3',
                    'tail': 'tail_4', 'legs': 'legs_5',
                },
            )
            for i in range(8)
        ]
        seed_id = append_seed(cats, filepath=path)
        loaded = get_seed(seed_id, filepath=path)
        assert loaded['id'] == seed_id
        assert len(loaded['cats']) == 8
        assert loaded['cats'][0]['name'] == 'Cat0'
        assert loaded['cats'][0]['color'] == [10, 20, 30]
        assert loaded['cats'][0]['parts']['body'] == 'body_3'

