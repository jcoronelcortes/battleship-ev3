# battleship-ev3

Programa del robot LEGO EV3 para el juego **Batalla Naval con Alexa**.
La skill de Alexa (repo `battleship-alexa`, rama `smart-mode`) envía cada jugada por **AWS IoT Core (MQTT)** y el EV3 la recibe por WiFi.

```
"Alexa, abre batalla naval" → Skill → Lambda → AWS IoT Core → WiFi → EV3 (este programa)
```

> Versión 2026. La versión de 2019 usaba el Alexa Gadgets Toolkit (Bluetooth con el Echo), que Amazon retiró en 2021. El código antiguo sigue en la rama `master`.

## Archivos

| Archivo | Qué hace |
|---|---|
| `main.py` | Se conecta a AWS IoT y ejecuta los comandos que llegan, en orden |
| `robot.py` | Qué hace el robot con cada comando (`start_game`, `player_attack`, `finish_game`, …) |
| `motion.py` | Movimientos: volver a casa con los sensores táctiles, ir a una casilla, empujar el bloque |
| `config.py` | Puertos, grados por fila y columna, velocidades y timeouts |
| `calibrate.py` | Calibración después de armar el robot |
| `hardware.py` | Motores reales de ev3dev2, o un robot simulado para probar en el computador |
| `install.sh` | Copia todo al EV3 desde tu computador |

## Conexiones

| Puerto | Elemento |
|---|---|
| A | Motor grande vertical derecho |
| D | Motor grande vertical izquierdo |
| C | Motor grande horizontal |
| B | Motor mediano (empuja el bloque Duplo) |
| 1 | Sensor táctil horizontal (posición inicial) |
| 4 | Sensor táctil vertical (posición inicial) |

La posición inicial ("casa") es la casilla **I9**.

En cada ataque el robot **sube** hasta la fila, va a la **izquierda** hasta la columna, **empuja** el bloque y **espera** en la casilla con la luz del resultado (roja si fue impacto, verde si fue agua) mientras Alexa lo anuncia. Después vuelve: primero a la **derecha** y luego **baja** hasta I9. La espera se ajusta con `RESULT_WAIT_SECONDS` en `config.py`.

## Instalación en el EV3

### 1. Sistema operativo
1. Descarga **ev3dev-stretch** (`ev3dev-stretch-ev3-generic-2020-04-10.zip`, la última versión) desde <https://www.ev3dev.org/downloads/>.
2. Grábalo en una microSD de 4 a 32 GB con [balenaEtcher](https://etcher.balena.io/).
3. Pon la microSD en el EV3 y enciéndelo. El primer arranque tarda unos 2 minutos.

### 2. WiFi
1. Conecta el adaptador WiFi USB (Edimax EW-7811Un) al puerto USB del EV3.
2. En la pantalla del EV3: **Wireless and Networks → Wi-Fi → Powered** (activar) **→ Start Scan**. Elige tu red y luego **Connect**.
3. Anota la IP que aparece arriba en la pantalla.

> El EV3 necesita la **hora correcta** para la conexión segura con AWS. ev3dev la sincroniza sola al tener internet. Si al conectarse ves `certificate verify failed`, revisa la hora con `date` por SSH.

### 3. Copiar el programa (desde tu Mac)
Primero tienen que existir los certificados. Se crean con `deploy/deploy.sh` en el repo `battleship-alexa`.
```bash
./install.sh                # o: ./install.sh 192.168.x.x
```
La contraseña del usuario `robot` es `maker`.

### 4. Calibrar
Por SSH (`ssh robot@ev3dev.local`):
```bash
cd battleship && python3 calibrate.py           # va a A1, E5 e I9
python3 calibrate.py --push C5                  # además empuja un bloque
```
Si el empujador queda antes o después de la casilla, ajusta `ROW_DEGREES` o `COLUMN_DEGREES` en `config.py`.

### 5. Jugar
```bash
python3 main.py
```
Cuando las luces del EV3 se ponen **verdes**, el robot está conectado. Di: **"Alexa, abre batalla naval"**.

Para que el robot arranque solo al encender el EV3:
```bash
./install.sh ev3dev.local --service
```

## Luces del EV3

| Color | Significado |
|---|---|
| Ámbar | Conectando o moviéndose |
| Verde | Conectado, esperando jugada |
| Rojo | Impacto, o error (por ejemplo, un sensor táctil no se presionó a tiempo y el motor se detuvo) |

## Probar sin el EV3
```bash
python3 -m unittest discover tests
python3 main.py --simulate --certs ../battleship-alexa-smart-mode/deploy/ev3-certs
```
El modo `--simulate` se conecta a AWS IoT de verdad y muestra en pantalla los movimientos que haría el robot.
