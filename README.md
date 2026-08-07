# rubiks-toolkit

Rubik's cube analysis tools, unified into one installable package with a
shared command-line interface:

- **`order`** — given a move sequence, compute how many times it must be
  repeated to bring a cube back to a solved-looking state. Works for any
  cube size N (the standard 3x3 is just `--size 3`, the default).
- **`bld-memo`** — given a 3x3 scramble, generate a blindfold-solving
  memorization in Speffz letter pairs (Old Pochmann or M2, 
  `--method old_pochmann` by default).

Both tools work by simulating cube state as a permutation (not by
brute-force repeating a sequence until it "looks" solved), then using
group-theory facts (cycle decomposition and least-common-multiple) to
compute the answer directly. See the module docstrings in
`src/rubiks_toolkit/` for the full mathematical writeup of each.

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

Output includes the corner and edge letter pairs (standard Speffz scheme), plus a
step-by-step detail line showing which cube position each letter
corresponds to. 

Default buffers: corner = ULB (R), edge = UL (D) for Old Pochmann or
DF (U) for M2. 

**Note:** The memorization is traced from the original scramble orientation.
For example, if the cube is scrambled with white top green front, the memorization is also
done from white top green front, even if wide or slice moves are part of the scramble.

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

## Development

```bash
pip install -e ".[dev]"
pytest
```

Tests cover known reference algorithms (sexy move, sledgehammer, T-perm),
edge cases (even vs. odd cube slice-move rules, layer-range notation), and
the BLD tracer against several verified scrambles.

## License

MIT — see [LICENSE](LICENSE).
