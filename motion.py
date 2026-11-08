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
    _home(hw.horizontal, hw.touch_horizontal, "horizontal touch sensor (port 1)",
          speed=-config.HOME_SPEED_PERCENT)


def go_home_vertical(hw):
    """Moves the carriage down until the vertical touch sensor is pressed (row I)."""
    _home(hw.vertical, hw.touch_vertical, "vertical touch sensor (port 4)",
          left_speed=-config.HOME_SPEED_PERCENT, right_speed=-config.HOME_SPEED_PERCENT)


def _home(motor, sensor, sensor_name, **speed):
    """Runs the motor until the sensor is pressed; stops it anyway after HOME_TIMEOUT_MS."""
    log.info("Homing until %s is pressed (pressed now: %s)", sensor_name, sensor.is_pressed)
    motor.on(**speed)
    pressed = sensor.wait_for_pressed(timeout_ms=config.HOME_TIMEOUT_MS)
    motor.stop()
    if not pressed:
        raise HomingError(sensor_name + " not pressed")
    time.sleep(0.5)


def go_home(hw):
    go_home_horizontal(hw)
    go_home_vertical(hw)


def move_to(hw, row, column):
    """From home (I9) moves to [row, column], both 0..8."""
    if not (0 <= row < config.BOARD_SIZE and 0 <= column < config.BOARD_SIZE):
        raise ValueError("cell out of the board: row {} column {}".format(row, column))

    rows_to_move = config.HOME_ROW - row
    if rows_to_move > 0:
        log.info("Row %s", row_letter(row))
        _turn(hw.vertical, rows_to_move * config.ROW_DEGREES, "Row")
        time.sleep(1)

    columns_to_move = config.HOME_COLUMN - column
    if columns_to_move > 0:
        log.info("Column %d", column + 1)
        _turn(hw.horizontal, columns_to_move * config.COLUMN_DEGREES, "Column")
        time.sleep(1)


def push_brick(hw):
    """Pushes the Duplo brick onto the cell and pulls the pusher back."""
    log.info("Pushing brick")
    _turn(hw.pusher, -config.PUSH_DEGREES, "Push", stop=False)
    _turn(hw.pusher, config.PUSH_DEGREES, "Pull back")


def _turn(motor, degrees, name, stop=True):
    """Turns a motor (or the vertical motor pair) by some degrees and waits until it finishes."""
    started = time.time()
    motor.run_to_rel_pos(position_sp=degrees, speed_sp=config.MOVE_SPEED_SP)
    motor.wait_while("running", timeout=config.MOVE_TIMEOUT_MS)
    if stop:
        motor.stop()
    log.info("%s: %d degrees in %d ms", name, degrees, int((time.time() - started) * 1000))
