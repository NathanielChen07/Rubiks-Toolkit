import random

import pytest

from rubiks_toolkit.square1 import (
    can_slice, do_slice, format_scramble, generate_moves, is_cube_shape,
    piece_sizes, rotate, solved_layer,
)


TOP = solved_layer(0, True)
BOTTOM = solved_layer(100, False)


def _replay(moves, end_with_slice=True):
    top, bottom = TOP, BOTTOM
    for i, (t, b) in enumerate(moves):
        top, bottom = rotate(top, t), rotate(bottom, b)
        if end_with_slice or i < len(moves) - 1:
            assert can_slice(top) and can_slice(bottom)
            top, bottom = do_slice(top, bottom)
    return top, bottom


def test_solved_layers_are_cube_shaped():
    assert piece_sizes(TOP) == [2, 1] * 4
    assert piece_sizes(BOTTOM) == [1, 2] * 4
    assert is_cube_shape(TOP) and is_cube_shape(BOTTOM)


@pytest.mark.parametrize("twist,legal", [
    ((0, 0), True),
    ((1, -1), True),     # documented TNoodle reference case
    ((-1, 1), False),    # ...and its illegal mirror
    ((3, 3), True),
    ((1, 1), False),
])
def test_slice_legality_from_solved(twist, legal):
    t, b = twist
    assert (can_slice(rotate(TOP, t)) and can_slice(rotate(BOTTOM, b))) == legal


def test_slice_is_self_inverse():
    top, bottom = do_slice(*do_slice(TOP, BOTTOM))
    assert (top, bottom) == (TOP, BOTTOM)


def test_slice_can_break_cube_shape():
    top, bottom = do_slice(rotate(TOP, -3), rotate(BOTTOM, 0))
    assert not (is_cube_shape(top) and is_cube_shape(bottom))


@pytest.mark.parametrize("seed", range(25))
@pytest.mark.parametrize("end_with_slice", [True, False])
def test_generated_scrambles_are_legal(seed, end_with_slice):
    random.seed(seed)
    moves, shape_break = generate_moves(end_with_slice=end_with_slice)
    assert 12 <= len(moves) <= 14
    assert all((t, b) != (0, 0) and -5 <= t <= 6 and -5 <= b <= 6 for t, b in moves)
    _replay(moves, end_with_slice)
    assert 5 <= shape_break <= 7
    assert all(is_cube_shape(layer) for layer in _replay(moves[:shape_break]))


def test_shape_preserving_phase_keeps_cube_shape():
    random.seed(0)
    moves, shape_break = generate_moves(total_moves=8, shape_moves=8)
    assert shape_break is None
    assert all(is_cube_shape(layer) for layer in _replay(moves))


def test_format_scramble():
    moves = [(1, 0), (-3, 2), (6, -5)]
    assert format_scramble(moves) == "(1,0)/(-3,2)/(6,-5)/"
    assert format_scramble(moves, end_with_slice=False) == "(1,0)/(-3,2)/(6,-5)"
    assert format_scramble(moves, mark=1) == "(1,0)/[(-3,2)]/(6,-5)/"
