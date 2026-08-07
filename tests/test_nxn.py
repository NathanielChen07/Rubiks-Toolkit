import pytest

from rubiks_toolkit.nxn import Cube, sequence_order


@pytest.mark.parametrize("seq,expected", [
    ("R", 4),
    ("R2", 2),
    ("R U R' U'", 6),                                     # "Sexy Move"
    ("R' F R F'", 6),                                     # "Sledgehammer"
    ("R U R' U' R' F R2 U' R' U' R U R' F'", 2),          # T-perm (self-inverse)
    ("M2 U M2 U2 M2 U M2", 2),                            # pure slice moves
])
def test_3x3_known_algorithms(seq, expected):
    cube = Cube(3)
    order, _, _ = sequence_order(cube, seq)
    assert order == expected


@pytest.mark.parametrize("n", [2, 3, 4, 5, 6, 7])
def test_single_quarter_turn_always_order_4(n):
    cube = Cube(n)
    order, _, _ = sequence_order(cube, "R")
    assert order == 4


def test_even_cube_rejects_slice_moves():
    cube = Cube(4)
    with pytest.raises(ValueError):
        sequence_order(cube, "M")


def test_odd_cube_accepts_slice_moves():
    cube = Cube(5)
    sequence_order(cube, "M")  # should not raise


def test_full_wide_turn_equals_whole_cube_rotation():
    cube = Cube(3)
    order, _, _ = sequence_order(cube, "3Rw")
    assert order == 4


def test_4x4_visual_period_vs_raw_permutation():
    # "L' U" on a 4x4 looks solved after 63 reps even though the raw
    # sticker permutation doesn't hit the literal identity until 252.
    cube = Cube(4)
    order, _, _ = sequence_order(cube, "L' U")
    assert order == 63


def test_layer_range_and_single_layer_notation_agree():
    cube = Cube(4)
    order_single, _, _ = sequence_order(cube, "3R")
    order_range, _, _ = sequence_order(cube, "3-3R")
    assert order_single == order_range


def test_layer_range_and_comma_list_parse():
    cube = Cube(7)
    order, _, _ = sequence_order(cube, "4-5R U 4-5R' U'")
    assert order > 1
    sequence_order(cube, "3,5R")  # should not raise


def test_out_of_range_layer_rejected():
    cube = Cube(4)
    with pytest.raises(ValueError):
        sequence_order(cube, "9R")
