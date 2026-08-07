"""
Blindfold Cube Memorization Generator

Given a scramble (standard face turns, wide/rotation turns, and the
M/E/S slice turns), this builds a piece-based model of a 3x3 cube
(each cubie stores its permutation and orientation, not raw
sticker colors as the primary state), applies the scramble, and
produces a standard blindfold memorization in Speffz letter
pairs.

Method:
    1. Build a piece-based cube model that tracks position, orientation, and face-map
       Also includes the letter associated with each sticker on the piece.
    2. Apply the scramble to the cube model
    3. Reorient the cube to its original scrambling frame
    4. Run the tracing algorithm to produce the memorization

See docs/blind-model.md for a more in depth explanation.
"""


#CUBE MODEL
CORNER_POS = ['UFR', 'UFL', 'ULB', 'UBR', 'DFR', 'DFL', 'DBL', 'DRB']
EDGE_POS = ['UF', 'UR', 'UB', 'UL', 'DF', 'DR', 'DB', 'DL',
            'FR', 'FL', 'BL', 'BR']

CI = {name: i for i, name in enumerate(CORNER_POS)}
EI = {name: i for i, name in enumerate(EDGE_POS)}

CORNER_MOVES = {
    'U': (['UBR', 'UFR', 'UFL', 'ULB'], {}),
    'D': (['DFR', 'DRB', 'DBL', 'DFL'], {}),
    'L': (['UFL', 'DFL', 'DBL', 'ULB'], {'DFL': 1, 'DBL': 2, 'ULB': 1, 'UFL': 2}),
    'R': (['UFR', 'UBR', 'DRB', 'DFR'], {'UBR': 2, 'DRB': 1, 'DFR': 2, 'UFR': 1}),
    'F': (['UFR', 'DFR', 'DFL', 'UFL'], {'DFR': 1, 'DFL': 2, 'UFL': 1, 'UFR': 2}),
    'B': (['ULB', 'DBL', 'DRB', 'UBR'], {'DBL': 1, 'DRB': 2, 'UBR': 1, 'ULB': 2}),
}
EDGE_MOVES = {
    'U': (['UF', 'UL', 'UB', 'UR'], {}),
    'D': (['DF', 'DR', 'DB', 'DL'], {}),
    'L': (['UL', 'FL', 'DL', 'BL'], {}),
    'R': (['UR', 'BR', 'DR', 'FR'], {}),
    'F': (['UF', 'FR', 'DF', 'FL'], {'UF': 1, 'FR': 1, 'DF': 1, 'FL': 1}),
    'B': (['UB', 'BL', 'DB', 'BR'], {'UB': 1, 'BL': 1, 'DB': 1, 'BR': 1}),
    'M': (['UF', 'DF', 'DB', 'UB'], {}),
    'E': (['FR', 'BR', 'BL', 'FL'], {}),
    'S': (['UR', 'DR', 'DL', 'UL'], {'UR': 1, 'DR': 1, 'DL': 1, 'UL': 1}),
}

FACE_CYCLE = {
    'U': {'U': 'U', 'D': 'D', 'R': 'F', 'F': 'L', 'L': 'B', 'B': 'R'},
    'D': {'U': 'U', 'D': 'D', 'F': 'R', 'R': 'B', 'B': 'L', 'L': 'F'},
    'L': {'L': 'L', 'R': 'R', 'U': 'F', 'F': 'D', 'D': 'B', 'B': 'U'},
    'R': {'L': 'L', 'R': 'R', 'U': 'B', 'B': 'D', 'D': 'F', 'F': 'U'},
    'F': {'F': 'F', 'B': 'B', 'U': 'R', 'R': 'D', 'D': 'L', 'L': 'U'},
    'B': {'F': 'F', 'B': 'B', 'U': 'L', 'L': 'D', 'D': 'R', 'R': 'U'},
    'M': {'U': 'F', 'F': 'D', 'D': 'B', 'B': 'U', 'L': 'L', 'R': 'R'},
    'E': {'F': 'R', 'R': 'B', 'B': 'L', 'L': 'F', 'U': 'U', 'D': 'D'},
    'S': {'U': 'R', 'R': 'D', 'D': 'L', 'L': 'U', 'F': 'F', 'B': 'B'},
}


