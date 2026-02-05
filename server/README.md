# Servidor TCP LIDAR para Raspberry Pi

Este directorio contiene el código del servidor TCP que se ejecuta en la Raspberry Pi 4 para enviar datos del RPLIDAR A1 a clientes remotos.

## Requisitos

### Hardware
- Raspberry Pi 4 (recomendado) o superior
- RPLIDAR A1 conectado vía USB (adaptador incluido en el kit)
- Tarjeta SD con Ubuntu 22.04 Server (o similar)

### Software
- Python 3.10 o superior
- Puerto serie `/dev/ttyUSB0` disponible

## Instalación

### Paso 1: Preparar el entorno

```bash
# Actualizar el sistema
sudo apt update
sudo apt upgrade -y

# Instalar Python y pip si no están instalados
sudo apt install python3 python3-pip -y
```

### Paso 2: Verificar conexion del LIDAR
``` bash
# Listar dispositivos USB
lsusb | grep -i "10c4:ea60"

# Verificar puerto de serie
ls -l /dev/ttyUSB0
```
Deberías ver: `Silicon Labs CP210x UART Bridge`

### Paso 3: Configurar permisos
```bash
# Añadir tu usuario al grupo dialout
sudo usermod -a -G dialout $USER
# Cerrar sesión y volver a entrar para aplicar cambios
# o ejecutar:
newgrp dialout
```
### Paso 4: Instalar dependencias
```bash
# Instalar la librería rplidar
pip3 install rplidar-roboticia
```
### Paso 5: Copiar el servidor a la Raspberry Pi
Desde tu PC, copia el archivo del servidor:
```bash
scp servidor_lidar_tcp.py usuario@IP_RASPBERRY:/home/usuario/
```
Ejemplo:
```bash
scp servidor_lidar_tcp.py pi@192.168.1.100:/home/pi
```
## Ejecutar en el servidor
En la Raspberry Pi:
```bash
# Navegar al directorio donde está el servidor
cd ~

# Ejecutar el servidor
python3 servidor_lidar_tcp.py
```

Salida esperada:

```text
============================================================
SERVIDOR LIDAR TCP (modo continuo)
============================================================

 Conectando al LIDAR...[2]
✓ LIDAR conectado

 Iniciando servidor TCP...[3]
✓ Servidor escuchando en puerto 5000

 Esperando cliente...[1]
```
El servidor quedará esperando conexiones. Para detenerlo, presiona `CTRL+C`

## Configuración avanzada
### Cambiar el puerto TCP
Edita `servidor_lidar_tcp.py` y modifica:

```python
TCP_PORT = 5000 # Cambia a otro puerto si lo necesitas
```

### Usar otro puerto serie
Si tu LIDAR está en /dev/ttyUSB1 o similar:
```python
LIDAR PORT = "/dev/ttyUSB1"
```

### Ejecutar como servicio systemd (arranque automático)
Para que el servidor arranque automáticamente al encender la Raspberry Pi:

1. Crear archivo de servicio:
```bash
sudo nano etc/systemd/system/lidar-server.service
```

2. Pegar el siguiente contenido (ajusta las rutas si es necesario):

```text
[Unit]
Description=RPLIDAR TCP Server
After=network.target

[Service]
Type=simple
User=pi
WorkingDirectory=/home/pi
ExecStart=/usr/bin/python3 /home/pi/servidor_lidar_tcp.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

3. Activar y arrancar el servicio
```bash
sudo systemctl daemon-reload
sudo systemctl enable lidar-server
sudo systemctl start lidar-server

# Ver estado
sudo systemctl status lidar-server

# Ver logs
journalctl -u lidar-server -f
```

## Solución de problemas

* Error: `Permission denied: '/dev/ttyUSB0'`

Solución: Tu usuario no tiene permisos para acceder al puerto serie.

```bash
sudo usermod -a -G dialout $USER
# Cerrar sesión y volver a entrar
```

* Error : `ModuleNorFoundError: No module named 'rplidar'`

Solución: La librería no está instalada.

```bash
pip3 install rplidar-roboticia
```

* Error: `Address already in use`

Solución: El puerto 5000 está siendo usado por otro proceso.

```bash
# Ver qué proceso está usando el puerto
sudo lsof -i :5000

# Matar el proceso (esa el PID que aparece)
sudo kill -9 PID
```
* Error: El LIDAR no se detecta

Solución: Verifica la conexión física y los drivers

``` bash
# Ver dispositivos USB conectados
lsusb

# Ver mensajes del kernel
dmesg | grep ttyUSB

# Si no aparece /dev/ttyUSB0, prueba a reconectar el cable USB o incluso a cambiarlo
```

* Error: El cliente no puede conectarse

Solución: Verificar firewall y red
```bash
# Verificar que el servidor esté escuchando
sudo netstat -tulpn | grep 5000

# Permitir el puerto en el firewall (si está activo)
sudo ufw allow 5000/tcp

# Verificar IP de la Raspberry Pi
hostname -I
```

## Rendimiento:
* Puntos por revolución: ~60-70 puntos (modo normal)
* Frecuencia de escaneo: ~5-10Hz
* Latencia de red: <50ms en LAN

## Referencias
* [RPLIDAR A1 Datasheet](https://www.slamtec.com/en/Lidar/A1)
* [rplidar-robotics (Librería Python)](https://github.com/Roboticia/RPLidar)
* [Documentación Ubuntu Server](https://ubuntu.com/server/docs/)