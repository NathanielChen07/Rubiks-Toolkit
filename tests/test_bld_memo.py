import pytest

from rubiks_toolkit.bld_memo import Cube, generate_memo


SCRAMBLES = [
    "D2 F' R2 B L2 F' D2 B2 D2 F2 L F' U B2 U' F2 L' B2 F'",
    "Uw2 R2 F' U' F Rw2 D2 L2 Bw' U2 M2 R' F2 Lw' E2 U' Rw2 B S' D' L2",
    "F2 Rw' B2 Uw L' D2 S Fw2 R' Uw2 M' E' B' Lw2 F' Dw R2 S2 U'",
    "F2 D2 F2 R2 D' B2 F2 L2 U L2 U' R2 F' R D' F2 L F R' U B' Rw2 Uw'",
]


@pytest.mark.parametrize("scramble", SCRAMBLES)
@pytest.mark.parametrize("method", ["old_pochmann", "m2"])
def test_memo_generation_does_not_raise_and_pairs_up(scramble, method):
    cube = Cube()
    cube.apply_scramble(scramble)
    memo = generate_memo(cube, method)
    # Every pair should be two characters (or one letter + '_' padding).
    for pair in memo["corner_pairs"] + memo["edge_pairs"]:
        assert len(pair) == 2
    # The buffer's own piece should never be spoken.
    assert "R" not in memo["corner_letters"]  # ULB corner buffer letter


def test_solved_cube_has_no_letters():
    cube = Cube()  # no scramble applied
    memo = generate_memo(cube, "old_pochmann")
    assert memo["corner_letters"] == []
    assert memo["edge_letters"] == []


def test_invalid_method_raises():
    cube = Cube()
    cube.apply_scramble("R U R' U'")
    with pytest.raises(ValueError):
        generate_memo(cube, "not_a_method")


def test_slice_move_cannot_be_wide():
    cube = Cube()
    with pytest.raises(ValueError):
        cube.apply_scramble("Mw")
