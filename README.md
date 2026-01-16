[![CI](https://github.com/PabloTarrio/create3-lidar-client/actions/workflows/ci.yml/badge.svg)](https://github.com/PabloTarrio/create3-lidar-client/actions/workflows/ci.yml)

# create3-lidar-client

Librería Python orientada a docencia para conectarse a un sistema ROS 2 (Create3 + SBC/RPi) y consumir en remoto el topic `/scan` (mensajes `sensor_msgs/LaserScan`) de un LIDAR.

## Objetivo

Consumir el topic `/scan` (tipo `sensor_msgs/LaserScan`) desde un sistema ROS 2 (Create3 + SBC/RPi) y exponer una API Python simple para docencia.

## Requisitos

- ROS 2 Humble instalado en la máquina que ejecuta el cliente Python (Linux o Windows).
- Red: el robot/SBC y el cliente deben estar en la misma red (o red enrutable).
- `ROS_DOMAIN_ID` debe coincidir en todos los equipos.

## Requisitos de ejecución

Este paquete requiere ROS 2 (p. ej. Humble) instalado y el entorno cargado (`source /opt/ros/<distro>/setup.bash`) para poder usar `ScanClient`.

## Instalación (modo desarrollo)

```bash
git clone https://github.com/PabloTarrio/create3-lidar-client.git
cd create3-lidar-client
python3 -m venv .venv
source .venv/bin/activate
pip install -U pip
pip install -e .
```
## EJEMPLO
Tras cargar el entorno de ROS2 y activar tu venv:

```bash
python examples/print_scan_stub.py
```
