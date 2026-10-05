"""
Square-1 Scrambler

Generates random, guaranteed-solvable Square-1 scrambles in standard WCA
notation, e.g.:

    (3,-3)/(0,-2)/(-3,-3)/(-2,-5)/(-2,0)/(-4,1)/(-2,-3)/(3,-2)/(-1,-3)/(6,-3)/

Method:
    1. Model each layer as 12 30-degree slots: corners fill 2 slots, edges 1.
    2. Shape-preserving phase: pick random twists, keeping only the ones
       that allow a slice AND leave both layers cube shaped after it.
    3. Shape-scrambling phase: pick random twists, keeping any that allow
       a slice, so the puzzle's shape gets scrambled too.
    4. Format the twists with "/" slices between them, optionally marking
       the move whose slice first breaks the cube shape.

See docs/square1-model.md for a more in depth explanation.
"""

import random


#Layer model

def solved_layer(offset, start_with_corner):
    layer = []
    label = offset
    pattern = [2, 1] if start_with_corner else [1, 2]
    for p in range(8):
        layer.extend([label] * pattern[p % 2])
        label += 1
    return layer


def rotate(layer, k):
    k = k % 12
    return [layer[(i - k) % 12] for i in range(12)]


def can_slice(layer):
    return layer[11] != layer[0] and layer[5] != layer[6]


def do_slice(top, bottom):
    return top[:6] + bottom[:6], top[6:] + bottom[6:]


def piece_sizes(layer):
    n = len(layer)
    start = 0
    for i in range(n):
        if layer[i - 1] != layer[i]:
            start = i
            break
    sizes = []
    cur_id = layer[start]
    size = 0
    idx = start
    for _ in range(n):
        if layer[idx] == cur_id:
            size += 1
        else:
            sizes.append(size)
            cur_id = layer[idx]
            size = 1
        idx = (idx + 1) % n
    sizes.append(size)
    return sizes


def is_cube_shape(layer):
    sizes = piece_sizes(layer)
    return len(sizes) == 8 and all(sizes[i] != sizes[(i + 1) % 8] for i in range(8))



#Scramble generation

def generate_moves(total_moves=None, shape_moves=None, end_with_slice=True, max_attempts=20000):
    if total_moves is None:
        total_moves = random.randint(12, 14)
    if shape_moves is None:
        shape_moves = min(total_moves, random.randint(5, 7))

    top, bottom = solved_layer(0, True), solved_layer(100, False)
    moves = []
    phase1_target = min(shape_moves, total_moves)

    #Phase 1: scramble piece permutation, keep the cube shape
    attempts = 0
    while len(moves) < phase1_target and attempts < max_attempts:
        attempts += 1
        tr, br = random.randint(-5, 6), random.randint(-5, 6)
        if tr == 0 and br == 0:
            continue
        rt, rb = rotate(top, tr), rotate(bottom, br)
        if can_slice(rt) and can_slice(rb):
            nt, nb = do_slice(rt, rb)
            if is_cube_shape(nt) and is_cube_shape(nb):
                top, bottom = nt, nb
                moves.append((tr, br))
    phase1_len = len(moves)

    #Phase 2: scramble the shape too, any legal slice is allowed
    attempts = 0
    while len(moves) < total_moves and attempts < max_attempts:
        attempts += 1
        tr, br = random.randint(-5, 6), random.randint(-5, 6)
        if tr == 0 and br == 0:
            continue
        rt, rb = rotate(top, tr), rotate(bottom, br)
        if can_slice(rt) and can_slice(rb):
            top, bottom = do_slice(rt, rb)
            moves.append((tr, br))

    if len(moves) < total_moves:
        raise RuntimeError("Could not find enough legal moves; try again.")

    shape_break = phase1_len if phase1_len < len(moves) else None
    return moves, shape_break



#Display

def format_scramble(moves, end_with_slice=True, mark=None):
    parts = [f"({t},{b})" for t, b in moves]
    if mark is not None:
        parts[mark] = f"[{parts[mark]}]"
    return "/".join(parts) + ("/" if end_with_slice else "")


def describe_shape_break(moves, shape_break):
    if shape_break is None:
        return f"Stays cube shaped for all {len(moves)} moves."
    t, b = moves[shape_break]
    return (f"Shape scrambles starting at move {shape_break + 1}, "
            f"marked in [brackets]: ({t},{b})")
