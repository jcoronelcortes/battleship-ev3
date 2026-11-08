"""Runs on a computer with the simulated robot:  python3 -m unittest discover tests"""
import json
import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import config  # noqa: E402
import hardware  # noqa: E402
from robot import BattleshipRobot  # noqa: E402


def message(command, **fields):
    fields["command"] = command
    fields.setdefault("type", "command")
    return json.dumps(fields).encode("utf-8")


class RobotTest(unittest.TestCase):

    def setUp(self):
        self.hw = hardware.simulated()
        self.robot = BattleshipRobot(self.hw)

    def moves(self):
        return [(name, degrees) for name, action, degrees in self.hw.events if action == "run_to_rel_pos"]

    def test_start_game_homes_both_axes(self):
        self.robot.handle_message(message("start_game"))
        waits = [name for name, action, _ in self.hw.events if action == "wait_for_pressed"]
        self.assertEqual(waits, ["touch_horizontal", "touch_vertical"])

    def test_attack_on_c5_moves_pushes_and_returns_home(self):
        # Java sends C5 as row 2, column 4
        self.robot.handle_message(message("player_attack", row="2", column="4", attackResult=3))
        self.assertEqual(self.moves(), [
            ("vertical", (8 - 2) * config.ROW_DEGREES),
            ("horizontal", (8 - 4) * config.COLUMN_DEGREES),
            ("pusher", -config.PUSH_DEGREES),
            ("pusher", config.PUSH_DEGREES),
        ])
        waits = [name for name, action, _ in self.hw.events if action == "wait_for_pressed"]
        self.assertEqual(waits, ["touch_horizontal", "touch_vertical"])

    def test_attack_on_home_cell_i9_only_pushes(self):
        self.robot.handle_message(message("player_attack", row="8", column="8", attackResult=1))
        self.assertEqual([name for name, _ in self.moves()], ["pusher", "pusher"])

    def test_duplicate_attack_does_not_move(self):
        self.robot.handle_message(message("player_attack", row="2", column="4", attackResult=5))
        self.assertEqual(self.moves(), [])

    def test_stuck_sensor_stops_motor_and_shows_red(self):
        hw = hardware.simulated(sensors_work=False)
        BattleshipRobot(hw).handle_message(message("start_game"))
        self.assertIn(("horizontal", "stop", None), hw.events)
        self.assertEqual(hw.events[-3:-1], [("leds", "LEFT", "RED"), ("leds", "RIGHT", "RED")])

    def test_every_command_from_the_skill_is_handled(self):
        for command in ["start_game", "game_mode_configured", "fail_attack", "alexa_impact",
                        "alexa_ship_destroyed", "finish_game", "test_mode"]:
            self.assertIn(command, self.robot.handlers)

    def test_bad_messages_do_not_crash(self):
        self.robot.handle_message(b"not json")
        self.robot.handle_message(message("unknown_command"))
        self.robot.handle_message(message("player_attack"))  # missing row/column


if __name__ == "__main__":
    unittest.main()
