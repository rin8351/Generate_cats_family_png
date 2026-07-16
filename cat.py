"""
Each trait (color and every body part) is a separate gene carrying a
`strength` value. Stronger genes are more likely to win inheritance and,
for colors, cover a larger share of the body. Strength grows in three ways:
  * match_bonus      - when both parents share the same allele (dominance),
  * win_bonus        - each time a gene wins inheritance,
  * main_body_bonus  - when a color claims the main fur gray (252, 252, 252).

Rare mutations add a weak extra color allele from Gen 0/1 lineage colors
into the child's genome (heritable, visible in the legend).

By Gen 2–3 the strongest colors and parts dominate. Each child's main body
color is always chosen from the parents' main colors (which keep accumulating
strength), so Gen 3's main fur is one of the two Gen 2 mains.
"""

import random
import logging
from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Set, Tuple

from PIL import Image

from config import GRAY_COLORS, RGB, GENETICS_PARAMS, CHILD_COLOR_COUNT_WEIGHTS
from image_processing import CatImageBuilder

logger = logging.getLogger(__name__)

PART_LOCI = ['ear', 'eyes', 'body', 'tail', 'legs']
MAIN_BODY_GRAY: RGB = (252, 252, 252)


@dataclass
class Gene:
    """A single heritable trait value with its inheritance strength."""
    value: Any        # RGB tuple (color) or a PIL.Image (body part)
    strength: float


def pick_child_color_count() -> int:
    """
    Pick how many color alleles a child carries, using CHILD_COLOR_COUNT_WEIGHTS.

    Weights are treated as percentages (or any relative shares) and normalized.
    Counts with weight 0 are skipped.
    """
    weights_map = GENETICS_PARAMS.get(
        'child_color_count_weights', CHILD_COLOR_COUNT_WEIGHTS
    )
    options = [n for n, w in sorted(weights_map.items()) if w > 0]
    if not options:
        return 4
    weights = [weights_map[n] for n in options]
    return random.choices(options, weights=weights, k=1)[0]


def _weighted_choice(genes: List[Gene]) -> Gene:
    """Pick one gene with probability proportional to its strength."""
    weights = [max(g.strength, 0.0) for g in genes]
    if sum(weights) <= 0:
        return random.choice(genes)
    return random.choices(genes, weights=weights, k=1)[0]


def _weighted_sample(pool: Dict[Any, float], k: int) -> List[Any]:
    """Sample up to k distinct keys, weighted by their strength values."""
    values = list(pool.keys())
    weights = [max(pool[v], 0.0) for v in values]
    chosen: List[Any] = []
    for _ in range(min(k, len(values))):
        if sum(weights) <= 0:
            pick = random.choice(values)
        else:
            pick = random.choices(values, weights=weights, k=1)[0]
        idx = values.index(pick)
        chosen.append(pick)
        values.pop(idx)
        weights.pop(idx)
    return chosen


def _innate_strength() -> float:
    """Innate strength of a Gen 0 gene, with optional random jitter."""
    base = GENETICS_PARAMS['base_strength']
    jitter = GENETICS_PARAMS.get('random_innate_jitter', 0.0)
    if jitter:
        return max(0.1, base + random.uniform(-jitter, jitter))
    return base


def _main_color(cat: 'Cat') -> RGB:
    """The color that claims MAIN_BODY_GRAY for this cat (strongest gene)."""
    return max(cat.color_genes, key=lambda g: g.strength).value


def collect_lineage_colors(cat: 'Cat', max_generation: int = 1) -> Set[RGB]:
    """
    Collect colors from ``cat`` and its ancestors up to ``max_generation``.

    Used as the mutation pool: Gen 0 founders and Gen 1 kittens only
    (not Gen 2+), and never a fresh pick from the full CATS_COLORS palette.
    """
    colors: Set[RGB] = set()

    def walk(node: Optional['Cat']) -> None:
        if node is None:
            return
        if node.generation <= max_generation:
            for gene in node.color_genes:
                colors.add(gene.value)
        walk(node.parent1)
        walk(node.parent2)

    walk(cat)
    return colors


def mutation_color_pool(parent1: 'Cat', parent2: 'Cat') -> Set[RGB]:
    """Gen 0 + Gen 1 colors available for a mutation in this child's lineage."""
    return collect_lineage_colors(parent1) | collect_lineage_colors(parent2)


