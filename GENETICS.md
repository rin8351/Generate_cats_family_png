# Genetics System

How color and body-part inheritance works in Cat Family Generator.

Traits are not pure coin-flips anymore. Each color and each body part is a
**gene** with a numeric **strength**. Stronger genes win inheritance more often,
paint more of the cat, and grow stronger across generations.

All knobs live in [`config.py`](config.py). The most important one for coat
variety is **`CHILD_COLOR_COUNT_WEIGHTS`** (see below).

---

## Quick picture

```
Gen 0  →  each founder: 1 color, random parts, innate strength
Gen 1  →  inherit parts + colors (weighted); weaker accents may sneak in
Gen 2+ →  same, but extra colors are taken by strength rank (stricter)
Gen 3  →  main body color is one of the two Gen 2 parents' main colors
```

Under each cat on the pedigree you see:

- name + generation  
- color swatches with strength values (strongest first)

---

## Genes and strength

| Gene type | What it stores | Strength grows when… |
|-----------|----------------|----------------------|
| **Color** | RGB allele | it wins inheritance (`win_bonus`), both parents share it (`match_bonus`), or it claims the main fur gray `(252, 252, 252)` (`main_body_bonus`) |
| **Body part** | ear / eyes / body / tail / legs image | it wins inheritance, or both parents share the same part (`match_bonus`) |

### Strength bonuses (`GENETICS_PARAMS`)

| Parameter | Default | Meaning |
|-----------|---------|---------|
| `base_strength` | `1.0` | Starting strength for Gen 0 genes |
| `match_bonus` | `1.0` | Extra when both parents carry the same allele |
| `win_bonus` | `0.5` | Extra after a gene wins inheritance |
| `main_body_bonus` | `1.0` | Extra for the color that paints `(252, 252, 252)` |
| `random_innate_jitter` | `0.0` | Optional ± spread on Gen 0 starting strength (`0` = all equal) |

Because of `main_body_bonus` + `win_bonus`, by Gen 2–3 the strongest colors
tend to dominate the main fur.

---

## How many colors a child gets

### `CHILD_COLOR_COUNT_WEIGHTS` — tune this freely

Defined at the top of [`config.py`](config.py):

```python
CHILD_COLOR_COUNT_WEIGHTS = {
    2: 10,   # 10%
    3: 25,   # 25%
    4: 40,   # 40%
    5: 20,   # 20%
    6: 5,    # 5%
}
```

For **each offspring**, the generator picks a target color count using these
weights as probabilities (percent-style).

- Change the numbers to favor fewer or more colors.  
- Weights are **normalized** if they do not sum to exactly 100.  
- Set a weight to **`0`** to disable that count (e.g. never allow 6).  
- The pick is also capped by how many distinct colors the two parents actually
  carry, and floored by the need to keep both parents' **main** colors.

Example: mostly 3–4 colors, rare 6:

```python
CHILD_COLOR_COUNT_WEIGHTS = {
    2: 5,
    3: 35,
    4: 40,
    5: 15,
    6: 5,
}
```

---

## Color inheritance (step by step)

1. **Merge** both parents' color pools. Shared colors get `match_bonus`.
2. **Always keep** each parent's main color (the one that painted
   `(252, 252, 252)` on that parent). Strong mains cannot vanish.
3. **Fill** remaining slots up to the count from `CHILD_COLOR_COUNT_WEIGHTS`:
   - Gen 1: weighted random among remaining colors  
   - Gen 2+ (`strict_color_from_generation`): take the strongest remaining
4. **Spillover** (`spillover_chance`): sometimes also take the *next* color by
   strength (e.g. the 5th after a quota of 4) — not a mutation, just randomness.
5. **Mutation** (`mutation_chance`): rarely add one **extra weak** allele from
   Gen 0 / Gen 1 lineage colors (not from the full `CATS_COLORS` palette).
   Mutations are heritable and always paint at least one accent gray so they
   show on the cat and in the legend.
6. **Main body bonus**: the strongest gene in the child gets `main_body_bonus`
   (it will paint `(252, 252, 252)`).

### Painting the coat

There are 11 gray shades in the templates. The strongest gene always paints
the main body gray `(252, 252, 252)`. Other grays are shared among weaker genes
by strength; every allele in the genome gets **at least one** gray so nothing
listed under the cat is invisible.

---

## Body-part inheritance

For each locus (`ear`, `eyes`, `body`, `tail`, `legs`):

- same part in both parents → child gets it for sure, strengths combine + `match_bonus`
- different parts → winner chosen weighted by strength, then `win_bonus`

So successful part shapes also accumulate power across generations.

---

## Extra randomness knobs

| Parameter | Default | Effect |
|-----------|---------|--------|
| `spillover_chance` | `0.25` | Chance to add the next-strongest leftover color after the normal quota |
| `mutation_chance` | `0.1` | Chance to add a weak Gen 0/1 throwback color |
| `mutation_strength` | `0.5` | Starting strength of a fresh mutation (stays weak vs mains) |
| `strict_color_from_generation` | `2` | From this gen onward, fill slots by strength rank instead of lottery |

---

## Seeds

Generation 0 can be saved/reloaded via `seeds.json` (`--load-seed`,
`--list-seeds`, `--no-save-seed`). Only founder colors and part refs are saved;
later generations are always re-rolled by inheritance.

```bash
python main.py --load-seed 3
python main.py --list-seeds
```

---

## Where to edit

| What | File |
|------|------|
| Color count probabilities | `CHILD_COLOR_COUNT_WEIGHTS` in `config.py` |
| Strength / mutation / spillover | `GENETICS_PARAMS` in `config.py` |
| Color palette for Gen 0 | `cats_colors.py` |
| Inheritance logic | `cat.py` |
