# rubiks-toolkit

Rubik's Cube and Square-1 analysis tools:

- **`order`** — given a move sequence, compute how many times it must be
  repeated to bring a cube back to a solved-looking state. Works for any
  NxN sized cube (the standard 3x3 is just `--size 3`, the default).
- **`bld-memo`** — given a 3x3 scramble, generate a blindfold-solving
  memorization in Speffz letter pairs (Old Pochmann or M2, 
  `--method old_pochmann` by default).
- **`sq1-scramble`** — generates a random, legal Square-1
  scramble in standard WCA notation.

The `order` and `bld-memo` tools work by simulating a cube state as a
permutation (not by brute force repeating a sequence until it "looks" solved),
then using group theory facts (cycle decomposition and least common multiple)
to compute the answer directly.

The `sq1-scramble` tool models each layer as 12 30-degree slots and only
commits a move when its slice is physically possible. See the files in docs
for the full description of each.

## Install

```bash
git clone https://github.com/<you>/rubiks-toolkit.git
cd rubiks-toolkit
pip install -e ".[dev]"
```

The `-e` (editable) install plus `[dev]` pulls in `pytest` for running the
test suite. Drop `[dev]` for a plain install.

## Usage

### Cycle order (`order`)

```bash
# Standard 3x3 (default size)
rubiks-toolkit order "R U R' U'"
# = repeated 6 time(s)

# NxN cube — any size 2 and up
rubiks-toolkit order "Rw U2 Rw' U2 Rw U2 Rw' 3Rw2" --size 4

# Layer-specific moves on bigger cubes: single inner layer, ranges, lists
rubiks-toolkit order "3R" --size 5          # just layer 3
rubiks-toolkit order "3-5R U 3-5R' U'" --size 7   # layers 3 through 5
rubiks-toolkit order "3,5R" --size 7        # layers 3 and 5 separately
```

Supported notation: `R L U D F B`, slice moves `M E S` (odd cubes only),
wide moves `Rw Lw Uw Dw Fw Bw` (optionally with an explicit depth like
`3Rw`), explicit inner layers/ranges/lists (`3R`, `4-5R`, `3,5R`), and the
usual `'` / `2` modifiers.

### Blindfold memorization (`bld-memo`)

```bash
rubiks-toolkit bld-memo "D2 F' R2 B L2 F' D2 B2 D2 F2 L F' U B2 U' F2 L' B2 F'"
rubiks-toolkit bld-memo "R U R' U' M2 F2" --method m2
```

Output includes the edge and corner letter pairs (standard Speffz scheme), plus a
step-by-step detail line showing which cube position each letter
corresponds to. 

Default buffers: corner = ULB (R), edge = UL (D) for Old Pochmann or
DF (U) for M2. 

**Note:** The memorization is traced from the original scramble orientation.
For example, if the cube is scrambled with white top green front, the memorization is also
done from white top green front, even if wide or slice moves are part of the scramble.

### Square-1 scramble (`sq1-scramble`)

```bash
rubiks-toolkit sq1-scramble
# (3,2)/(-2,4)/(-3,6)/(2,2)/(-5,-5)/(-1,2)/(4,-2)/[(-3,-1)]/(-3,6)/(-3,2)/(0,6)/(3,-4)
# Shape scrambles starting at move 8, marked in [brackets]: (-3,-1)

rubiks-toolkit sq1-scramble --plain   ]
# (3,2)/(-2,4)/(-3,6)/(2,2)/(-5,-5)/(-1,2)/(4,-2)/(-3,-1)/(-3,6)/(-3,2)/(0,6)/(3,-4)
# raw notation only, no indicator for when shape scramble starts
```

Each scramble is 12-14 moves. The first 5-7 keep the puzzle cube shaped while
the pieces get mixed up. The move in `[brackets]` is the one whose slice
first breaks the cube shape, and every move after it may scramble the shape
further. 

### As a library

```python
from rubiks_toolkit.nxn import Cube, sequence_order

cube = Cube(4)
order, cycles, visual_periods = sequence_order(cube, "Rw U2 Rw'")
```

```python
from rubiks_toolkit.bld_memo import Cube, generate_memo

cube = Cube()
cube.apply_scramble("R U R' U' M2 F2")
memo = generate_memo(cube, "old_pochmann")
print(memo["corner_pairs"], memo["edge_pairs"])
```

```python
from rubiks_toolkit.square1 import generate_moves, format_scramble

moves, shape_break = generate_moves()
print(format_scramble(moves))
```

## Development

```bash
pip install -e ".[dev]"
pytest
```

Tests cover known reference algorithms (sexy move, sledgehammer, T-perm),
edge cases (even vs. odd cube slice-move rules, layer-range notation),
the BLD tracer against several verified scrambles, and Square-1 slice
legality (including the TNoodle `(1,-1)/` vs. `(-1,1)/` reference case)
plus the shape of generated scrambles.

## License

MIT — see [LICENSE](LICENSE).
