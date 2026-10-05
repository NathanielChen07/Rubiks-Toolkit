import re

from rubiks_toolkit.cli import main


def test_order_command(capsys):
    ret = main(["order", "R U R' U'"])
    assert ret == 0
    out = capsys.readouterr().out
    assert "repeated 6 time" in out


def test_order_command_with_size(capsys):
    ret = main(["order", "R", "--size", "5"])
    assert ret == 0
    out = capsys.readouterr().out
    assert "repeated 4 time" in out


def test_order_command_invalid_move(capsys):
    ret = main(["order", "Q"])
    assert ret == 1
    err = capsys.readouterr().err
    assert "Error" in err


def test_bld_memo_command(capsys):
    ret = main(["bld-memo", "R U R' U'", "--method", "m2"])
    assert ret == 0
    out = capsys.readouterr().out
    assert "Scramble" in out


def test_sq1_scramble_command(capsys):
    ret = main(["sq1-scramble"])
    assert ret == 0
    out = capsys.readouterr().out.splitlines()
    assert len(out) == 2
    assert "cube shaped" in out[1] or "Shape scrambles" in out[1]


def test_sq1_scramble_command_plain(capsys):
    ret = main(["sq1-scramble", "--plain"])
    assert ret == 0
    out = capsys.readouterr().out.strip()
    assert re.fullmatch(r"(\(-?\d,-?\d\)/){11,13}\(-?\d,-?\d\)/?", out)
