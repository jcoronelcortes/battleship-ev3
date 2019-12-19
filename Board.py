import logging

from ev3dev2.motor import Motor
from ev3dev2.sound import Sound
from time import sleep
from datetime import datetime

# Set the logging level to INFO to see messages from AlexaGadget
logging.basicConfig(level=logging.INFO)

def restart_vertical(tank_pair, ts1):
    print("Restart vertical motors")
    tank_pair.on(left_speed=-40, right_speed=-40)

    while not ts1.is_pressed:  
        sleep(0.1)

    tank_pair.stop()
    tank_pair.position = 0
    sleep(0.5)


def restart_horizontal(lm, ts2):
    print("Restart horizontal motor")
    lm.on(speed=-40)
    while not ts2.is_pressed:  
        sleep(0.1)

    lm.stop()
    sleep(0.5)


def move_positon_player_attack(tank_pair, lm, row, column):
    
    # 1 - Move Tank_Pair to the row requested (the initial position is 0)
    rowPosition = 8 - row
    if(rowPosition > 0):
        rowPosition = rowPosition * 140 
        print("Row : {}".format(rowPosition))
        startMoveToPosition = datetime.now()
        tank_pair.run_to_rel_pos(position_sp=rowPosition, speed_sp=400, stop_action = Motor.STOP_ACTION_BRAKE)
        tank_pair.wait_while(Motor.STATE_RUNNING)
        tank_pair.stop()
        totalSeconds = total_time_to_move(startMoveToPosition)
        print("Total time for row : {}".format(totalSeconds))
        sleep(1)
        

    # 2 - Movbe lm to the column requested (the initial position is 8)
    columnPosition = 8 - column
    if(columnPosition > 0):
        columnPosition = columnPosition * 280
        print("Column : {}".format(columnPosition))
        startMoveToPosition = datetime.now()
        lm.run_to_rel_pos(position_sp=columnPosition, speed_sp=400, stop_action = Motor.STOP_ACTION_BRAKE)
        lm.wait_while(Motor.STATE_RUNNING)
        lm.stop()
        totalSeconds = total_time_to_move(startMoveToPosition)
        print("Total time for column : {}".format(totalSeconds))
        sleep(1)


def execute_player_attack(mm, attackResult, shipDestroyed):
    
    # 1 - Push the duplo brick on the board
    print("Empujando bloque")
    mm.run_to_rel_pos(position_sp=-350, speed_sp=400, stop_action = Motor.STOP_ACTION_BRAKE)
    mm.wait_while(Motor.STATE_RUNNING)
    
    mm.run_to_rel_pos(position_sp=350, speed_sp=400, stop_action = Motor.STOP_ACTION_BRAKE)
    mm.wait_while(Motor.STATE_RUNNING)
    
    mm.stop()

    # 2 - Logic to print the result of the attack
    if(attackResult == 1):
        print("You have impact a ship")
    
    elif(attackResult == 2):  
        print("Ship destroyed. You have sunk a  {}".format(shipDestroyed))

    elif(attackResult == 3):  
        print("You failed your shot")
    
    elif(attackResult == 4):  
        print("Congratulations. It is the final impact. You have won the game")
        

def transform_row_value_to_letter(row):

    if row == 0:

        return "A"

    elif row == 1:

        return "B"

    elif row == 2:

        return "C"

    elif row == 3:

        return "D"

    elif row == 4:

        return "E"

    elif row == 5:

        return "F"
    
    elif row == 6:

        return "G"
    
    elif row == 7:

        return "H"
    
    elif row == 8:

        return "I"
    
    return ""

def total_time_to_move(startMovePosition):
    
    totalTime = datetime.now() - startMovePosition 
    totalSeconds = int(totalTime.total_seconds() * 1000) 
    return totalSeconds  
