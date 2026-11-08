#!/usr/bin/env python3
"""Calibration after rebuilding the robot: homes both axes, then visits cells you choose.

    python3 calibrate.py              # visits A1, E5 and I9 (corners and center)
    python3 calibrate.py C5 A9        # visits the cells you name
    python3 calibrate.py --push C5    # also pushes a brick on each cell

If the pusher stops before or after the cell, change ROW_DEGREES / COLUMN_DEGREES in config.py.

Python 3.5 compatible (ev3dev-stretch): no f-strings.
"""
import argparse
import logging

import hardware
import motion


def parse_cell(text):
    text = text.strip().upper()
    row = motion.ROW_LETTERS.index(text[0])
    column = int(text[1:]) - 1
    if not 0 <= column <= 8:
        raise ValueError(text)
    return row, column


def main():
    parser = argparse.ArgumentParser(description="Calibrate the Battleship robot")
    parser.add_argument("cells", nargs="*", default=["A1", "E5", "I9"])
    parser.add_argument("--push", action="store_true", help="push a brick on each cell")
    parser.add_argument("--simulate", action="store_true")
    args = parser.parse_args()
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(name)s: %(message)s")

    hw = hardware.simulated() if args.simulate else hardware.real()
    motion.go_home(hw)
    for cell in args.cells:
        row, column = parse_cell(cell)
        print("Moving to {} ...".format(cell.upper()))
        motion.move_to(hw, row, column)
        if args.push:
            motion.push_brick(hw)
        try:
            input("Is the pusher over {}? Press Enter to continue ".format(cell.upper()))
        except EOFError:
            pass
        motion.go_home(hw)
    print("Done. Adjust config.py if a cell was off.")


if __name__ == "__main__":
    main()
