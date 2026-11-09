"""Executes the game commands sent by the Alexa skill (Lambda -> AWS IoT Core -> this robot).

Command JSON (same fields the Java skill sends):
  {"command": "player_attack", "row": "2", "column": "4", "attackResult": 3, "shipDestroyed": "NO", ...}

Compatible con Python 3.5 (ev3dev-stretch): sin f-strings.
"""
import json
import logging

import motion

log = logging.getLogger("robot")

# attackResult values (SendCommandDirective.java)
IMPACT = 1
SHIP_DESTROYED = 2
FAIL = 3
PLAYER_WON = 4
DUPLICATE_ATTACK = 5


class BattleshipRobot(object):

    def __init__(self, hw):
        self.hw = hw
        self.handlers = {
            "start_game": self.start_game,
            "game_mode_configured": self.game_mode_configured,
            "player_attack": self.player_attack,
            "fail_attack": self.alexa_missed,
            "alexa_impact": self.alexa_hit,
            "alexa_ship_destroyed": self.alexa_sank_ship,
            "finish_game": self.finish_game,
            "test_mode": self.test_mode,
        }

    def handle_message(self, raw):
        """Entry point for one MQTT message. Never raises: errors are shown on the LEDs."""
        try:
            payload = json.loads(raw.decode("utf-8") if isinstance(raw, bytes) else raw)
        except ValueError:
            log.error("Invalid JSON: %r", raw)
            return
        command = payload.get("command")
        handler = self.handlers.get(command)
        if handler is None:
            log.warning("Unknown command: %s", command)
            return
        log.info("Command %s: %s", command, payload)
        try:
            handler(payload)
        except motion.HomingError as e:
            log.error("Homing failed: %s", e)
            self.leds("RED")
            self.hw.sound.speak("Check sensor")
        except Exception:
            log.exception("Command %s failed", command)
            self.leds("RED")

    # ---------- commands ----------

    def start_game(self, payload):
        self.leds("AMBER")
        motion.go_home(self.hw)
        self.leds("GREEN")

    def game_mode_configured(self, payload):
        self.hw.sound.beep()

    def player_attack(self, payload):
        result = int(payload.get("attackResult", 0))
        if result == DUPLICATE_ATTACK:
            # The zone was already attacked: Alexa says so, the robot does not move
            log.info("Duplicate attack, robot stays home")
            return
        row = int(payload["row"])
        column = int(payload["column"])
        log.info("Player attacks %s%d (result %d)", motion.row_letter(row), column + 1, result)

        self.leds("AMBER")
        motion.move_to(self.hw, row, column)
        motion.push_brick(self.hw)
        if result in (IMPACT, SHIP_DESTROYED, PLAYER_WON):
            self.leds("RED")
        else:
            self.leds("GREEN")
        if result == SHIP_DESTROYED:
            log.info("Player sank a %s", payload.get("shipDestroyed"))
        # Up to the row, left to the column, push; wait for the result; then right and down (go_home)
        motion.wait_for_result()
        motion.go_home(self.hw)
        self.leds("GREEN")

    def alexa_missed(self, payload):
        self.leds("GREEN")

    def alexa_hit(self, payload):
        self.hw.sound.play_tone(880, 0.2)
        self.leds("RED")

    def alexa_sank_ship(self, payload):
        self.hw.sound.play_song((("C5", "e"), ("G4", "e"), ("C4", "q")))
        self.leds("RED")

    def finish_game(self, payload):
        self.hw.sound.play_song((("C4", "e"), ("E4", "e"), ("G4", "e"), ("C5", "q")))
        for color in ("RED", "GREEN", "AMBER", "GREEN"):
            self.leds(color)
        motion.go_home(self.hw)

    def test_mode(self, payload):
        log.info("Alexa board:\n%s", payload.get("logZones"))

    # ---------- helpers ----------

    def leds(self, color):
        self.hw.leds.set_color("LEFT", color)
        self.hw.leds.set_color("RIGHT", color)
