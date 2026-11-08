#!/usr/bin/env bash
# Run on your computer to copy the robot program to the EV3 over WiFi (SSH).
#
#   ./install.sh                      # EV3 at ev3dev.local, user robot (password: maker)
#   ./install.sh 192.168.1.50         # EV3 by IP address
#   ./install.sh ev3dev.local --service   # also start the robot automatically when the EV3 boots
#   ./install.sh --fetch-only         # only download paho-mqtt into lib/ (no EV3 needed)
#
# Certificates come from ../battleship-alexa-smart-mode/deploy/ev3-certs (created by deploy.sh).
set -euo pipefail
cd "$(dirname "$0")"

HOST="ev3dev.local"
SERVICE=0
FETCH_ONLY=0
for arg in "$@"; do
  case "$arg" in
    --service) SERVICE=1 ;;
    --fetch-only) FETCH_ONLY=1 ;;
    *) HOST="$arg" ;;
  esac
done
CERTS="${CERTS:-../battleship-alexa-smart-mode/deploy/ev3-certs}"
REMOTE="robot@${HOST}"
DEST="/home/robot/battleship"

# ---------- paho-mqtt 1.5.1 (pure Python, works with the EV3's Python 3.5) ----------
if [ ! -d lib/paho ]; then
  echo "Downloading paho-mqtt 1.5.1"
  TMP=$(mktemp -d)
  python3 -m pip download --quiet "paho-mqtt==1.5.1" --no-deps --no-binary :all: -d "$TMP"
  tar -xzf "$TMP"/paho-mqtt-1.5.1.tar.gz -C "$TMP"
  mkdir -p lib
  cp -R "$TMP"/paho-mqtt-1.5.1/src/paho lib/
  rm -rf "$TMP"
fi
[ "$FETCH_ONLY" = 1 ] && { echo "lib/paho ready"; exit 0; }

for f in robot.env certificate.pem.crt private.pem.key AmazonRootCA1.pem; do
  [ -f "${CERTS}/${f}" ] || { echo "Missing ${CERTS}/${f}. Run deploy/deploy.sh first."; exit 1; }
done

# ---------- Copy to the EV3 ----------
echo "Copying to ${REMOTE}:${DEST} (password for user robot is 'maker' unless you changed it)"
ssh "$REMOTE" "mkdir -p ${DEST}/certs ${DEST}/lib"
scp -q -r *.py lib "${REMOTE}:${DEST}/"
scp -q "${CERTS}"/robot.env "${CERTS}"/certificate.pem.crt "${CERTS}"/private.pem.key "${CERTS}"/AmazonRootCA1.pem \
  "${REMOTE}:${DEST}/certs/"
ssh "$REMOTE" "chmod 600 ${DEST}/certs/private.pem.key && chmod +x ${DEST}/main.py ${DEST}/calibrate.py"

if [ "$SERVICE" = 1 ]; then
  echo "Installing the battleship service (asks for the robot password for sudo)"
  scp -q battleship.service "${REMOTE}:/tmp/battleship.service"
  ssh -t "$REMOTE" "sudo mv /tmp/battleship.service /etc/systemd/system/ && sudo systemctl daemon-reload && sudo systemctl enable --now battleship"
fi

echo
echo "Installed. On the EV3 run:  cd ${DEST} && python3 main.py"
echo "Or open it from the EV3 screen: File Browser > battleship > main.py"
