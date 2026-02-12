[![CI](https://github.com/PabloTarrio/rplidar-tcp-client/actions/workflows/ci.yml/badge.svg?branch=main)](https://github.com/PabloTarrio/rplidar-tcp-client/actions/workflows/ci.yml)

# rplidar-tcp-client

Librería Python para acceder remotamente a datos del sensor RPLIDAR A1 conectado a una Raspberry Pi 4 mediante TCP sockets.

## Objetivo

Proporcionar una forma simple y directa de obtener datos de escaneo LIDAR desde cualquier ordenador mediante TCP, sin necesidad de instalar ROS 2.

## Características

- **Sin dependencias de ROS 2**: Comunicación TCP pura con Python estándar
- **Acceso remoto**: Conecta desde cualquier PC en la misma red
- **Configuración simple**: Archivo `config.ini` con tu LIDAR asignado
- **Reconexión automática**: Reintentos configurables si falla la conexión
- **Plug & play**: API simple con context managers
- **Fácil instalación**: `pip install` directo
- **Ejemplos incluidos**: Scripts listos para usar

## Requisitos

### Servidor (Raspberry Pi 4)
- Raspberry Pi 4 con Ubuntu 24.04 Server
- RPLIDAR A1 conectado vía USB
- Python 3.10+
- Librería `rplidar` instalada

### Cliente (tu PC)
- Python 3.10+
- Conexión de red a la Raspberry Pi

## Instalación

### 1. En tu PC (cliente)

```bash
git clone https://github.com/PabloTarrio/rplidar-tcp-client.git
cd rplidar-tcp-client
python3 -m venv venv
source venv/bin/activate  # En Windows: venv\Scripts\activate
pip install -e .
```

### 2. Configurar tu LIDAR

Copia el archivo de ejemplo y edita la IP de tu LIDAR asignado:

```bash
cp config.ini.example config.ini
nano config.ini # o usa tu editor favorito
```
Edita la linea `host` con la Ip de tu servidor LIDAR:

```text
[lidar]
#Cambia esta IP por la de tu LIDAR asignado
host = 192.168.1.103
port = 5000
timeout = 5.0
max_retries = 3
retry_delay = 2.0
scan_mode = Express
```
LIDAR disponibles en el Laboratorio:

* LIDAR 1: 192.168.1.101
* LIDAR 2: 192.168.1.102
* LIDAR 3: 192.168.1.103
* LIDAR 4: 192.168.1.104
* LIDAR 5: 192.168.1.105
* LIDAR 6: 192.168.1.106

>NOTA: El archivo `config.ini` es local y no se sube a GIT (está en .gitignore)

### 3. En la Raspberry PI (servidor)
El servidor TCP debe estar corriendo en la Raspberry Pi. Consulta la documentación en [server/README.md](/server/README.md) para instrucciones de instalación.

## Uso Básico

### Ejemplo simple
```python
from lidarclient import LidarClient
from lidarclient.config import load_config

# Cargar configuración desde config.ini
config = load_config()

# Conectar al servidor
with LidarClient(
    config["host"],
    port = config["port"],
    timeout = config["timeout"],
    max_retries = config["max_retries"],
    retry_delay = config["retry_delay"],
    scan_mode = config["scan_mode"]
) as client:
    # Obtener una revolución completa
    scan = client.get_scan()
    
    print(f"Recibidos {len(scan)} puntos")
    
    # Cada punto es una tupla (quality, angle, distance)
    for quality, angle, distance in scan[:5]:
        print(f"Ángulo: {angle:.2f}°, Distancia: {distance:.2f}mm")
```
### Ejemplos incluidos

El proyecto incluye varios scripts de ejemplo para usar:
```bash
# Captura básica de una revolución
python examples/simple_scan.py

# Stream continuo con estadísticas
python examples/continuous_stream.py

# Formato compatible con ROS 2 LaserScan
python examples/print_scan_stub.py

# Visualización de datos en tiempo real. Gráfico 2D
python examples/visualize_realtime.py

# Diagnóstico y comparación de modos de escaneo
python examples/lidar_diagnostics.py
```


Todos los ejemplos leen automaticamente tu `config.ini`, así que solo necesitas configurarlo una vez.

Consulta [examples/README.md](/examples/README.md) para más detalles sobre cada ejemplo.

## Estructura del proyecto
```text
rplidar-tcp-client/
|___ config.ini.example          # Plantilla de configuración
|___ src/
|    |___lidarclient/
|        |___ __init__.py
|        |___ client.py
|        |___ config.py          # Parser de configuración
|___ examples/                   # Scripts de ejemplo
|    |___ simple_scan.py
|    |___ continuous_stream.py
|    |___ print_scan_stub.py
|    |___ visualize_realtime.py
|    |___ lidar_diagnostics.py
|___ server/                     # Código del servidor (Raspberry Pi)
|___ tests/                      # Tests
|___ docs/                       # Documentación adicional
```

## Configuración avanzada
Parámetros del `config.ini`:

* `host` (obligatorio): IP del servidor LIDAR
* `port` (default: 5000): Puerto TCP del servidor
* `timeout` (default: 5.0): Timeout en segundos para operaciones de red
* `max_retries` (default: 3): Número de reintentos si falla la conexión
* `retry_delay` (default: 2.0): Segundos de espera entre reintentos
* `scan_mode` (default: Express): Modo de escaneo del LIDAR
    - `Standard`: ~360 puntos/revolución, incluye datos de calidad (0-15)
    - `Express` : ~720 puntos/revolución, sin datos de calidad


Uso sin `config.ini` (avanzado)

Si necesitas especificar la IP directamente en el código:

```python
from lidarclient import LidarClient

client = LidarClient("10.0.0.5", port=5000, max_retries=3, scan_mode= 'Express')
client.connect_with_retry()
scan = client.get_scan()
client.disconnect()
```

## Solución de problemas

#### Error: `No se encontró el archivo 'config.ini'`

Solución:
```bash
cp config.ini.example config.ini
nano config.ini # Edita la IP de tu LIDAR
```

#### Error: `Connection refused`

Causas posibles:

* El servidor TCP no está corriendo en la Raspberry Pi.
* La IP en `config.ini` es incorrecta
* Problema de red/firewall

Solución:

1. Verifica que el servidor está corriendo: 
```bash 
sudo systemctl status rplidar-server.service
```
2. Comprueba la IP:
```bash 
ping <IP_de_tu_config.ini>
```
3. Verifica que el puerto 5000 está abierto
```bash 
sudo ss -tlnp | grep 5000
```

#### Error: `No module named 'lidarclient'`

Solución:

* Asegúrate de haber instalado el paquete:
```bash 
pip install -e .
```
* Activa el entorno virtual si lo estás usando: 
```bash
source venv\bin\activate
```
#### Timeout al conectar

Solución:
Aumenta el `timeout` en `config.ini`:
```text
timeout = 10.0
```

## Desarollo

#### Ejecutar tests
```bash
pytest
```

#### Ejecutar linting
```bash
ruff check .
ruf format .
```

## Contribuir

Lee [CONTRIBUTING.md](/CONTRIBUTING.md) para conocer el workflow de desarrollo.

## Licencia

Este proyecto está bajo licencia MIT. Ver [LICENSE](/LICENSE) para más detalles

## Documentacion adicional

* [CHANGELOG.md](/CHANGELOG.md): Historial de cambios.
* [CODE_OF_CONDUCT.md](/CODE_OF_CONDUCT.md): Código de conducta.
* [examples/README.md](/examples/README.md): Detalles sobre los ejemplos disponibles
* [server/README.md](/server/README.md): Configuración del servidor en Raspberry Pi.

## Enlaces relacionados
* [SLAMTEC RPLIDAR A1 Datasheet](https://www.slamtec.com/en/Lidar/A1)
* Librería Python: [rplidar-roboticia](https://github.com/Roboticia/RPLidar)