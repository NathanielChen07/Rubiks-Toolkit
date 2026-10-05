"""Command-line interface for rubiks_toolkit.

Subcommands
-----------
order         Compute how many times a move sequence must repeat to return
              an NxN cube to a solved-looking state (defaults to N=3).
bld-memo      Convert a scramble into a Speffz blindfold memorization. (defaults to OP)
sq1-scramble  Generate a random Square-1 scramble in WCA notation.
"""

import argparse
import random
import sys

from . import bld_memo as bld
from . import nxn
from . import square1 as sq1


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


def _cmd_sq1_scramble(args):
    end_with_slice = random.choice([True, False])
    moves, shape_break = sq1.generate_moves(end_with_slice=end_with_slice)
    if args.plain:
        print(sq1.format_scramble(moves, end_with_slice))
    else:
        print(sq1.format_scramble(moves, end_with_slice, mark=shape_break))
        print(sq1.describe_shape_break(moves, shape_break))
    return 0


def build_parser():
    parser = argparse.ArgumentParser(
        prog="rubiks-toolkit",
        description="Cycle-order calculators, BLD memo generation, and Square-1 scrambles.",
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

    p_sq1 = sub.add_parser(
        "sq1-scramble",
        help="Generate a random Square-1 scramble in WCA notation.",
    )
    p_sq1.add_argument(
        "--plain", action="store_true",
        help="Print only the raw scramble, without marking where the shape scrambles.",
    )
    p_sq1.set_defaults(func=_cmd_sq1_scramble)

    return parser


def main(argv=None):
    parser = build_parser()
    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
