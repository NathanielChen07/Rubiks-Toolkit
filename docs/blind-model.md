# Blindfold Cube Memorization Generator

This uses a different, piece-based cube model than ``rubiks_toolkit.nxn``
(which is sticker-based and generalizes to any N). This is because the two
are solving different problems: sticker permutation order vs. piece-level
blindfold tracing with orientation and face-relabeling. 

# Cube model:

- 8 corners, 12 edges. Each is stored as (piece_id, orientation).
  `piece_id` is the index of the cubie's home (solved) slot, so a
  slot is "solved" exactly when piece_id == slot_index.
- Corner orientation in {0, 1, 2}, edge orientation in {0, 1}.
- Each piece also carries a small `face_map`: for
  each of its stickers, which face it's currently on. This is
  still piece-level data (indexed by the piece, not a sticker grid).
  It is simply a fuller description of "how is this piece
  twisted", derived from the exact same rotation-derived move
  tables as the permutation/orientation, and it is what lets the
  memo generator pick the correct letter of a piece's 2-3 Speffz
  letters at each step.
- Moves are 4-cycles of slots with an orientation delta for
  whichever piece lands in each slot, derived from first-principles
  3-D rotation matrices, not copied from a library. They satisfy the
  standard invariants (corner-orientation sum == 0 mod 3, edge-flip
  count is even, same move 4 times == identity, move * inverse(move) 
  == identity) under all base, slice, and wide moves.
- Wide moves are the standard combination of a face turn plus the
  matching slice turn (Rw = R + M', Uw = U + E', Fw = F + S, ...).
- Centers: U/D/L/R/F/B are fixed physical/spatial slot labels, not
  colors. Base face turns never move a center out of its own face,
  but M/E/S turns, and therefore the hidden slice half of every
  wide move (Rw = R + M', Uw = U + E', ...), physically relocate
  the centers themselves. `Cube.center_fmap` tracks, for each
  original center color, which physical slot it currently occupies.
  Before tracing, `Cube.reoriented()` uses that map to re-express
  the whole piece state in the fixed original color frame. (Ex: white
  top, green front, or whatever orientation the cube was scrambled in.)
  This matches what a real blindfold solver would do: they pick the cube
  back up and rotate it to their home orientation before memorizing.
      
# Speffz Letter Scheme:

Speffz assigns 24 distinct letters (A-X) to corners and a separate
24 letters (A-X) to edges. Letters are assigned face by face, in the
fixed order U, L, F, R, B, D. Each face contributes its 4 corner
letters (or 4 edge letters) consecutively, going clockwise starting
at a specific corner (per the standard Speffz rule):
   U starts at ULB, L at ULB, F at UFL, R at UFR, B at UBR, D at DFL 
   "ULB" standards for Upper, Left, Back, etc.
So every corner has 3 letters (one per side) and every edge
has 2. Which one of those letters gets used at a given moment in the
trace is not arbitrary. It depends on the piece's current
orientation, which is exactly what `face_map` captures.

# Buffers:

- Corners (both methods): the ULB corner, and more specifically, 'R'
  (ULB's three letters are A, E, R -- the Speffz default buffer).
- Edges, Old Pochmann: the UL edge, 'D'.
- Edges, M2: the DF edge, 'U'.

# Tracing Algorithm:

Think of every corner/edge slot's 3 (or 2) faces as separate,
individually-labeled locations. A move permutes which sticker sits
at which location (this is derived from the same validated
permutation + a per-move face relabeling). Tracing then runs on this
24-location permutation instead of the plain 8/12 piece one:

 1. Start at the buffer, entered via its designated letter. Look up
    what's currently at that location. That sticker's letter is the
    first target. Keep following (letter -> location -> sticker's
    letter -> ...) until the sticker found belongs to the buffer
    piece itself. This last buffer is not included in the memo.
 2. If unsolved letters remain, start a "cycle break", meaning jump to 
    the lowest still-unvisited letter (commonly A), add it to the memo, 
    then follow the same process until the sticker found belongs to the 
    same piece the break started on. Add that last letter to the memo.
 3. Whenever any one letter of a piece is used (as a target or as a
    break-start), the whole piece counts as handled and its other
    letter(s) are automatically resolved and never separately named
    (this is why the letter counts land near, but not always exactly at, 
    "one per unsolved piece").
 4. Pure "twist/flip only" pieces (already in the right slot but
    mis-oriented) show up naturally as a short self-contained loop
    over that single piece's own letters. These are processed last
    among cycle breaks, since real solvers typically solve and memorize
    these at the very end.
 5. Form letter pairs for the memo. If the total letter count is odd, the
    last letter is left unpaired and is printed with a trailing underscore.
