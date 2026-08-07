"""
NxN Rubik's Cube Move-Sequence Repeater Calculator

Given a cube size N and a sequence of moves (Singmaster-style notation,
extended to support big cubes), this script calculates how many times the
sequence must be repeated to return a solved NxNxN cube back to solved

Method:
  1. Build a permutation of all of the cube's surface stickers.
  2. Apply the given move sequence exactly once to a solved cube.
  3. Decompose the resulting permutation into disjoint cycles.
  4. Compute the Least Common Multiple (LCM) of the cycle lengths.
     That LCM is the number of repetitions needed. The "order" of a
     permutation (the smallest number of times you must apply it to get
     back to the identity) always equals the LCM of its disjoint cycle
     lengths because all cycles must finish at the same time for the cube
     to returned to a solve state.

See docs/nxn-model.md for a more in depth explanation.
"""

import math
import re
from itertools import product


#Rotation functions

def rot_x(pos, normal, sign):
    x, y, z = pos
    nx, ny, nz = normal
    if sign == 1:
        y2, z2 = -z, y
        ny2, nz2 = -nz, ny
    else:
        y2, z2 = z, -y
        ny2, nz2 = nz, -ny
    return (x, y2, z2), (nx, ny2, nz2)


def rot_y(pos, normal, sign):
    x, y, z = pos
    nx, ny, nz = normal
    if sign == 1:
        x2, z2 = z, -x
        nx2, nz2 = nz, -nx
    else:
        x2, z2 = -z, x
        nx2, nz2 = -nz, nx
    return (x2, y, z2), (nx2, ny, nz2)


def rot_z(pos, normal, sign):
    x, y, z = pos
    nx, ny, nz = normal
    if sign == 1:
        x2, y2 = y, -x
        nx2, ny2 = ny, -nx
    else:
        x2, y2 = -y, x
        nx2, ny2 = -ny, nx
    return (x2, y2, z), (nx2, ny2, nz)


ROTATE = {'x': rot_x, 'y': rot_y, 'z': rot_z}
AXIS_POSITION_INDEX = {'x': 0, 'y': 1, 'z': 2}



#Face/slice definitions

FACE_AXIS = {
    'R': ('x', 1, -1),
    'L': ('x', -1, 1),
    'U': ('y', 1, -1),
    'D': ('y', -1, 1),
    'F': ('z', 1, 1),
    'B': ('z', -1, -1),
}

SLICE_AXIS = {
    'M': ('x', 1),
    'E': ('y', 1),
    'S': ('z', 1),
}

TOKEN_PATTERN = re.compile(
    r"^(\d+(?:[-,]\d+)*)?(Rw|Lw|Uw|Dw|Fw|Bw|R|L|U|D|F|B|M|E|S)(2'|'2|2|')?$"
)


def _layer_numbers_from_spec(modifier, wide, n, token):
    if modifier is None:
        depth = 2 if wide else 1
        return list(range(1, depth + 1))

    if '-' in modifier:
        a_str, b_str = modifier.split('-')
        a, b = int(a_str), int(b_str)
        if a > b:
            a, b = b, a
        layer_numbers = list(range(a, b + 1))
    elif ',' in modifier:
        layer_numbers = [int(x) for x in modifier.split(',')]
    else:
        k = int(modifier)
        layer_numbers = list(range(1, k + 1)) if wide else [k]

    for k in layer_numbers:
        if k < 1 or k > n:
            raise ValueError(
                f"'{token}': layer {k} is out of range for a {n}x{n} cube "
                f"(must be between 1 and {n})."
            )
    return layer_numbers


def parse_token(token, n):
    m = TOKEN_PATTERN.match(token)
    if not m:
        raise ValueError(
            f"'{token}' is not a recognized move. Supported base moves: "
            f"R,L,U,D,F,B, M,E,S, Rw,Lw,Uw,Dw,Fw,Bw, each optionally "
            f"prefixed with a layer number ('3R'), a layer range ('4-5R'), "
            f"or a comma-separated layer list ('3,5R'), and suffixed with "
            f"' or 2."
        )
    layer_spec, face_code, modifier = m.group(1), m.group(2), m.group(3)
    wide = face_code.endswith('w')
    base_face = face_code[:-1] if wide else face_code

    if base_face in SLICE_AXIS:
        if wide:
            raise ValueError(f"'{token}': slice moves (M/E/S) cannot be wide.")
        if layer_spec:
            raise ValueError(f"'{token}': slice moves (M/E/S) don't take a layer number.")
        if n % 2 == 0:
            raise ValueError(
                f"'{token}': M/E/S require an odd-sized cube -- a {n}x{n} "
                f"cube has no single middle layer along that axis."
            )
        axis, base_sign = SLICE_AXIS[base_face]
        layer_coords = frozenset({0})
    else:
        axis, side, base_sign = FACE_AXIS[base_face]
        max_coord = n - 1
        layer_numbers = _layer_numbers_from_spec(layer_spec, wide, n, token)
        coords = [side * (max_coord - 2 * (k - 1)) for k in layer_numbers]
        layer_coords = frozenset(coords)

    if modifier is None:
        sign, repeat = base_sign, 1
    elif modifier == "'":
        sign, repeat = -base_sign, 1
    else:
        sign, repeat = base_sign, 2

    return axis, layer_coords, sign, repeat



