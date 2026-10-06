# Square-1 Scrambler

The Square-1 is the only shapeshifting puzzle officially recognized by the WCA. Since it shapeshifts, there are physical restrictions on what moves can be applied at a given state, resulting in complications when applying moves. 

The Square-1 consists of 3 layers, with the top and bottom consisting of 4 corners and 4 edges. 

Unlike the other two tools, this one doesn't analyze a sequence. It generates
one. Each scramble is a series of random moves that are checked to be physically
legal, so any scramble it prints can be applied to a solved Square-1, and is
therefore solvable. Output is in standard WCA notation:

    (3,-3)/(0,-2)/(-3,-3)/(-2,-5)/(-2,0)/(-4,1)/(-2,-3)/(3,-2)/(-1,-3)/(6,-3)/

# Puzzle model:

- Each layer (top and bottom) is 12 "wedge" slots of 30 degrees each.
  A corner piece fills 2 consecutive slots (60 degrees), an edge piece
  fills 1 slot (30 degrees). 4 corners + 4 edges = 12 slots per layer,
  matching the real puzzle. A layer is stored as a list of 12 piece ids,
  so a corner shows up as the same id twice in a row.
- The middle layer isn't tracked. It only ever flips between two states
  and doesn't affect which moves are legal.
- Solved state: the top layer's slot 0 sits at the start of a corner, but
  the bottom layer's slot 0 sits at the start of an edge. On a real,
  solved Square-1 the two layers' piece boundaries are offset from each
  other by one piece, not stacked corner-on-corner. Getting this offset
  right is what makes the legal twists before a slice match a real cube
  instead of an idealized/symmetric one.

# Moves:

- Twist `(x, y)`: rotate the top layer by x spots and the bottom layer by
  y spots (each spot = 30 degrees, range -5..6). `(0,0)` is never
  generated since it turns nothing. Twists are always physically possible:
  the top and bottom layers spin independently no matter what shape the
  puzzle is in. `-` denotes a counterclockwise rotation.
- Slice `/`: swaps the top layer's right half (slots 6-11) with the bottom
  layer's left half (slots 0-5). This is only physically possible when
  neither layer has a corner straddling the cut line. That means slots
  11|0 and 5|6 must both be piece boundaries on both layers, since a
  corner can't be cut in half. This is the real "you need a flat side
  to cut" restriction.
- Every twist is followed by a slice, except that a scramble may stop
  right after its last twist without cutting. The CLI picks one or the
  other at random for each scramble.

# Shape:

A layer is "cube shaped" only when its 8 pieces still alternate corner, edge,
corner, edge... around the layer. Twisting never changes a layer's shape. Only
slicing can, and only when the half that gets swapped in is arranged
differently than the half it replaces (e.g. leaving two corners next to each
other). This is what turns the puzzle into a "shield", "kite", etc.

Scrambles are generated in two phases to reflect this:

 1. Shape-preserving phase (the first 5-7 moves, chosen at random): only
    slices that leave both layers cube shaped are allowed. The pieces get
    mixed up, but the puzzle still looks like a cube.
 2. Shape-scrambling phase (the remaining moves): the first slice in this
    phase is required to break the cube shape, and after that any legal
    slice is allowed. The puzzle ends in the jumbled, non-cubic shape a
    real scrambled Square-1 has.

By default the output marks the move where phase 2 starts, the move whose slice
first breaks the cube shape, in `[brackets]`. `--plain` prints the scramble
without the marker.

# Generation:

For each move, a random twist is picked and applied to a copy of the current
state. If both layers can be sliced afterwards (and, in phase 1, the slice keeps
the cube shape), the twist and slice are committed. Otherwise the twist is
thrown away and a new one is drawn. Since a move is never committed unless its
slice is legal, every scramble can be performed on a real puzzle.

Note: this is a random-move scrambler. The WCA's and csTimer's official scrambler (TNoodle)
is random-state, meaning it picks a uniformly random puzzle state and solves
it to produce the scramble. Random-move scrambles are fine for practice, but
aren't guaranteed to be as evenly distributed over all states.

# Validation:

The piece layout, twist direction, and slice legality were checked against
TNoodle's source (`SquareOnePuzzle.java`): its 24-slot array uses the same
solved layout, and its slash swaps slots 6-11 with 12-17, which is exactly the
top's right half with the bottom's left half. One documented check: from a
solved cube, `(1,-1)/` is legal but `(-1,1)/` is not. This model reproduces
that, and the test suite covers it.
