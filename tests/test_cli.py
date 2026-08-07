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
