#!/usr/bin/env bash
# Se ejecuta en tu computador: copia el programa del robot al EV3 por WiFi (SSH).
#
#   ./install.sh                          # EV3 en ev3dev.local, usuario robot (contraseña: maker)
#   ./install.sh 192.168.1.50             # EV3 por dirección IP
#   ./install.sh ev3dev.local --service   # además, el robot arranca solo al encender el EV3
#   ./install.sh --fetch-only             # solo descarga paho-mqtt en lib/ (no necesita el EV3)
#
# Los certificados vienen de ../battleship-alexa-smart-mode/deploy/ev3-certs (los crea deploy.sh).
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

# ---------- paho-mqtt 1.5.1 (Python puro, funciona con el Python 3.5 del EV3) ----------
if [ ! -d lib/paho ]; then
  echo "Descargando paho-mqtt 1.5.1"
  TMP=$(mktemp -d)
  python3 -m pip download --quiet "paho-mqtt==1.5.1" --no-deps --no-binary :all: -d "$TMP"
  tar -xzf "$TMP"/paho-mqtt-1.5.1.tar.gz -C "$TMP"
  mkdir -p lib
  cp -R "$TMP"/paho-mqtt-1.5.1/src/paho lib/
  rm -rf "$TMP"
fi
[ "$FETCH_ONLY" = 1 ] && { echo "lib/paho listo"; exit 0; }

for f in robot.env certificate.pem.crt private.pem.key AmazonRootCA1.pem; do
  [ -f "${CERTS}/${f}" ] || { echo "Falta ${CERTS}/${f}. Primero ejecuta deploy/deploy.sh en battleship-alexa."; exit 1; }
done

# ---------- Copia al EV3 ----------
echo "Copiando a ${REMOTE}:${DEST} (la contraseña del usuario robot es 'maker', salvo que la hayas cambiado)"
ssh "$REMOTE" "mkdir -p ${DEST}/certs ${DEST}/lib"
scp -q -r *.py lib "${REMOTE}:${DEST}/"
scp -q "${CERTS}"/robot.env "${CERTS}"/certificate.pem.crt "${CERTS}"/private.pem.key "${CERTS}"/AmazonRootCA1.pem \
  "${REMOTE}:${DEST}/certs/"
ssh "$REMOTE" "chmod 600 ${DEST}/certs/private.pem.key && chmod +x ${DEST}/main.py ${DEST}/calibrate.py"

if [ "$SERVICE" = 1 ]; then
  echo "Instalando el servicio battleship (pide la contraseña del robot para sudo)"
  scp -q battleship.service "${REMOTE}:/tmp/battleship.service"
  ssh -t "$REMOTE" "sudo mv /tmp/battleship.service /etc/systemd/system/ && sudo systemctl daemon-reload && sudo systemctl enable --now battleship"
fi

echo
echo "Instalado. En el EV3 ejecuta:  cd ${DEST} && python3 main.py"
echo "O ábrelo desde la pantalla del EV3: File Browser > battleship > main.py"
