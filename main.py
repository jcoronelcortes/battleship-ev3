#!/usr/bin/env python3
"""Battleship robot: listens to AWS IoT Core (MQTT) and moves the EV3.

On the EV3:      python3 main.py
On a computer:   python3 main.py --simulate      (no motors, prints the moves)

Needs the folder certs/ with robot.env, certificate.pem.crt, private.pem.key and AmazonRootCA1.pem
(created by battleship-alexa-smart-mode/deploy/deploy.sh and copied by install.sh).

Python 3.5 compatible (ev3dev-stretch): no f-strings.
"""
import argparse
import logging
import os
import queue
import ssl
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "lib"))  # paho-mqtt copied by install.sh

import paho.mqtt.client as mqtt  # noqa: E402

import hardware  # noqa: E402
from robot import BattleshipRobot  # noqa: E402

log = logging.getLogger("main")


def read_env(path):
    values = {}
    with open(path) as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                key, value = line.split("=", 1)
                values[key.strip()] = value.strip()
    return values


def make_client(client_id):
    if hasattr(mqtt, "CallbackAPIVersion"):  # paho-mqtt 2.x (computer)
        return mqtt.Client(mqtt.CallbackAPIVersion.VERSION1, client_id=client_id, clean_session=True)
    return mqtt.Client(client_id=client_id, clean_session=True)  # paho-mqtt 1.x (EV3)


def main():
    parser = argparse.ArgumentParser(description="Battleship EV3 robot")
    parser.add_argument("--simulate", action="store_true", help="run without EV3 hardware")
    parser.add_argument("--certs", default=os.path.join(HERE, "certs"), help="folder with robot.env and certificates")
    args = parser.parse_args()

    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s: %(message)s")

    env = read_env(os.path.join(args.certs, "robot.env"))
    endpoint, topic, client_id = env["IOT_ENDPOINT"], env["TOPIC"], env["CLIENT_ID"]

    hw = hardware.simulated(speed_factor=0.05) if args.simulate else hardware.real()
    robot = BattleshipRobot(hw)
    robot.leds("AMBER")
    hw.sound.speak("Battleship")

    commands = queue.Queue()

    def on_connect(client, userdata, flags, rc):
        if rc == 0:
            log.info("Connected to AWS IoT %s, listening on %s", endpoint, topic)
            client.subscribe(topic, qos=1)
            robot.leds("GREEN")
        else:
            log.error("Connection refused (code %s). Check certificates and policy.", rc)
            robot.leds("RED")

    def on_disconnect(client, userdata, rc):
        log.warning("Disconnected from AWS IoT (code %s), reconnecting...", rc)
        robot.leds("AMBER")

    def on_message(client, userdata, message):
        commands.put(message.payload)

    client = make_client(client_id)
    client.tls_set(ca_certs=os.path.join(args.certs, "AmazonRootCA1.pem"),
                   certfile=os.path.join(args.certs, "certificate.pem.crt"),
                   keyfile=os.path.join(args.certs, "private.pem.key"),
                   tls_version=ssl.PROTOCOL_TLSv1_2)
    client.on_connect = on_connect
    client.on_disconnect = on_disconnect
    client.on_message = on_message
    client.reconnect_delay_set(min_delay=1, max_delay=30)

    log.info("Connecting to %s as %s", endpoint, client_id)
    client.connect_async(endpoint, 8883, keepalive=60)
    client.loop_start()

    try:
        # Motors block for seconds, so commands run here, one at a time, in arrival order
        while True:
            robot.handle_message(commands.get())
    except KeyboardInterrupt:
        log.info("Stopping")
    finally:
        client.loop_stop()
        client.disconnect()
        robot.leds("BLACK")


if __name__ == "__main__":
    main()