def maybe_add_mutation_gene(
    color_genes: List[Gene],
    parent1: 'Cat',
    parent2: 'Cat',
) -> List[Gene]:
    """
    Rarely append one weak color gene from Gen 0/1 lineage colors.

    The mutation becomes a real allele in the genome (shows in the legend,
    can be inherited). It stays weak so it will not claim MAIN_BODY_GRAY.
    Prefers a color not already carried by the child.
    """
    chance = GENETICS_PARAMS.get('mutation_chance', 0.0)
    if chance <= 0 or random.random() >= chance:
        return color_genes

    carried = {g.value for g in color_genes}
    pool = mutation_color_pool(parent1, parent2) - carried
    if not pool:
        # Fall back to any lineage color if everything is already carried
        pool = mutation_color_pool(parent1, parent2)
    if not pool:
        return color_genes

    mut_color = random.choice(list(pool))
    mut_strength = GENETICS_PARAMS.get('mutation_strength', 0.5)
    # If the color somehow already exists, keep the stronger allele only
    if mut_color in carried:
        return color_genes

    logger.info(
        f"Color mutation: added {mut_color} (strength {mut_strength})"
    )
    return list(color_genes) + [Gene(mut_color, mut_strength)]


def inherit_part_genes(parent1: 'Cat', parent2: 'Cat') -> Dict[str, Gene]:
    """
    Inherit body-part genes from two parents using gene strength.

    If both parents carry the same allele (same underlying image object),
    the child inherits it for sure with combined + bonus strength. Otherwise
    the winner is chosen weighted by strength and gains ``win_bonus``.
    """
    match_bonus = GENETICS_PARAMS['match_bonus']
    win_bonus = GENETICS_PARAMS['win_bonus']

    genes: Dict[str, Gene] = {}
    for locus in PART_LOCI:
        g1 = parent1.part_genes[locus]
        g2 = parent2.part_genes[locus]
        if g1.value is g2.value:
            genes[locus] = Gene(g1.value, g1.strength + g2.strength + match_bonus)
        else:
            winner = _weighted_choice([g1, g2])
            genes[locus] = Gene(winner.value, winner.strength + win_bonus)
    return genes


def inherit_color_genes(
    parent1: 'Cat',
    parent2: 'Cat',
    generation: int = 1,
) -> List[Gene]:
    """
    Inherit color genes from two parents using gene strength.

    Both parents' main-body colors are always kept in the child genome so a
    strong main (e.g. turquoise that already claimed 252 on a parent) cannot
    vanish in the next generation. Remaining slots are filled by strength.

    Colors shared by both parents are reinforced (match_bonus). Each inherited
    color gains ``win_bonus``; the eventual main-body winner gets an extra
    ``main_body_bonus`` via ``reinforce_main_body_gene``.

    With ``spillover_chance``, the next color by strength after the normal
    quota (e.g. 5th when the quota is 4) may also enter — pure randomness,
    separate from Gen 0/1 mutations.
    """
    match_bonus = GENETICS_PARAMS['match_bonus']
    win_bonus = GENETICS_PARAMS['win_bonus']
    strict_from = GENETICS_PARAMS.get('strict_color_from_generation', 2)
    spillover_chance = GENETICS_PARAMS.get('spillover_chance', 0.0)

    def to_dict(genes: List[Gene]) -> Dict[RGB, float]:
        d: Dict[RGB, float] = {}
        for g in genes:
            d[g.value] = max(d.get(g.value, 0.0), g.strength)
        return d

    d1 = to_dict(parent1.color_genes)
    d2 = to_dict(parent2.color_genes)

    merged: Dict[RGB, float] = {}
    for color in set(d1) | set(d2):
        if color in d1 and color in d2:
            merged[color] = d1[color] + d2[color] + match_bonus
        else:
            merged[color] = d1.get(color, d2.get(color, 0.0))

    # Parent mains must survive — these are the colors that painted (252,252,252)
    must_keep: List[RGB] = []
    for main in (_main_color(parent1), _main_color(parent2)):
        if main not in must_keep:
            must_keep.append(main)

    num = min(len(merged), max(pick_child_color_count(), len(must_keep)))
    selected: List[RGB] = list(must_keep)
    remaining_slots = num - len(selected)
    remaining = {c: s for c, s in merged.items() if c not in selected}

    if remaining_slots > 0 and remaining:
        if generation >= strict_from:
            ranked = sorted(remaining.keys(), key=lambda c: remaining[c], reverse=True)
            selected.extend(ranked[:remaining_slots])
        else:
            selected.extend(_weighted_sample(remaining, remaining_slots))

    # Occasional spillover: next color by strength after the normal quota
    leftover = {c: s for c, s in merged.items() if c not in selected}
    if leftover and spillover_chance > 0 and random.random() < spillover_chance:
        next_color = max(leftover.keys(), key=lambda c: leftover[c])
        selected.append(next_color)
        logger.debug(f"Color spillover: added {next_color} (rank by strength)")

    return [Gene(color, merged[color] + win_bonus) for color in selected]


