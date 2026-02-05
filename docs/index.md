# Documentación técnica - rplidar-tcp-client

Documentación técnica y de referencia para el proyecto **rplidar-tcp-client**. Esta documentación complementa el README principal con información detallada sobre hardware, configuración de red y recursos de terceros.

> **Nota**: Esta carpeta contiene documentación técnica avanzada y de referencia. Para uso básico del proyecto, consulta el [README principal](../README.md).

---

## Contenido

### [Hardware](./hardware/)

Documentación sobre montaje físico y conexiones eléctricas.

- **[Montaje de RPi en Create 3 Cargo Bay](./hardware/rpi_create3_cargo_bay.md)** — Montaje físico de la Raspberry Pi 4 en la bahía de carga del iRobot Create 3, incluyendo planos mecánicos, hardware necesario (tornillos M2.5 y M3) y archivos STL.
- **[Diagrama de Cableado](./hardware/wiring.md)** — Esquemas de conexión eléctrica: alimentación de la RPi, conexión USB del RPLIDAR A1, y solución de problemas comunes.

### [Software](./software/)

Configuración de red y comunicaciones.

- **[Configuración de Red](./software/network_config.md)** — Configuración de red para la Raspberry Pi 4: IP estática, acceso remoto SSH, y conectividad con otros dispositivos (Create3, PC cliente).

### [Vendor (Documentación de Terceros)](./vendor/)

Manuales y datasheets oficiales de fabricantes.

- **[RPLIDAR A1](./vendor/rplidar_a1/)** — Documentación técnica oficial de Slamtec: datasheet, protocolo de comunicación, especificaciones técnicas.
- **[iRobot Create 3](./vendor/create3/)** — Documentación oficial de iRobot: especificaciones técnicas, archivos CAD, manuales de usuario.

---

## Relación con el proyecto

### Arquitectura actual (TCP directo)

El proyecto utiliza una arquitectura cliente-servidor TCP:

![Arquitectura](/docs/images/arquitectura_tcp.png)

**Documentación del servidor**: Ver [server/README.md](../server/README.md)  
**Documentación del cliente**: Ver [README principal](../README.md)

### Hardware compatible

- **Raspberry Pi 4** (recomendado) o superior
- **RPLIDAR A1** de Slamtec
- **Opcional**: iRobot Create 3 (para montaje móvil)

---

## Enlaces útiles

### Proyecto
- **Repositorio GitHub**: [github.com/PabloTarrio/rplidar-tcp-client](https://github.com/PabloTarrio/rplidar-tcp-client)
- **Issues**: [github.com/PabloTarrio/rplidar-tcp-client/issues](https://github.com/PabloTarrio/rplidar-tcp-client/issues)

### Documentación del proyecto
- [README principal](../README.md) - Uso básico del cliente
- [server/README.md](../server/README.md) - Instalación del servidor en RPi
- [examples/README.md](../examples/README.md) - Ejemplos de uso
- [CONTRIBUTING.md](../CONTRIBUTING.md) - Guía de contribución
- [CHANGELOG.md](../CHANGELOG.md) - Historial de cambios

### Referencias externas
- [RPLIDAR A1 Product Page](https://www.slamtec.com/en/Lidar/A1)
- [rplidar-roboticia (librería Python)](https://github.com/Roboticia/RPLidar)
- [iRobot Create 3 Docs](https://iroboteducation.github.io/create3_docs/)


## Contribuciones

Para reportar problemas, sugerir mejoras o contribuir al proyecto:

1. Revisa [CONTRIBUTING.md](../CONTRIBUTING.md) para el workflow
2. Abre un issue en [GitHub Issues](https://github.com/PabloTarrio/rplidar-tcp-client/issues)
3. Lee el [CODE_OF_CONDUCT.md](../CODE_OF_CONDUCT.md)

---

*Última actualización: Febrero 2026*
