# create3-lidar-client
Librería Python orientada a docencia para conectarse a un sistema ROS 2 (Create3 + SBC/RPi) y consumir en remoto el topic /scan (mensajes sensor_msgs/LaserScan) de un LIDAR, ofreciendo una API sencilla para leer, filtrar y reenviar datos de distancia desde scripts o aplicaciones. ​

## Objetivo

Consumir el topic `/scan` (tipo `sensor_msgs/LaserScan`) desde un sistema ROS 2 (Create3 + SBC/RPi) y exponer una API Python simple para docencia.

## Requisitos

- ROS 2 Humble instalado en la máquina que ejecuta el cliente Python (Linux o Windows).
- Red: el robot/SBC y el cliente deben estar en la misma red (o red enrutable).
- `ROS_DOMAIN_ID` debe coincidir en todos los equipos.

## Instalación (modo desarrollo)

```bash
git clone https://github.com/PabloTarrio/create3-lidar-client.git
cd create3-lidar-client
python3 -m venv .venv
source .venv/bin/activate
pip install -U pip
pip install -e .