def reinforce_main_body_gene(color_genes: List[Gene]) -> List[Gene]:
    """
    Add ``main_body_bonus`` to the strongest color gene.

    That gene is the one that will paint MAIN_BODY_GRAY; boosting it here
    makes the claim stick harder in subsequent generations.
    """
    if not color_genes:
        return color_genes

    bonus = GENETICS_PARAMS.get('main_body_bonus', 0.0)
    if bonus <= 0:
        return color_genes

    strongest = max(color_genes, key=lambda g: g.strength)
    reinforced: List[Gene] = []
    boosted = False
    for g in color_genes:
        if not boosted and g.value == strongest.value and g.strength == strongest.strength:
            reinforced.append(Gene(g.value, g.strength + bonus))
            boosted = True
        else:
            reinforced.append(g)
    return reinforced


def build_color_map(color_genes: List[Gene]) -> Dict[RGB, RGB]:
    """
    Map each gray shade to one color for the whole cat (all body parts).

    * (252, 252, 252) → strongest gene (main fur across the whole cat);
    * other gray shades → weaker genes, shared by strength
      (if only one color gene, every gray becomes that color).

    Every color allele gets at least one accent gray when possible, so a
    listed mutation (even at strength 0.5) always shows on the cat.
    """
    genes = sorted(color_genes, key=lambda g: g.strength, reverse=True)
    strongest = genes[0]
    color_map: Dict[RGB, RGB] = {MAIN_BODY_GRAY: strongest.value}

    other_grays = [g for g in GRAY_COLORS if g != MAIN_BODY_GRAY]
    weak_genes = genes[1:]

    if not weak_genes:
        for gray in other_grays:
            color_map[gray] = strongest.value
        return color_map

    n_grays = len(other_grays)
    n_weak = len(weak_genes)

    # Guarantee visibility: each allele paints ≥1 gray when there are enough
    if n_weak <= n_grays:
        counts = [1] * n_weak
        leftover = n_grays - n_weak
        if leftover > 0:
            total = sum(g.strength for g in weak_genes)
            if total <= 0:
                raw = [leftover / n_weak] * n_weak
            else:
                raw = [leftover * g.strength / total for g in weak_genes]
            extras = [int(r) for r in raw]
            rem = leftover - sum(extras)
            by_frac = sorted(
                range(n_weak),
                key=lambda i: raw[i] - extras[i],
                reverse=True,
            )
            for i in range(rem):
                extras[by_frac[i % n_weak]] += 1
            counts = [1 + e for e in extras]
    else:
        # More alleles than accent grays — strongest weak genes win slots
        total = sum(g.strength for g in weak_genes)
        if total <= 0:
            raw = [n_grays / n_weak] * n_weak
        else:
            raw = [n_grays * g.strength / total for g in weak_genes]
        counts = [int(r) for r in raw]
        rem = n_grays - sum(counts)
        by_frac = sorted(
            range(n_weak),
            key=lambda i: raw[i] - counts[i],
            reverse=True,
        )
        for i in range(rem):
            counts[by_frac[i % n_weak]] += 1

    shuffled = other_grays[:]
    random.shuffle(shuffled)
    idx = 0
    for gene, count in zip(weak_genes, counts):
        for _ in range(count):
            color_map[shuffled[idx]] = gene.value
            idx += 1
    while idx < len(shuffled):
        color_map[shuffled[idx]] = weak_genes[0].value
        idx += 1

    return color_map


