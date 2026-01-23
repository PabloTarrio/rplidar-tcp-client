# Documentación de create3-lidar-client

Bienvenido a la documentación del proyecto **create3-lidar-client**. Esta guía cubre la instalación de hardware, configuración y uso del escáner láser RPLIDAR A1 360° con el iRobot Create 3 y Raspberry Pi 4.

## Estructura de la Documentación

### [Instalación de Hardware](./hardware/)
Instalación física de la Raspberry Pi 4 en la bahía de carga del Create 3 e integración del sensor RPLIDAR A1.

- **[Montaje de RPi en Cargo Bay del Create 3](./hardware/rpi_create3_cargo_bay.md)** — Instrucciones paso a paso para montar la Raspberry Pi 4 dentro de la bahía de carga del Create 3, incluyendo planos mecánicos, hardware requerido (tornillos M2.5 y M3) y archivos STL.
- **[Diagrama de Cableado](./hardware/wiring.md)** — Conexiones eléctricas completas: USB-C entre Create 3 y RPi, adaptador USB para RPLIDAR A1, enrutamiento de potencia y solución de problemas comunes de conectores.

### [Configuración de Software](./software/)
Configuración de Ubuntu Server 22.04, ROS 2 Humble y conectividad de red.

- **[Configuración de Raspberry Pi 4 + ROS 2 Humble](./software/pi4_humble_setup.md)** — Guía completa incluyendo instalación de Ubuntu Server 22.04, configuración del modo gadget USB (`interfaz usb0`), instalación de ROS 2 Humble y selección de RMW (CycloneDDS vs FastDDS).
- **[Configuración de Red](./software/network_config.md)** — Configuración de `usb0` con IP fija (192.168.186.3/24), configuración de interfaz Wi-Fi (si aplica) y solución de problemas de descubrimiento DDS.

### [Integración de RPLIDAR A1](./rplidar_a1/)
Instalación del driver del sensor, archivos launch y integración con ROS 2.

- **[Configuración del Driver RPLIDAR A1](./rplidar_a1/driver_setup.md)** — Instalación del paquete rplidar_ros2, detección de puerto USB (`/dev/ttyUSB*`), configuración de velocidad en baudios (típicamente 115200) y verificaciones de estado.
- **[SLAM con create3_lidar_slam](./rplidar_a1/slam_setup.md)** — Uso del ejemplo oficial `create3_lidar_slam`: lanzamiento de `sensors_launch.py`, configuración de la transformación estática (frame del láser), y ejecución de SLAM con `slam_toolbox`.

### [Solución de Problemas](./troubleshooting/)
Problemas comunes y soluciones.

- **[Problemas de Hardware](./troubleshooting/hardware.md)** — LIDAR no detectado, problemas de conexión USB, problemas de suministro de energía.
- **[Problemas de ROS 2 / Red](./troubleshooting/ros2_network.md)** — Fallos en descubrimiento DDS, topics no publicándose, errores de frame TF, interfaz `usb0` no apareciendo.

### [Documentación de Terceros](./vendor/)
Hojas de datos y manuales de referencia oficiales.

- **[Documentación RPLIDAR A1](./vendor/rplidar_a1/)** — Documentación técnica oficial de Slamtec: datasheet, manual de usuario, protocolo de comunicación y referencia del SDK.
- **[Documentación iRobot Create 2](./vendor/create3/)** - Documentación técnica oficial de iRobot: datasheet, manual de usuario, archivos STL

---

## Lista de Verificación Rápida

- [ ] **Hardware**: RPi montada en cargo bay, LIDAR montado en la parte superior o placa portadora
- [ ] **Conexiones**: USB-C (Create 3 ↔ RPi), adaptador USB (LIDAR ↔ RPi), potencia verificada
- [ ] **USB Gadget**: `usb0` configurada y visible en la RPi (`ip a show usb0`)
- [ ] **Red**: Ping al Create 3 desde RPi (`ping 192.168.186.2`)
- [ ] **ROS 2**: Humble instalado, RMW_IMPLEMENTATION configurado y verificado
- [ ] **LIDAR**: Driver instalado, topic `/scan` publicándose
- [ ] **SLAM**: `create3_lidar_slam` ejecutándose, `slam_toolbox` activo, RViz mostrando mapa

---

## Enlaces del Proyecto

- **Repositorio**: [github.com/PabloTarrio/create3-lidar-client](https://github.com/PabloTarrio/create3-lidar-client)
- **Relacionado**: [Documentación iRobot Create 3](https://iroboteducation.github.io/create3_docs/), [create3_lidar_slam](https://index.ros.org/p/create3_lidar_slam/)

---

## Contribuciones

Para preguntas, problemas o mejoras, consulta [CONTRIBUTING.md](../CONTRIBUTING.md) y [CODE_OF_CONDUCT.md](../CODE_OF_CONDUCT.md).

