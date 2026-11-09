"""Configuración del robot. Medida en el robot de 2019; ajústala con calibrate.py después de armarlo.

Compatible con Python 3.5 (ev3dev-stretch): sin f-strings.
"""

# Puertos (ver el mapa de cables en el README)
PORT_VERTICAL_RIGHT = "outA"   # motor grande, mueve el carro a una fila (junto con D)
PORT_PUSHER = "outB"           # motor mediano, empuja el bloque Duplo
PORT_HORIZONTAL = "outC"       # motor grande, mueve el empujador a una columna
PORT_VERTICAL_LEFT = "outD"    # motor grande, mueve el carro a una fila (junto con A)
PORT_TOUCH_HORIZONTAL = "in1"  # sensor táctil de la posición inicial horizontal
PORT_TOUCH_VERTICAL = "in4"    # sensor táctil de la posición inicial vertical

# Tablero: 9 x 9, filas A..I, columnas 1..9. La posición inicial es I9 (fila 8, columna 8).
BOARD_SIZE = 9
HOME_ROW = 8
HOME_COLUMN = 8

# Grados del motor por casilla y velocidades (grados por segundo)
ROW_DEGREES = 140
COLUMN_DEGREES = 280
PUSH_DEGREES = 350
# Después de empujar, el carro se queda en la casilla mostrando el resultado (luz roja o verde)
# mientras Alexa lo anuncia; recién entonces vuelve: primero a la derecha y después baja.
RESULT_WAIT_SECONDS = 2
MOVE_SPEED_SP = 400
HOME_SPEED_PERCENT = 40

# Seguridad: detener el motor si su sensor táctil no se presiona a tiempo (un motor trabado puede romper el armado)
HOME_TIMEOUT_MS = 20000
MOVE_TIMEOUT_MS = 20000
