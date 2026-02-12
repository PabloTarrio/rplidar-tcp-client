# Servidor TCP LIDAR para Raspberry Pi

Este directorio contiene el código del servidor TCP que se ejecuta en la Raspberry Pi 4 para enviar datos del RPLIDAR A1 a clientes remotos.

## Requisitos

### Hardware
- Raspberry Pi 4 (recomendado) o superior
- RPLIDAR A1 conectado vía USB (adaptador incluido en el kit)
- Tarjeta SD con Ubuntu 24.04 Server (o similar)

### Software
- Python 3.10 o superior
- Puerto serie `/dev/ttyUSB0` disponible

### Cliente
Los clientes remotos requieren:

* Python 3.10+ con la libreria `lidarclient` instalada.
* Archivo `config.ini` configurado con la IP de este servidor

Ver [../README.md](../README.md) para instrucciones completas de configuración del cliente.

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
        # 10c4 = VendorID (VID)  - Identificador del fabricante [Silicon Labs]
        # ea60 = ProductID (PID) - Identificador del producto específico [Chip C210x UART Bridge]
        # Estamos buscando específicamente este dispositivo

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
> NOTA:
> Ubuntu 24.04 implementa PEP668 lo que impide instalar paquetes con pip directamente en el sistema para proteger conflictos.
>
> Dado que en mi proyecto voy a clonar la SD para replicarla, preferimos saltarnos esta restricción e instalar directamente en el sistema, aunque no es recomentable.
>
> Lo recomendable sería crear un Entorno Virtual, activarlo y realizar en él la instalación con el comando anterior.

```bash
# Instalar la librería rplidar directamente en el sistema.
pip3 install rplidar-roboticia --break-system-packages
```

### Paso 5: Copiar el servidor a la Raspberry Pi
Desde tu PC, copia el archivo del servidor:
```bash
scp /tu_ruta_al_archivo/servidor_lidar_tcp.py USUARIO_RASPBERRY_PI@IP_RASPBERRY_PI:/home/USUARIO_RASPBERRY_PI
```
Ejemplo:
```bash
scp /home/miusuario/proyecto/servidor_lidar_tcp.py pi@192.168.1.100:/home/pi
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

> **NOTA sobre modos de escaneo:**
> El servidor recibe el modo de escaneo (Standard o Express) desde cada cliente que se conecta.
> No es necesario configurar nada en el servidor. Los clientes especifican su modo preferido
> en su archivo `config.ini` mediante el parámetro `scan_mode`.

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

### Ejecutar como servicio systemd (arranque automático) [RECOMENDADO]

Para que el servidor arranque automáticamente al encender la Raspberry Pi:

### 1. Crear ubicación permanente con entorno virtual

```bash
# Crear carpeta del servidor
sudo mkdir -p /opt/rplidar-server

# Copiar el servidor
sudo cp servidor_lidar_tcp.py /opt/rplidar-server/
sudo chmod +x /opt/rplidar-server/servidor_lidar_tcp.py

# Instalar python3-venv si no está
sudo apt install -y python3-venv

# Crear entorno virtual
sudo python3 -m venv /opt/rplidar-server/.venv

# Instalar dependencias en el venv
sudo /opt/rplidar-server/.venv/bin/pip install rplidar-roboticia
```
### 2. Crear archivo de servicio
```bash
sudo nano /etc/systemd/system/rplidar-server.service 
```
Pegar este contenido en el archivo:
```text
[Unit]
Description=RPLIDAR A1 TCP Server
After=network.target
Wants=network-online.target

[Service]
Type=simple
User=root
WorkingDirectory=/opt/rplidar-server
ExecStart=/opt/rplidar-server/.venv/bin/python3 /opt/rplidar-server/servidor_lidar_tcp.py
Restart=on-failure
RestartSec=5
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
```
### 3. Activar y arrancar el servicio
```bash
# Recargar configuración de systemd
sudo systemctl daemon-reload

# Habilitar arranque automático
sudo systemctl enable rplidar-server.service

# Arrancar el servicio ahora
sudo systemctl start rplidar-server.service

# Ver estado
sudo systemctl status rplidar-server.service
```
### 4. Gestión del servicio
```bash
# Ver logs en tiempo real
sudo journalctl -u rplidar-server.service -f

# Reiniciar servicio
sudo systemctl restart rplidar-server.service

# Detener servicio
sudo systemctl stop rplidar-server.service

# Deshabilitar arranque automático
sudo systemctl disable rplidar-server.service
```
### 5. Verificar que funciona
```bash
# Comprobar que el puerto 5000 está escuchando
sudo ss -tlnp | grep 5000
# Debería mostrar: LISTEN ... python3 ...

# Obtener IP de la Raspberry Pi
hostname -I
```

Probar desde un cliente:

Los clientes ahora usan `config.ini` para configurar la conexión. Ver [../README.md](../README.md) para instrucciones del cliente.

Ejemplo rápido de prueba desde tu PC:
```bash
# 1. Configurar IP del servidor en config.ini
echo "[lidar]" > config.ini
echo "host = $(hostname -I | awk '{print $1}')" >> config.ini
echo "port = 5000" >> config.ini
echo "timeout = 5.0" >> config.ini
echo "max_retries = 3" >> config.ini
echo "retry_delay = 2.0" >> config.ini
echo "scan_mode = Express" >> config.ini
```

### 6. Clonar a otra Raspberry Pi
Para replicar esta configuración en otra RPi:
```bash
# 1. Copiar carpeta completa del servidor
scp -r /opt/rplidar-server usuario@otra-rpi:/opt/

# 2. Copiar archivo de servicio
scp /etc/systemd/system/rplidar-server.service usuario@otra-rpi:/tmp/

# 3. En la otra RPi, mover y activar
sudo mv /tmp/rplidar-server.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable rplidar-server.service
sudo systemctl start rplidar-server.service
```

### Ventajas de este método
* Entorno virtual aislado (cumple PEP668)
* Fácil de clonar a múltiples RPi
* Arranque automático robusto
* Logs centralizados en journalctl

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

## Rendimiento

El servidor soporta dos modos de escaneo que el cliente puede seleccionar:

### Modo Standard
* Puntos por revolución: ~360 puntos
* Datos de calidad: Sí (0-15)
* Frecuencia de escaneo: ~5-10 Hz
* Latencia de red: <50ms en LAN
* Ideal para: Aplicaciones que necesitan datos de calidad de las mediciones

### Modo Express
* Puntos por revolución: ~720 puntos (mayor densidad)
* Datos de calidad: No (`None`)
* Frecuencia de escaneo: ~5-10 Hz
* Latencia de red: <50ms en LAN
* Ideal para: Aplicaciones que priorizan densidad de puntos sobre calidad

> **Nota:** El modo se configura desde el cliente en `config.ini` mediante el parámetro `scan_mode`.

## Referencias
* [RPLIDAR A1 Datasheet](https://www.slamtec.com/en/Lidar/A1)
* [rplidar-robotics (Librería Python)](https://github.com/Roboticia/RPLidar)
* [Documentación Ubuntu Server](https://ubuntu.com/server/docs/)