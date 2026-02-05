[![CI](https://github.com/PabloTarrio/rplidar-tcp-client/actions/workflows/ci.yml/badge.svg?branch=main)](https://github.com/PabloTarrio/rplidar-tcp-client/actions/workflows/ci.yml)

# rplidar-tcp-client

Librería Python para acceder remotamente a datos del sensor RPLIDAR A1 conectado a una Raspberry Pi 4 mediante TCP sockets.

## Objetivo

Proporcionar una forma simple y directa de obtener datos de escaneo LIDAR desde cualquier ordenador mediante TCP, sin necesidad de instalar ROS 2.

## Características

- **Sin dependencias de ROS 2**: Comunicación TCP pura con Python estándar
- **Acceso remoto**: Conecta desde cualquier PC en la misma red
- **Plug & play**: API simple con context managers
- **Fácil instalación**: `pip install` directo
- **Ejemplos incluidos**: Scripts listos para usar

## Requisitos

### Servidor (Raspberry Pi 4)
- Raspberry Pi 4 con Ubuntu 22.04 Server
- RPLIDAR A1 conectado vía USB
- Python 3.10+
- Librería `rplidar` instalada

### Cliente (tu PC)
- Python 3.10+
- Conexión de red a la Raspberry Pi

## Instalación

### En tu PC (cliente)

```bash
git clone https://github.com/PabloTarrio/rplidar-tcp-client.git
cd rplidar-tcp-client
python3 -m venv venv
source venv/bin/activate  # En Windows: venv\Scripts\activate
pip install -e .
```

## En la Raspberry Pi (servidor)
El servidor TCP debe estar corriendo en la Raspberry Pi. Consulta la documentación en `/server` para instrucciones de instalación

## Uso básico:

Ejemplo simple:

``` python
from lidarclient import LidarClient

# Conectar al servidor (ajusta la IP de tu Raspberry Pi)
with LidarClient("192.168.1.100", port=5000) as client:
    # Obtener una revolución completa
    scan = client.get_scan()
    
    print(f"Recibidos {len(scan)} puntos")
    
    # Cada punto es una tupla (quality, angle, distance)
    for quality, angle, distance in scan[:5]:
        print(f"Ángulo: {angle:.2f}°, Distancia: {distance:.2f}mm")
```
El proyecto incluye varios scripts de ejemplo:
```bash
# Captura básica de una revolución
python examples/simplescan.py

# Stream continuo con estadísticas
python examples/continuousstream.py

# Formato compatible con ROS 2 LaserScan
python examples/printscanstub.py
```

Consulta [examples/README.md](https://github.com/PabloTarrio/rplidar-tcp-client/blob/main/examples/README.md) para más detalles sobre cada ejemplo

## Estructura del proyecto:

``` text
rplidar-tcp-client/
├── src/
│   └── lidarclient/          # Librería cliente
│       ├── __init__.py
│       └── client.py
├── examples/                 # Scripts de ejemplo
│   ├── simplescan.py
│   ├── continuousstream.py
│   └── printscanstub.py
├── server/                   # Código del servidor (Raspberry Pi)
├── tests/                    # Tests
└── docs/                     # Documentación adicional
```

## Configuración:

* Cambiar la IP del servidor

Todos los ejemplos usan `192.168.1.100` por defecto. Cámbiala por la IP de tu Raspberry Pi:

``` python
client = LidarClient("TU_IP_RASPBERRY_PI", port=5000)
```

## Solución de problemas:
``` text Error: Conection refused ```
* Verifica que el servidor TCP está corriendo en la Raspberry Pi.
* Comprueba que la IP con `ping IP_TU_RASPBERRY_PI`

``` texto Error: No module named 'lidarclient'```
* Asegúrate de haber instalado el paquete: `pip install -e .`
* Activa el entorno virtual si lo estás usando

## Desarrollo:
Ejecutar tests

```bash
pytest 
```

Ejecutar linting
```bash
ruff check .
ruff format .
```

## Contribuir
Lee [CONTRIBUTING.md](https://github.com/PabloTarrio/rplidar-tcp-client/blob/main/CONTRIBUTING.md) para conocer el workflow de desarollo

## Licencia
Este proyecto está bajo licencia MIT. Ver [LICENSE.md](https://github.com/PabloTarrio/rplidar-tcp-client/blob/main/LICENSE) para más detalles.

## Documentación adicional
* [CHANGELOG.md](https://github.com/PabloTarrio/rplidar-tcp-client/blob/main/CHANGELOG.md): Historial de cambios
* [CODE_OF_CONDUCT.md](https://github.com/PabloTarrio/rplidar-tcp-client/blob/main/CODE_OF_CONDUCT.md): Código de conducta
* [examples/README.md](https://github.com/PabloTarrio/rplidar-tcp-client/blob/main/examples/README.md): Detalles sobre los ejemplos disponibles.

## Enlaces relacionados
* [RPLIDAR A1 Datasheet](https://www.slamtec.com/en/Lidar/A1)
* [rplidar-robotics (Librería Python)](https://github.com/Roboticia/RPLidar)