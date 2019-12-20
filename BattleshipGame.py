import logging
import json

from agt import AlexaGadget

from time import sleep
from random import seed
from random import randint
from datetime import datetime

from ev3dev2.motor import Motor, MoveTank, LargeMotor, MediumMotor, OUTPUT_A, OUTPUT_B, OUTPUT_C, OUTPUT_D
from ev3dev2.sensor import INPUT_1, INPUT_4
from ev3dev2.sensor.lego import TouchSensor
from ev3dev2.sound import Sound
from ev3dev2.led import Leds

from Board import restart_horizontal, restart_vertical, move_positon_player_attack
from Board import execute_player_attack, transform_row_value_to_letter

# Set the logging level to INFO to see messages from AlexaGadget
logging.basicConfig(level=logging.INFO)

class BatallaNaval(AlexaGadget):

    def __init__(self):
        """
        Performs Alexa Gadget initialization routines and ev3dev resource allocation.
        """
        super().__init__()

        # Gadget state
        self.patrol_mode = False

        # Ev3dev initialization
        self.leds = Leds()
        self.sound = Sound()
        self.tsVertical = TouchSensor(INPUT_4) 
        self.tsHorizontal = TouchSensor(INPUT_1) 
        self.mm = MediumMotor(OUTPUT_B)
        self.tank_pair = MoveTank(OUTPUT_A, OUTPUT_D)
        self.tank_pair.reset()
        self.lm = LargeMotor(OUTPUT_C)


        print("--------------------------------------------")
        print("  BATTLESHIP ")
        print("--------------------------------------------")
        self.sound.speak("BATTLESHIP")


    def on_connected(self, device_addr):
        """
        Gadget connected to the paired Echo device.
        :param device_addr: the address of the device we connected to
        """
        self.leds.set_color("LEFT", "GREEN")
        self.leds.set_color("RIGHT", "GREEN")
        print("{} connected to Echo device".format(self.friendly_name))


    def on_disconnected(self, device_addr):
        """
        Gadget disconnected from the paired Echo device.
        :param device_addr: the address of the device we disconnected from
        """
        self.leds.set_color("LEFT", "BLACK")
        self.leds.set_color("RIGHT", "BLACK")
        print("{} disconnected from Echo device".format(self.friendly_name))


    def on_custom_mindstorms_gadget_control(self, directive):
        """
        Handles the Custom.Mindstorms.Gadget control directive.
        :param directive: the custom directive with the matching namespace and name
        """
        try:
            print("***************************************************************************")
            payload = json.loads(directive.payload.decode("utf-8"))
            print("Directive - Payload information : {}".format(payload))
            print("***************************************************************************")
            command_type = payload["command"]
            if command_type == "start_game":

                print("Starting a new game")
                restart_horizontal(self.lm, self.tsHorizontal)
                restart_vertical(self.tank_pair, self.tsVertical)
                    
            elif command_type == "player_attack":

                print("Executing player attack")
                # Logic to pushj the brick on the position (X, Y) (0....8, 0....8)
                row = int(payload["row"])
                column = int(payload["column"])

                rowValue = transform_row_value_to_letter(row)
                print("Row : {}".format(rowValue))
                columnValue = column + 1
                print("Column : {}".format(columnValue))

                move_positon_player_attack(self.tank_pair, self.lm, row, column)
                
                attackResult = int(payload["attackResult"])
                shipDestroyed = payload["shipDestroyed"]

                execute_player_attack(self.mm, attackResult, shipDestroyed)
                
                if attackResult > 0 and attackResult < 6:

                    restart_horizontal(self.lm, self.tsHorizontal)
                    restart_vertical(self.tank_pair, self.tsVertical)

            elif command_type == "alexa_attack":

                print("Executing Alexa attack")
                row = payload["row"]
                column = payload["column"]

                print("Row : {}".format(row))
                print("Column : {}".format(column))

            elif command_type == "test_mode":

                logZones = payload["logZones"]
                print("Alexa Board information\n {}".format(logZones))

            elif command_type == "finish_game":   

                print("Alexa o el Jugador gana el juego. Bajando barra vertical")
                #Logica para subir al maximo y luego bajar     

        except KeyError:

            sound = Sound()
            print("Command sent into the Directive is not supported : {}".format(directive))
            sound.speak("ERROR")
            sound.speak("ERROR")
            sound.speak("ERROR")
        

if __name__ == '__main__':
    # Startup sequence
    gadget = BatallaNaval()
    gadget.sound.play_song((('C4', 'e'), ('D4', 'e'), ('E5', 'q')))
    gadget.leds.set_color("LEFT", "GREEN")
    gadget.leds.set_color("RIGHT", "GREEN")

    # Gadget main entry point
    gadget.main()

    # Shutdown sequence
    gadget.sound.play_song((('E5', 'e'), ('C4', 'e')))
    gadget.leds.set_color("LEFT", "BLACK")
    gadget.leds.set_color("RIGHT", "BLACK")