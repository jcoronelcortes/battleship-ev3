"""Robot movements on the board. Based on the 2019 Board.py, with timeouts so a motor never runs forever.

Python 3.5 compatible (ev3dev-stretch): no f-strings.
"""
import logging
import time

import config

log = logging.getLogger("motion")

ROW_LETTERS = "ABCDEFGHI"


class HomingError(Exception):
    """A touch sensor was not pressed in time: the motor was stopped."""


def row_letter(row):
    return ROW_LETTERS[row] if 0 <= row < len(ROW_LETTERS) else "?"


def go_home_horizontal(hw):
    """Moves the pusher right until the horizontal touch sensor is pressed (column 9)."""
    log.info("Homing horizontal axis (pressed=%s)", hw.touch_horizontal.is_pressed)
    hw.horizontal.on(speed=-config.HOME_SPEED_PERCENT)
    pressed = hw.touch_horizontal.wait_for_pressed(timeout_ms=config.HOME_TIMEOUT_MS)
    hw.horizontal.stop()
    if not pressed:
        raise HomingError("horizontal touch sensor (port 1) not pressed")
    time.sleep(0.5)


def go_home_vertical(hw):
    """Moves the carriage down until the vertical touch sensor is pressed (row I)."""
    log.info("Homing vertical axis (pressed=%s)", hw.touch_vertical.is_pressed)
    hw.vertical.on(left_speed=-config.HOME_SPEED_PERCENT, right_speed=-config.HOME_SPEED_PERCENT)
    pressed = hw.touch_vertical.wait_for_pressed(timeout_ms=config.HOME_TIMEOUT_MS)
    hw.vertical.stop()
    if not pressed:
        raise HomingError("vertical touch sensor (port 4) not pressed")
    time.sleep(0.5)


def go_home(hw):
    go_home_horizontal(hw)
    go_home_vertical(hw)


def move_to(hw, row, column):
    """From home (I9) moves to [row, column], both 0..8."""
    rows_to_move = config.HOME_ROW - row
    if rows_to_move > 0:
        degrees = rows_to_move * config.ROW_DEGREES
        log.info("Row %s: %d degrees", row_letter(row), degrees)
        started = time.time()
        hw.vertical.run_to_rel_pos(position_sp=degrees, speed_sp=config.MOVE_SPEED_SP)
        hw.vertical.wait_while("running", timeout=config.MOVE_TIMEOUT_MS)
        hw.vertical.stop()
        log.info("Row move took %d ms", int((time.time() - started) * 1000))
        time.sleep(1)

    columns_to_move = config.HOME_COLUMN - column
    if columns_to_move > 0:
        degrees = columns_to_move * config.COLUMN_DEGREES
        log.info("Column %d: %d degrees", column + 1, degrees)
        started = time.time()
        hw.horizontal.run_to_rel_pos(position_sp=degrees, speed_sp=config.MOVE_SPEED_SP)
        hw.horizontal.wait_while("running", timeout=config.MOVE_TIMEOUT_MS)
        hw.horizontal.stop()
        log.info("Column move took %d ms", int((time.time() - started) * 1000))
        time.sleep(1)


def push_brick(hw):
    """Pushes the Duplo brick onto the cell and pulls the pusher back."""
    log.info("Pushing brick")
    hw.pusher.run_to_rel_pos(position_sp=-config.PUSH_DEGREES, speed_sp=config.MOVE_SPEED_SP)
    hw.pusher.wait_while("running", timeout=config.MOVE_TIMEOUT_MS)
    hw.pusher.run_to_rel_pos(position_sp=config.PUSH_DEGREES, speed_sp=config.MOVE_SPEED_SP)
    hw.pusher.wait_while("running", timeout=config.MOVE_TIMEOUT_MS)
    hw.pusher.stop()
