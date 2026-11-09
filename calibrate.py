#!/usr/bin/env python3
"""Calibración después de armar el robot: vuelve a la posición inicial y visita las casillas que elijas.

    python3 calibrate.py              # visita A1, E5 e I9 (esquinas y centro)
    python3 calibrate.py C5 A9        # visita las casillas que indiques
    python3 calibrate.py --push C5    # además empuja un bloque en cada casilla

Si el empujador queda antes o después de la casilla, ajusta ROW_DEGREES / COLUMN_DEGREES en config.py.

Compatible con Python 3.5 (ev3dev-stretch): sin f-strings.
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
    parser = argparse.ArgumentParser(description="Calibrar el robot de Batalla Naval")
    parser.add_argument("cells", nargs="*", default=["A1", "E5", "I9"])
    parser.add_argument("--push", action="store_true", help="empujar un bloque en cada casilla")
    parser.add_argument("--simulate", action="store_true")
    args = parser.parse_args()
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(name)s: %(message)s")

    hw = hardware.simulated() if args.simulate else hardware.real()
    motion.go_home(hw)
    for cell in args.cells:
        row, column = parse_cell(cell)
        print("Moviendo a {} ...".format(cell.upper()))
        motion.move_to(hw, row, column)
        if args.push:
            motion.push_brick(hw)
        try:
            input("El empujador quedo sobre {}? Presiona Enter para continuar ".format(cell.upper()))
        except EOFError:
            pass
        motion.go_home(hw)
    print("Listo. Ajusta config.py si alguna casilla quedo desplazada.")


if __name__ == "__main__":
    main()
