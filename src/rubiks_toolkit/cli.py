"""Command-line interface for rubiks_toolkit.

Subcommands
-----------
order       Compute how many times a move sequence must repeat to return
            an NxN cube to a solved-looking state (defaults to N=3).
bld-memo    Convert a scramble into a Speffz blindfold memorization. (defaults to OP)
"""

import argparse
import sys

from . import bld_memo as bld
from . import nxn


def _cmd_order(args):
    cube = nxn.Cube(args.size)
    try:
        order, cycles, visual_periods = nxn.sequence_order(cube, args.sequence)
    except ValueError as err:
        print(f"Error: {err}", file=sys.stderr)
        return 1
    print(f"[{args.size}x{args.size}x{args.size}] Move sequence: {args.sequence!r}")
    print(nxn.describe_cycle_structure(cycles, visual_periods))
    print(f"==> The sequence must be repeated {order} time(s) to return "
          f"the cube to a solved-looking state.")
    return 0


def _cmd_bld_memo(args):
    cube = bld.Cube()
    try:
        cube.apply_scramble(args.scramble)
    except ValueError as err:
        print(f"Error: {err}", file=sys.stderr)
        return 1
    memo = bld.generate_memo(cube, args.method)
    bld.print_memo(args.scramble, args.method, memo)
    return 0


def build_parser():
    parser = argparse.ArgumentParser(
        prog="rubiks-toolkit",
        description="Cycle-order calculators and BLD memo generation for Rubik's cubes.",
    )
    sub = parser.add_subparsers(dest="command", required=True)

    p_order = sub.add_parser(
        "order",
        help="Compute the repeat-order of a move sequence on an NxN cube.",
    )
    p_order.add_argument("sequence", help="Space-separated move sequence, e.g. \"R U R' U'\"")
    p_order.add_argument(
        "-n", "--size", type=int, default=3,
        help="Cube size N (default: 3, i.e. a standard 3x3x3).",
    )
    p_order.set_defaults(func=_cmd_order)

    p_bld = sub.add_parser(
        "bld-memo",
        help="Convert a 3x3 scramble into a Speffz blindfold memorization.",
    )
    p_bld.add_argument("scramble", help="Space-separated scramble, e.g. \"R U R' U' M2 F2\"")
    p_bld.add_argument(
        "-m", "--method", choices=["old_pochmann", "m2"], default="old_pochmann",
        help="Edge-tracing method (default: old_pochmann).",
    )
    p_bld.set_defaults(func=_cmd_bld_memo)

    return parser


def main(argv=None):
    parser = build_parser()
    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
