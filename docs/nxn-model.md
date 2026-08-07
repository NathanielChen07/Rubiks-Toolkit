# NxN Rubik's Cube Move-Sequence Repeater Calculator

This originally only worked for standard 3x3 cubes. But the underlying model
is a sticker-permutation model that works for any size cube, so code has been
generalized to support any sized cube. Setting N=3 gives the same behavior as
the original 3x3-only calculator. This is why there is no separate 3x3-specific
program in this repository.

# Cube model:

- The cube is represented purely as a permutation of its surface
  stickers. A sticker is a (cubie position, outward-facing normal vector) pair.
  Ex: the sticker on the front face of the top-front-right cubie.
  The sticker's position is the entire state. There are 6*N^2 stickers on an
  NxNxN cube. For cubes 4x4 and larger, center piece stickers are tracked as well.

- Coordinates: cubies sit on an integer grid (0..N-1 per axis),
  converted to a symmetric "centered" coordinate: c = 2*i - (N-1). 
  This makes the middle of the cube sit at 0 regardless of N, and 
  means a single set of rotation formulas works identically for every cube size, odd or even. 
  Ex: The coordinate system for a 3x3 would be -2, 0, 2. A 4x4 would be -3, -1, 1, 3.

- Sticker generation: every cubie touching the surface (with at
  least one coordinate at the minimum or maximum) contributes one
  sticker per face it's exposed on: 1 sticker for a center piece,
  2 for an edge piece, 3 for a corner piece. Interior cubies (fully
  hidden) contribute nothing, since they're never visible and don't 
  affect the state of the cube.

- Rotations: a 90-degree turn about one axis only changes the other
  two coordinates. This is applied to both a sticker's position AND its
  normal vector, since a sticker's face identity turns along with
  it. These formulas are size-independent.

- Moves as layer selection: a move doesn't hard-code "which stickers
  move". It specifies an axis and a set of coordinate values
  along that axis, and every sticker sitting at one of those
  coordinates gets rotated. Therefore, all types of moves function on 
  the same mechanism.

- Applying a sequence: Each quarter turn is precomputed once
  as a `mapping` (position i to its next position) and cached,
  then applied to the current state. Once every move in the sequence has
  been applied, the final state after one repetition of the sequence
  has been reached.

# Cycle Decomposition: 

  Once the the full sequence has been established and applied, the resulting
  permutation is decomposed into disjoint cycles. It starts at a sticker in the solve state,
  finds where it ends up after the sequence. The sticker that should be in this target spot
  is then tracked after the sequence, and so on. Once it returns to the original sticker, the 
  cycle is complete. Then a completely unvisited sticker is chosen and the process repeats until
  all the stickers have been visited. The order of the sequence of moves (how many repetitions
  return the cube to solved state) is the LCM of all cycle lengths. This
  is a direct application of a basic group-theory fact: the order of
  any permutation equals the LCM of its disjoint cycle lengths. No
  brute-force repeated simulation is needed.

# Visual Period:

  Sometimes, the raw cycle length isn't the right answer. On a 4x4+, 
  several distinct center stickers on the same face share
  a color and are visually interchangeable. A cycle can permute
  purely among same-colored stickers and "look" solved well before
  it returns to the physical solved state. An example is the sequence L' U.
  This popular 2-move sequence takes 63 repetitions to return a 3x3 cube to the
  solved state. And since this only affects the outer layers of a 4x4, it should
  also be 63 for a 4x4. However, a 4x4 has center pieces that rotate, but don't 
  leave a solved state in this sequence. And since 63 == 3 mod 4, after 63 repetitions,
  the center pieces have been "rotated" 3 times from the original position. Therefore,
  the cube isn't literally "solved", and it would technically take 63 * 4 = 252 cycles.
  But in reality, 63 repetitions is all that's needed because the cube is still visually
  solved afterwards. `_visual_period` checks, for each cycle, the smallest divisor 
  of its length at which every sticker's color (not position) matches its color m
  steps earlier. That's the number of repetitions needed for that cycle to
  look solved, which can be smaller than its raw length.
  The reported order is the LCM of these visual periods, not of the
  raw cycle lengths.    

# Move notation supported

  - For a cube of size N, layers counted 1..N starting from the left
  - Plain face turn: R, L, U, D, F, B (turns just layer 1)
  - Wide turn (default 2 layers): Rw, Lw, Uw, Dw, Fw, Bw
  - Wide turn, explicit depth: (k)Rw (turns outer k layers), e.g. 3Rw
  - Single inner slice, explicit depth: (k)R (turns ONLY layer k), e.g. 2R
  - Layer range:  (a)-(b)R (turns layers a through b together as one
    move). Ex: 3-5R turns the 3rd, 4th, and 5th layers
  - Layer list: (a),(b),...R (turns exactly those layers). 
    Ex: 3,5R turns the 3rd and 5th layer
  - Middle slices (odd N only): M, E, S (M follows L, E follows D, S follows F)
  - Modifiers: ' (counter-clockwise) and 2 (180 degrees), e.g. Rw', 3Fw2, 4-5R'