class Cube:
    def __init__(self):
        self.corners = [(i, 0) for i in range(8)]
        self.edges = [(i, 0) for i in range(12)]
        self.c_fmap = [{f: f for f in CORNER_POS[i]} for i in range(8)]
        self.e_fmap = [{f: f for f in EDGE_POS[i]} for i in range(12)]
        self.center_fmap = {f: f for f in 'UDLRFB'}

    @staticmethod
    def _apply_cycle(face, state, fmap, index_map, cycle_names, deltas, mod):
        idxs = [index_map[n] for n in cycle_names]
        old_state = [state[i] for i in idxs]
        old_fmap = [fmap[state[i][0]] for i in idxs]
        n = len(idxs)
        for k in range(n):
            dest = idxs[k]
            piece, orient = old_state[k - 1]
            d = deltas.get(cycle_names[k], 0)
            state[dest] = (piece, (orient + d) % mod)
            fmap[piece] = {hf: FACE_CYCLE[face][cf] for hf, cf in old_fmap[k - 1].items()}

    def apply_base_move(self, face, times=1):
        times %= 4
        for _ in range(times):
            if face in CORNER_MOVES:
                cyc, delt = CORNER_MOVES[face]
                self._apply_cycle(face, self.corners, self.c_fmap, CI, cyc, delt, 3)
            cyc_e, delt_e = EDGE_MOVES[face]
            self._apply_cycle(face, self.edges, self.e_fmap, EI, cyc_e, delt_e, 2)
            if face in 'MES':
                self.center_fmap = {c: FACE_CYCLE[face][s] for c, s in self.center_fmap.items()}

    def apply_wide_move(self, face, times=1):
        times %= 4
        if times == 0:
            return
        pairing = {
            'U': ('E', (4 - times) % 4), 'D': ('E', times),
            'R': ('M', (4 - times) % 4), 'L': ('M', times),
            'F': ('S', times), 'B': ('S', (4 - times) % 4),
        }
        self.apply_base_move(face, times)
        slice_face, slice_times = pairing[face]
        self.apply_base_move(slice_face, slice_times)

    def apply_scramble(self, scramble):
        for tok in scramble.split():
            face, wide, count = parse_token(tok)
            if wide:
                self.apply_wide_move(face, count)
            else:
                self.apply_base_move(face, count)

    def reoriented(self):
        inv_center = {slot: color for color, slot in self.center_fmap.items()}

        def build(positions, index_map, state, fmap, n):
            new_fmap = [
                {hf: inv_center[cf] for hf, cf in fmap[piece].items()}
                for piece in range(n)
            ]
            name_by_faceset = {frozenset(name): name for name in positions}
            new_state = [None] * n
            for new_name in positions:
                old_faces = frozenset(self.center_fmap[ch] for ch in new_name)
                old_name = name_by_faceset[old_faces]
                new_state[index_map[new_name]] = state[index_map[old_name]]
            return new_state, new_fmap

        new_corners, new_c_fmap = build(CORNER_POS, CI, self.corners, self.c_fmap, 8)
        new_edges, new_e_fmap = build(EDGE_POS, EI, self.edges, self.e_fmap, 12)
        return new_corners, new_c_fmap, new_edges, new_e_fmap


