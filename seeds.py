"""
Gen 0 seed storage.

A "seed" here is a snapshot of Generation 0 only: each cat's name, solid color,
and body-part references (body_1, ear_2, ...). Later generations are never saved —
they are re-rolled (and re-named) by inheritance every run.
"""

from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import Any, Dict, List

from config import SEEDS_FILE, RGB

logger = logging.getLogger(__name__)

PART_ORDER = ['ear', 'eyes', 'body', 'tail', 'legs']


def _empty_store() -> Dict[str, Any]:
    return {'seeds': []}


def load_store(filepath: str = SEEDS_FILE) -> Dict[str, Any]:
    """Load the seeds JSON file, or return an empty store if missing."""
    path = Path(filepath)
    if not path.exists():
        return _empty_store()
    with open(path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    if 'seeds' not in data or not isinstance(data['seeds'], list):
        raise ValueError(f"Invalid seeds file format: {filepath}")
    return data


def save_store(store: Dict[str, Any], filepath: str = SEEDS_FILE) -> None:
    """Write the seeds store to disk (pretty-printed)."""
    path = Path(filepath)
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(store, f, indent=2, ensure_ascii=False)
        f.write('\n')
    logger.info(f"Saved seeds to {filepath}")


def list_seeds(filepath: str = SEEDS_FILE) -> List[Dict[str, Any]]:
    """Return all saved seeds (may be empty)."""
    return load_store(filepath)['seeds']


def get_seed(seed_id: int, filepath: str = SEEDS_FILE) -> Dict[str, Any]:
    """Look up a seed by numeric id. Raises KeyError if missing."""
    for seed in list_seeds(filepath):
        if seed.get('id') == seed_id:
            return seed
    raise KeyError(f"Seed id {seed_id} not found in {filepath}")


def append_seed(
    cats: List[Dict[str, Any]],
    filepath: str = SEEDS_FILE,
) -> int:
    """
    Append a new Gen 0 seed and return its id.

    Each cat dict must have:
      - name: str
      - color: [R, G, B]
      - parts: {ear, eyes, body, tail, legs} -> refs like 'body_1'
    """
    store = load_store(filepath)
    next_id = 1
    if store['seeds']:
        next_id = max(s['id'] for s in store['seeds']) + 1

    entry = {'id': next_id, 'cats': cats}
    store['seeds'].append(entry)
    save_store(store, filepath)
    logger.info(f"Appended Gen 0 seed #{next_id} ({len(cats)} cats)")
    return next_id


def make_cat_snapshot(
    name: str,
    color: RGB,
    part_refs: Dict[str, str],
) -> Dict[str, Any]:
    """Build one Gen 0 cat record for the seeds file."""
    missing = [p for p in PART_ORDER if p not in part_refs]
    if missing:
        raise ValueError(f"Missing part refs: {missing}")
    return {
        'name': name,
        'color': list(color),
        'parts': {p: part_refs[p] for p in PART_ORDER},
    }


def format_seed_summary(seed: Dict[str, Any]) -> str:
    """One-line human summary of a seed for --list-seeds."""
    cats = seed.get('cats', [])
    names = [c.get('name', '?') for c in cats]
    return f"#{seed['id']}: {', '.join(names)}"