#Cube model
class Cube:
    def __init__(self, n):
        if n < 2:
            raise ValueError("Cube size must be at least 2 (a 2x2x2 or larger).")
        self.n = n
        self.stickers = self._build_stickers()
        self.sticker_index = {s: i for i, s in enumerate(self.stickers)}
        self.num_stickers = len(self.stickers)
        self._quarter_turn_cache = {}

    def _center(self, i):
        return 2 * i - (self.n - 1)

    def _build_stickers(self):
        n = self.n
        stickers = []
        for ix, iy, iz in product(range(n), repeat=3):
            idxs = (ix, iy, iz)
            if not any(idx == 0 or idx == n - 1 for idx in idxs):
                continue
            pos = tuple(self._center(idx) for idx in idxs)
            for axis_i, idx in enumerate(idxs):
                if idx == 0 or idx == n - 1:
                    normal = [0, 0, 0]
                    normal[axis_i] = 1 if idx == n - 1 else -1
                    stickers.append((pos, tuple(normal)))
        return stickers

    def _quarter_turn_mapping(self, axis, layers, sign):
        key = (axis, layers, sign)
        cached = self._quarter_turn_cache.get(key)
        if cached is not None:
            return cached

        mapping = list(range(self.num_stickers))
        axis_pos = AXIS_POSITION_INDEX[axis]
        rotate_fn = ROTATE[axis]

        for i, (pos, normal) in enumerate(self.stickers):
            if pos[axis_pos] in layers:
                new_pos, new_normal = rotate_fn(pos, normal, sign)
                mapping[i] = self.sticker_index[(new_pos, new_normal)]

        self._quarter_turn_cache[key] = mapping
        return mapping

    def _apply_mapping(self, state, mapping):
        new_state = [None] * len(state)
        for i, value in enumerate(state):
            new_state[mapping[i]] = value
        return new_state

    def apply_sequence(self, move_tokens):
        state = list(range(self.num_stickers))
        for token in move_tokens:
            axis, layers, sign, repeat = parse_token(token, self.n)
            mapping = self._quarter_turn_mapping(axis, layers, sign)
            for _ in range(repeat):
                state = self._apply_mapping(state, mapping)
        return state



#Cycle decomposition and LCM

def decompose_into_cycles(state):
    n = len(state)
    visited = [False] * n
    cycles = []
    for start in range(n):
        if visited[start]:
            continue
        cycle = []
        j = start
        while not visited[j]:
            visited[j] = True
            cycle.append(j)
            j = state[j]
        cycles.append(cycle)
    return cycles


def _divisors(n):
    return [d for d in range(1, n + 1) if n % d == 0]


def _visual_period(cycle, colors):
    length = len(cycle)
    color_seq = [colors[i] for i in cycle]
    for m in _divisors(length):
        if all(color_seq[t] == color_seq[(t + m) % length] for t in range(length)):
            return m
    return length


def sequence_order(cube, move_string):
    tokens = move_string.split()
    if not tokens:
        raise ValueError("No moves given.")
    final_state = cube.apply_sequence(tokens)
    cycles = decompose_into_cycles(final_state)
    colors = [s[1] for s in cube.stickers]
    visual_periods = [_visual_period(c, colors) for c in cycles]
    order = 1
    for period in visual_periods:
        if period > 1:
            order = math.lcm(order, period)
    return order, cycles, visual_periods


#Display

_NUMBER_WORDS = {
    1: "One", 2: "Two", 3: "Three", 4: "Four", 5: "Five",
    6: "Six", 7: "Seven", 8: "Eight", 9: "Nine", 10: "Ten",
    11: "Eleven", 12: "Twelve",
}


def _count_word(n):
    return _NUMBER_WORDS.get(n, str(n))


def describe_cycle_structure(cycles, visual_periods):
    nontrivial = sorted(p for p in visual_periods if p > 1)
    trivial_count = sum(1 for p in visual_periods if p == 1)
    collapsed = sum(
        1 for c, p in zip(cycles, visual_periods) if p > 1 and p < len(c)
    )

    if not nontrivial:
        return (
            "Detected cycles: none -- every sticker returns to a "
            "color-matching spot immediately. This sequence already "
            "looks solved after just 1 repetition.\nLCM() = 1"
        )

    counts = {}
    for period in nontrivial:
        counts[period] = counts.get(period, 0) + 1

    parts = []
    for period in sorted(counts):
        n = counts[period]
        word = _count_word(n)
        cycle_word = "cycle" if n == 1 else "cycles"
        parts.append(f"{word} {period}-{cycle_word}")

    lcm_input = []
    for period in sorted(counts):
        lcm_input.extend([period] * counts[period])

    order = 1
    for period in lcm_input:
        order = math.lcm(order, period)

    lines = [
        f"Detected cycles: {', '.join(parts)} "
        f"(plus {trivial_count} unaffected/color-matching stickers).",
        f"LCM({', '.join(str(x) for x in lcm_input)}) = {order}",
    ]
    if collapsed:
        lines.append(
            f"Note: {collapsed} cycle(s) reach a color-matching state "
            f"sooner than their raw permutation length would suggest -- "
            f"this happens when a cycle only shuffles same-colored "
            f"stickers on a single face (common with big-cube centers), "
            f"which is invisible on a physical cube."
        )
    return "\n".join(lines)


def solve_and_report(cube, move_string):
    print(f"\n[{cube.n}x{cube.n}x{cube.n}] Move sequence: {move_string!r}")
    order, cycles, visual_periods = sequence_order(cube, move_string)
    print(describe_cycle_structure(cycles, visual_periods))
    print(f"The sequence must be repeated {order} times to return "
          f"the cube to a solved state.")
    return order
