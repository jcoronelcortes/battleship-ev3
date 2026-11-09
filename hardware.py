"""Creates the robot hardware: the real ev3dev2 devices, or a simulated robot for testing on a computer.

Compatible con Python 3.5 (ev3dev-stretch): sin f-strings.
"""
import logging
import time

import config

log = logging.getLogger("hardware")


class Hardware(object):
    def __init__(self, vertical, horizontal, pusher, touch_vertical, touch_horizontal, leds, sound):
        self.vertical = vertical
        self.horizontal = horizontal
        self.pusher = pusher
        self.touch_vertical = touch_vertical
        self.touch_horizontal = touch_horizontal
        self.leds = leds
        self.sound = sound


def real():
    from ev3dev2.led import Leds
    from ev3dev2.motor import LargeMotor, MediumMotor, MoveTank
    from ev3dev2.sensor.lego import TouchSensor
    from ev3dev2.sound import Sound

    vertical = MoveTank(config.PORT_VERTICAL_LEFT, config.PORT_VERTICAL_RIGHT)
    vertical.reset()
    return Hardware(
        vertical=vertical,
        horizontal=LargeMotor(config.PORT_HORIZONTAL),
        pusher=MediumMotor(config.PORT_PUSHER),
        touch_vertical=TouchSensor(config.PORT_TOUCH_VERTICAL),
        touch_horizontal=TouchSensor(config.PORT_TOUCH_HORIZONTAL),
        leds=Leds(),
        sound=Sound())


# ---------------- Simulated robot (no EV3 needed) ----------------

class _SimMotor(object):
    def __init__(self, name, events, speed_factor):
        self.name = name
        self.events = events
        self.speed_factor = speed_factor

    def on(self, *args, **kwargs):
        self.events.append((self.name, "on", kwargs))

    def run_to_rel_pos(self, position_sp=0, speed_sp=0):
        self.events.append((self.name, "run_to_rel_pos", position_sp))
        log.info("[sim] %s turns %d degrees", self.name, position_sp)
        time.sleep(abs(position_sp) / float(speed_sp or 1) * self.speed_factor)

    def wait_while(self, state, timeout=None):
        return True

    def stop(self):
        self.events.append((self.name, "stop", None))

    def reset(self):
        pass


class _SimTouch(object):
    def __init__(self, name, events, works=True):
        self.name = name
        self.events = events
        self.works = works
        self.is_pressed = False

    def wait_for_pressed(self, timeout_ms=None):
        self.events.append((self.name, "wait_for_pressed", timeout_ms))
        return self.works


class _SimLeds(object):
    def __init__(self, events):
        self.events = events

    def set_color(self, group, color):
        self.events.append(("leds", group, color))


class _SimSound(object):
    def __init__(self, events):
        self.events = events

    def speak(self, text, **kwargs):
        self.events.append(("sound", "speak", text))
        log.info("[sim] says: %s", text)

    def beep(self, *args, **kwargs):
        self.events.append(("sound", "beep", None))

    def play_song(self, song, **kwargs):
        self.events.append(("sound", "song", len(song)))

    def play_tone(self, frequency, duration, **kwargs):
        self.events.append(("sound", "tone", frequency))


def simulated(speed_factor=0.0, sensors_work=True):
    """speed_factor 1.0 waits as long as the real motors would; 0 runs instantly (tests)."""
    events = []
    hw = Hardware(
        vertical=_SimMotor("vertical", events, speed_factor),
        horizontal=_SimMotor("horizontal", events, speed_factor),
        pusher=_SimMotor("pusher", events, speed_factor),
        touch_vertical=_SimTouch("touch_vertical", events, sensors_work),
        touch_horizontal=_SimTouch("touch_horizontal", events, sensors_work),
        leds=_SimLeds(events),
        sound=_SimSound(events))
    hw.events = events
    return hw