class Cat:
    """Represents a cat with a genome (color + body-part genes)."""

    def __init__(self, name: str, part_genes: Dict[str, Gene],
                 color_genes: List[Gene], generation: int):
        self.name = name
        self.generation = generation
        self.part_genes = part_genes
        # Main-body claim boosts strength before it is passed to children
        self.color_genes = reinforce_main_body_gene(color_genes)
        self.parts: Dict[str, Image.Image] = {
            loc: gene.value for loc, gene in part_genes.items()
        }
        # Representative single color (strongest), kept for compatibility
        self.color: RGB = max(self.color_genes, key=lambda g: g.strength).value
        self.parent1: Optional['Cat'] = None
        self.parent2: Optional['Cat'] = None
        self.image: Optional[Image.Image] = None
        logger.debug(f"Created cat: {name} (Gen {generation})")

    def _label_title(self) -> str:
        return f"{self.name} (Gen {self.generation})"

    def _color_strengths(self) -> List[Tuple[RGB, float]]:
        """Color genes strongest-first for the under-cat legend."""
        ranked = sorted(self.color_genes, key=lambda g: g.strength, reverse=True)
        return [(g.value, g.strength) for g in ranked]

    def generate_image(self) -> Image.Image:
        """Render the cat from its genome (parts + strength-weighted colors)."""
        img = CatImageBuilder.combine_parts(self.parts)
        color_map = build_color_map(self.color_genes)
        img = CatImageBuilder.apply_color_numpy(img, color_map)
        CatImageBuilder.add_cat_label(img, self._label_title(), self._color_strengths())
        self.image = img
        logger.info(f"Generated image for {self.name} (Gen {self.generation})")
        return img

    def __repr__(self) -> str:
        return f"Cat(name='{self.name}', gen={self.generation}, color={self.color})"


class ParentCat(Cat):
    """Gen 0 cat: single color, innate gene strengths."""

    def __init__(self, name: str, color: RGB, parts: Dict[str, Image.Image]):
        part_genes = {
            loc: Gene(parts[loc], _innate_strength()) for loc in PART_LOCI
        }
        color_genes = [Gene(color, _innate_strength())]
        super().__init__(name, part_genes, color_genes, generation=0)


class OffspringCat(Cat):
    """A cat whose genome is inherited from two parents with gene strength."""

    def __init__(self, name: str, parent1: Cat, parent2: Cat, generation: int):
        part_genes = inherit_part_genes(parent1, parent2)
        color_genes = inherit_color_genes(parent1, parent2, generation)
        color_genes = maybe_add_mutation_gene(color_genes, parent1, parent2)
        super().__init__(name, part_genes, color_genes, generation)
        self.parent1 = parent1
        self.parent2 = parent2


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
        self.kittens: List[OffspringCat] = []
        self.grandkittens: List[OffspringCat] = []
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
        """Create a Gen 0 parent cat."""
        if name is None:
            name = self.get_random_name()

        parent = ParentCat(name, color, parts)
        self.parents.append(parent)
        self.all_cats.append(parent)

        logger.info(f"Created parent: {name}")
        return parent

    def create_kitten(self, parent1: Cat, parent2: Cat,
                      name: str = None) -> OffspringCat:
        """Create a Gen 1 kitten from two parents."""
        if name is None:
            name = self.get_random_name()

        kitten = OffspringCat(name, parent1, parent2, generation=1)
        self.kittens.append(kitten)
        self.all_cats.append(kitten)

        logger.info(f"Created kitten: {name}")
        return kitten

    def create_grandkitten(self, parent1: Cat, parent2: Cat,
                           name: str = None) -> OffspringCat:
        """Create a grandkitten (Gen 2) or great-grandkitten (Gen 3)."""
        if name is None:
            name = self.get_random_name("GrandKitten ")

        generation = 3 if parent1.generation >= 2 and parent2.generation >= 2 else 2
        grandkitten = OffspringCat(name, parent1, parent2, generation)
        self.grandkittens.append(grandkitten)
        self.all_cats.append(grandkitten)

        logger.info(f"Created grandkitten: {name} (Gen {generation})")
        return grandkitten
