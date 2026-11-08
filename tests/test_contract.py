"""The skill (Java) and the robot (Python) must agree on the JSON format.

These are the exact messages from battleship-alexa RobotCommandContractTest.java:
if one side changes, both tests must change together.
"""
import os
import sys
import tempfile
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import config  # noqa: E402
import hardware  # noqa: E402
from robot import BattleshipRobot  # noqa: E402

START_GAME = ('{"type":"command","command":"start_game","attackResult":0,"shipDestroyed":"NO",'
              '"row":null,"column":null,"alexaRow":null,"alexaColumn":null,"logZones":null}')
PLAYER_SANK_SHIP = ('{"type":"command","command":"player_attack","attackResult":2,"shipDestroyed":"Destroyer",'
                    '"row":"2","column":"4","alexaRow":"E","alexaColumn":"5","logZones":null}')


class ContractTest(unittest.TestCase):

    def setUp(self):
        self.hw = hardware.simulated()
        self.robot = BattleshipRobot(self.hw)

    def test_start_game_message_from_the_skill(self):
        self.robot.handle_message(START_GAME.encode("utf-8"))
        self.assertIn(("touch_vertical", "wait_for_pressed", config.HOME_TIMEOUT_MS), self.hw.events)

    def test_player_attack_message_from_the_skill(self):
        self.robot.handle_message(PLAYER_SANK_SHIP.encode("utf-8"))
        moves = [(name, degrees) for name, action, degrees in self.hw.events if action == "run_to_rel_pos"]
        self.assertEqual(moves[:2], [("vertical", 6 * config.ROW_DEGREES), ("horizontal", 4 * config.COLUMN_DEGREES)])

    def test_cell_outside_the_board_does_not_move(self):
        bad = PLAYER_SANK_SHIP.replace('"row":"2"', '"row":"12"')
        self.robot.handle_message(bad.encode("utf-8"))
        self.assertFalse([e for e in self.hw.events if e[1] == "run_to_rel_pos"])
        self.assertIn(("leds", "LEFT", "RED"), self.hw.events)


class EnvFileTest(unittest.TestCase):

    def test_reads_robot_env_written_by_deploy_sh(self):
        import importlib
        main = importlib.import_module("main")
        with tempfile.NamedTemporaryFile("w", suffix=".env", delete=False) as f:
            f.write("IOT_ENDPOINT=abc-ats.iot.us-east-1.amazonaws.com\nTOPIC=battleship/ev3\n# comment\n\nCLIENT_ID=battleship-ev3\n")
        try:
            self.assertEqual(main.read_env(f.name), {
                "IOT_ENDPOINT": "abc-ats.iot.us-east-1.amazonaws.com",
                "TOPIC": "battleship/ev3",
                "CLIENT_ID": "battleship-ev3"})
        finally:
            os.remove(f.name)


if __name__ == "__main__":
    unittest.main()