def parse_token(token):
    s = token
    if not s:
        raise ValueError("Empty move token")
    count = 1
    if s.endswith("2"):
        count = 2
        s = s[:-1]
    elif s.endswith("'") or s.endswith("\u2019"):
        count = 3
        s = s[:-1]
    wide = False
    if s.endswith('w') or s.endswith('W'):
        wide = True
        s = s[:-1]
    if len(s) != 1:
        raise ValueError(f"Cannot parse move: '{token}'")
    ch = s
    if ch.islower():
        if ch.upper() in 'UDLRFB':
            wide = True
            face = ch.upper()
        elif ch in 'mes':
            face = ch.upper()
        else:
            raise ValueError(f"Unknown move: '{token}'")
    else:
        if ch in 'UDLRFBMES':
            face = ch
        else:
            raise ValueError(f"Unknown move: '{token}'")
    if face in 'MES' and wide:
        raise ValueError(f"Slice move cannot be wide: '{token}'")
    return face, wide, count



#Speffz Letter scheme

FACE_ORDER = ['U', 'L', 'F', 'R', 'B', 'D']
LETTERS = 'ABCDEFGHIJKLMNOPQRSTUVWX'

CORNER_CW = {
    'U': ['ULB', 'UBR', 'UFR', 'UFL'],
    'L': ['ULB', 'UFL', 'DFL', 'DBL'],
    'F': ['UFL', 'UFR', 'DFR', 'DFL'],
    'R': ['UFR', 'UBR', 'DRB', 'DFR'],
    'B': ['UBR', 'ULB', 'DBL', 'DRB'],
    'D': ['DFL', 'DFR', 'DRB', 'DBL'],
}
EDGE_CW = {
    'U': ['UB', 'UR', 'UF', 'UL'],
    'L': ['UL', 'FL', 'DL', 'BL'],
    'F': ['UF', 'FR', 'DF', 'FL'],
    'R': ['UR', 'BR', 'DR', 'FR'],
    'B': ['UB', 'BL', 'DB', 'BR'],
    'D': ['DF', 'DR', 'DB', 'DL'],
}


def _build_letters(cw_table):
    pos_face_to_letter = {}
    letter_to_pos_face = {}
    i = 0
    for face in FACE_ORDER:
        for pos in cw_table[face]:
            L = LETTERS[i]
            i += 1
            pos_face_to_letter[(pos, face)] = L
            letter_to_pos_face[L] = (pos, face)
    return pos_face_to_letter, letter_to_pos_face


CORNER_PFL, CORNER_LFP = _build_letters(CORNER_CW)
EDGE_PFL, EDGE_LFP = _build_letters(EDGE_CW)

CORNER_BUFFER_POS, CORNER_BUFFER_LETTER = 'ULB', 'R'
EDGE_BUFFER = {
    'old_pochmann': ('UL', 'D'),
    'm2': ('DF', 'U'),
}


#Memorization tracing

def _own_letters(letter, lfp, pfl):
    pos, _face = lfp[letter]
    return set(pfl[(pos, f)] for f in pos)


def _decal_at(pos, face, state, fmap, positions, index_map):
    piece, _orient = state[index_map[pos]]
    home_pos = positions[piece]
    fm = fmap[piece]
    for home_face, cur_face in fm.items():
        if cur_face == face:
            return (home_pos, home_face)
    raise RuntimeError("inconsistent face map")


def _build_location_permutation(state, fmap, positions, index_map, pfl, lfp):
    mapping = {}
    for L, (pos, face) in lfp.items():
        mapping[L] = pfl[_decal_at(pos, face, state, fmap, positions, index_map)]
    return mapping


def _find_cycles(m):
    seen, cycles = set(), []
    for x in m:
        if x in seen or m[x] == x:
            continue
        cyc = [x]
        seen.add(x)
        y = m[x]
        while y != x:
            cyc.append(y)
            seen.add(y)
            y = m[y]
        cycles.append(cyc)
    return cycles


