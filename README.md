# 🐱 Cat Family Generator

## Example

<img src="cats_family_preview.png" alt="Cat family pedigree (preview)" width="500">

[Full resolution output](cats_family.png)

## 📋 Table of Contents
- [Overview](#-overview)
- [Installation](#-installation)
- [Usage](#-usage)
- [Testing](#-testing)
- [Project Structure](#-project-structure)
- [How It Works](#-how-it-works)
- [Genetics](#-genetics)
- [Configuration](#️-configuration)
- [Examples](#-examples)


## Overview

The Cat Family Generator creates multi-generational cat families by combining body parts (ears, eyes, body, tail, legs) and applying a **strength-based genetics** system for colors and shapes. Traits are inherited from parents across four generations; stronger genes win more often and accumulate power over time.



## How It Works

### 1. **Image Loading**
The `ImageLoader` class validates and loads cat body parts from folders under `parts/`:
- Ears (`parts/ear/`)
- Eyes (`parts/eyes/`)
- Body (`parts/body/`)
- Tail (`parts/tail/`)
- Legs (`parts/legs/`)

You can draw and add more PNG variants into any of these folders — they will be picked up automatically.

### 2. **Part Combination**
`CatImageBuilder` arranges parts vertically:
```
┌─────────┐
│  Ears   │
├─────────┤
│  Eyes   │
├─────────┼───────┐
│  Body   │ Tail  │
├─────────┴───────┤
│      Legs       │
└─────────────────┘
```

### 3. **Color Application**
Original images use grayscale templates. Colors are applied by:
1. Detecting gray shades in the template
2. Mapping each shade to a genetic color (strongest → main body `(252, 252, 252)`)
3. Using NumPy for efficient pixel replacement

### 4. **Family Layout**
The final image is a left-to-right pedigree: generations are columns, children sit vertically between their parents, and bracket lines connect each pair to their child.

```
Gen 0          Gen 1         Gen 2          Gen 3
────────       ──────        ──────         ──────
Parent1 ──┐
          ├── Kitten1 ──┐
Parent2 ──┘             │
                        ├── GrandKitten1 ──┐
Parent3 ──┐             │                  │
          ├── Kitten2 ──┘                  │
Parent4 ──┘                                ├── GreatGrandKitten
Parent5 ──┐                                │
          ├── Kitten3 ──┐                  │
Parent6 ──┘             │                  │
                        ├── GrandKitten2 ──┘
Parent7 ──┐             │
          ├── Kitten4 ──┘
Parent8 ──┘
```

Each cat is labeled with its name, generation, and a legend of its color genes (swatch + strength).


##  Genetics

Colors and body parts are genes with
**strength** that grows when they win, match in both parents, or (for colors)
paint the main fur. By Gen 2–3, strong traits dominate.

**Full write-up:** [`GENETICS.md`](GENETICS.md)

### Quick knobs (`config.py`)

The main control for how many colors a kitten carries:

```python
CHILD_COLOR_COUNT_WEIGHTS = {
    2: 10,   # 10%
    3: 25,   # 25%
    4: 40,   # 40%
    5: 20,   # 20%
    6: 5,    # 5%
}
```

Edit these percentages freely (normalized if they do not sum to 100; `0` disables a count).

Other genetics settings live in `GENETICS_PARAMS` (strength bonuses, spillover,
mutation chance, etc.) — see [`GENETICS.md`](GENETICS.md).


## Configuration

### Color Palette (`cats_colors.py`)

Cat colors live in a separate file: `cats_colors.py`. You can extend the list with any colors you like. Use RGB tuples in the form `(R, G, B)` with values from 0 to 255. The built-in palette is mostly soft pastel shades, but you can add brighter or darker colors as well.

```python
CATS_COLORS = [
    (255, 193, 204),  # example pastel pink
    (255, 0, 0),      # add your own RGB colors
    (0, 255, 0),
    # ...
]
```

### Cat Names (`cats_name.TXT`)

Cat names are taken from `cats_name.TXT`. Put any names you like there — one name per line. They will be used when labeling cats in the family image.

### Other settings (`config.py`)

Edit `config.py` for paths, fonts, layout, genetics, and output options. Gen 0
snapshots can be saved/reloaded via `seeds.json`.

### Command-Line Options

| Option | Description | Default |
|--------|-------------|---------|
| `-o`, `--output` | Output filename | `cats_family.png` |
| `--load-seed ID` | Replay Gen 0 from `seeds.json` (kids re-rolled) | — |
| `--list-seeds` | List saved Gen 0 seeds and exit | — |
| `--no-save-seed` | Do not append a new random Gen 0 to seeds | Off |
| `-v`, `--verbose` | Enable debug logging | Off |
| `--log` | Save logs to file | None |
| `-h`, `--help` | Show help message | - |

## Project Structure

```
Generate_cats_family_png/
├── main.py                 # Main entry point with CLI
├── cat.py                  # Cat classes and genetics logic
├── image_processing.py     # Image manipulation and combining
├── config.py               # Paths, layout, genetics knobs
├── cats_colors.py          # Cat color palette (edit to add colors)
├── seeds.py / seeds.json   # Save / reload Gen 0 founders
├── requirements.txt        # Python dependencies
├── README.md               # This file
├── GENETICS.md             # Genetics system (strength, weights, mutation)
├── .gitignore              # Git ignore patterns
├── cats_name.TXT           # List of cat names
├── cats_family.png         # Example output (full size)
├── cats_family_preview.png # README preview
├── parts/                  # Cat body part images
│   ├── body/               # Body variants (PNG)
│   ├── ear/                # Ear variants (PNG)
│   ├── eyes/               # Eye variants (PNG)
│   ├── legs/               # Leg variants (PNG)
│   └── tail/               # Tail variants (PNG)
└── tests/                  # Project tests
```

### Custom body parts

Want more variety? Draw your own parts and drop PNG files into the matching folder under `parts/` (for example `parts/ear/8.png`). Use the same grayscale style as the existing assets so coloring still works. New files are included automatically — no code changes needed.
## Installation

### Prerequisites

- Python 3.8 or higher
- pip (Python package manager)

### Steps

1. **Clone the repository**
   ```bash
   git clone https://github.com/rin8351/Generate_cats_family_png.git
   cd Generate_cats_family_png
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Verify installation**
   ```bash
   python main.py --help
   ```

## Testing

Tests live in `tests/` and are run with [pytest](https://pytest.org/) (configured in `pytest.ini`). They are not called from the generator itself — run them separately:

```bash
pytest
```

Or explicitly:

```bash
pytest tests/ -v
```

On every push and pull request to `main`/`master`, GitHub Actions runs the same suite (see `.github/workflows/tests.yml`).

## Usage

### Basic Usage

Generate a cat family with default settings:

```bash
python main.py
```

This creates `cats_family.png` in the current directory. This creates cats_family.png in the current directory. Each run overwrites that file; use -o to save under a different name.

### Advanced Usage

**Custom output filename:**
```bash
python main.py -o my_awesome_cats.png
```

**Replay Gen 0 from a saved seed** (later generations still re-roll):
```bash
python main.py --load-seed 3
```

**List saved Gen 0 seeds:**
```bash
python main.py --list-seeds
```

**Verbose logging:**
```bash
python main.py -v
```

**Save logs to file:**
```bash
python main.py --log generation.log
```

### Generation / genetics parameters

Layout and fonts: `GENERATION_PARAMS` in `config.py`.  
Genetics (including **`CHILD_COLOR_COUNT_WEIGHTS`**): see [`GENETICS.md`](GENETICS.md).

### Output Settings
```python
OUTPUT_SETTINGS = {
    'default_filename': 'cats_family.png',
    'format': 'PNG',
    'quality': 95,
}
```

## Examples

### Example 1: Default Generation
```bash
python main.py
```
Generates a random cat family (Gen 0 is auto-saved to `seeds.json`).

### Example 2: Replay a Gen 0 seed
```bash
python main.py --load-seed 3 -o family_from_seed3.png
```
Same founders; Gen 1–3 are re-rolled by inheritance.

### Example 3: Debug Mode
```bash
python main.py -v --log debug.log
```
Generates cats while logging detailed information for troubleshooting.

