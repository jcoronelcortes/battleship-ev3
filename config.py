"""Robot settings. Measured on the 2019 robot; adjust with calibrate.py after rebuilding it.

Python 3.5 compatible (ev3dev-stretch): no f-strings.
"""

# Ports (see README for the cable map)
PORT_VERTICAL_RIGHT = "outA"   # large motor, moves the carriage to a row (paired with D)
PORT_PUSHER = "outB"           # medium motor, pushes the Duplo brick
PORT_HORIZONTAL = "outC"       # large motor, moves the pusher to a column
PORT_VERTICAL_LEFT = "outD"    # large motor, moves the carriage to a row (paired with A)
PORT_TOUCH_HORIZONTAL = "in1"  # touch sensor at the horizontal home position
PORT_TOUCH_VERTICAL = "in4"    # touch sensor at the vertical home position

# Board: 9 x 9, rows A..I, columns 1..9. Home position is I9 (row 8, column 8).
BOARD_SIZE = 9
HOME_ROW = 8
HOME_COLUMN = 8

# Motor degrees per cell and speeds (tacho counts per second)
ROW_DEGREES = 140
COLUMN_DEGREES = 280
PUSH_DEGREES = 350
MOVE_SPEED_SP = 400
HOME_SPEED_PERCENT = 40

# Safety: stop a motor if its touch sensor is not pressed in time (a stuck motor can break the build)
HOME_TIMEOUT_MS = 20000
MOVE_TIMEOUT_MS = 20000