def trace_cycles(state, fmap, positions, index_map, pfl, lfp, buffer_pos, buffer_start_letter):
    mapping = _build_location_permutation(state, fmap, positions, index_map, pfl, lfp)
    buffer_letters = _own_letters(buffer_start_letter, lfp, pfl)
    fixed = set(L for L in mapping if mapping[L] == L)
    visited = set(fixed)
    letters, steps = [], []

    def mark(letter):
        visited.update(_own_letters(letter, lfp, pfl))

    def emit(letter):
        letters.append(letter)
        steps.append((letter, lfp[letter][0]))
        mark(letter)

    current = buffer_start_letter
    while True:
        next = mapping[current]
        if next in buffer_letters:
            visited.update(buffer_letters)
            break
        emit(next)
        current = next

    all_cycles = _find_cycles(mapping)
    twist_only = set()
    for cyc in all_cycles:
        if len(set(lfp[L][0] for L in cyc)) == 1:
            twist_only.update(cyc)

    while True:
        remaining = sorted(L for L in mapping if L not in visited)
        if not remaining:
            break
        non_twist = [L for L in remaining if L not in twist_only]
        bstart = non_twist[0] if non_twist else remaining[0]
        own = _own_letters(bstart, lfp, pfl)
        emit(bstart)
        current = bstart
        while True:
            next = mapping[current]
            emit(next)
            if next in own:
                break
            current = next

    return letters, steps


def format_pairs(letters):
    pairs = []
    i = 0
    while i < len(letters):
        if i + 1 < len(letters):
            pairs.append(letters[i] + letters[i + 1])
            i += 2
        else:
            pairs.append(letters[i] + '_')
            i += 1
    return pairs


def generate_memo(cube, method):
    method = method.lower()
    if method not in ('old_pochmann', 'm2'):
        raise ValueError("method must be 'old_pochmann' or 'm2'")

    edge_buffer_pos, edge_buffer_letter = EDGE_BUFFER[method]

    corners, c_fmap, edges, e_fmap = cube.reoriented()

    corner_letters, corner_steps = trace_cycles(
        corners, c_fmap, CORNER_POS, CI, CORNER_PFL, CORNER_LFP,
        CORNER_BUFFER_POS, CORNER_BUFFER_LETTER)
    edge_letters, edge_steps = trace_cycles(
        edges, e_fmap, EDGE_POS, EI, EDGE_PFL, EDGE_LFP,
        edge_buffer_pos, edge_buffer_letter)

    return {
        'method': method,
        'corner_buffer': f"{CORNER_BUFFER_POS} (enter via '{CORNER_BUFFER_LETTER}')",
        'edge_buffer': f"{edge_buffer_pos} (enter via '{edge_buffer_letter}')",
        'corner_letters': corner_letters,
        'edge_letters': edge_letters,
        'corner_steps': corner_steps,
        'edge_steps': edge_steps,
        'corner_pairs': format_pairs(corner_letters),
        'edge_pairs': format_pairs(edge_letters),
    }


#Display

def print_memo(scramble, method, memo):
    print("=" * 66)
    print(f"Scramble : {scramble}")
    print(f"Method   : {'Old Pochmann' if method == 'old_pochmann' else 'M2'}")
    print(f"Buffers  : corner={memo['corner_buffer']}  edge={memo['edge_buffer']}")
    print("-" * 66)
    print(f"EDGES  ({len(memo['edge_letters'])} letters):")
    print("  Pairs :", ' '.join(memo['edge_pairs']) if memo['edge_pairs'] else '(solved)')
    if memo['edge_steps']:
        print("  Detail:", ', '.join(f"{L}[{p}]" for L, p in memo['edge_steps']))
    print(f"\nCORNERS  ({len(memo['corner_letters'])} letters):")
    print("  Pairs :", ' '.join(memo['corner_pairs']) if memo['corner_pairs'] else '(solved)')
    if memo['corner_steps']:
        print("  Detail:", ', '.join(f"{L}[{p}]" for L, p in memo['corner_steps']))
    print("=" * 66)


def run(scramble, method):
    cube = Cube()
    cube.apply_scramble(scramble)
    memo = generate_memo(cube, method)
    print_memo(scramble, method, memo)
    return memo
