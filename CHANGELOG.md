# Changelog

All notable changes to this project will be documented in this file.

---

## [0.4.0] - 2026-02-11

### Added
- Sistema de configuración flexible con `config.ini`
  - Archivo de plantilla `config.ini.example` versionado
  - Parser de configuración en `src/lidar_client/config.py`
  - Configuración de: host, port, timeout, max_retries, retry_delay
  - Documentación de los 6 LIDAR del laboratorio UIE
  - Protección con `.gitignore` para evitar subir configuraciones locales
- Reconexión automática del cliente
  - Nuevo método `connect_with_retry()` con lógica de reintentos
  - Parámetros configurables `max_retries` y `retry_delay`
  - Logging informativo de cada intento de conexión
- Tests unitarios con pytest (Commit #58)
  - Cobertura de código: 88%
  - CI/CD automático con GitHub Actions
  - Ejecución automática en cada Pull Request
- Servicio systemd para servidor persistente
  - Arranque automático al iniciar la Raspberry Pi
  - Entorno virtual aislado (cumple PEP 668)
  - Logs centralizados con journalctl
  - Documentación completa en `server/README.md`
  - Instrucciones de clonación a múltiples RPi

### Changed
- Ejemplos actualizados para usar `config.ini` en lugar de IPs hardcodeadas
- Cliente soporta parámetros de reconexión: `max_retries`, `retry_delay`
- Servidor optimizado: inicia escaneo SOLO cuando hay cliente conectado
- Servidor detiene escaneo automáticamente al desconectar cliente

### Fixed
- Saturación del buffer del LIDAR (Commit #55)
  - El servidor ya no acumula datos cuando no hay clientes conectados
  - Prevención del error "Too many bytes in the input buffer"
- Compatibilidad hacia atrás: `connect()` sigue funcionando sin cambios

---

## [0.3.0] - 2026-02-09

### Added
- Manejo robusto de errores en el cliente con excepciones personalizadas (`LidarConnectionError`, `LidarTimeoutError`, `LidarDataError`)
- Timeout configurable en el cliente (por defecto 5.0s)
- Validación de tamaño de datos recibidos para prevenir corrupción
- Método privado `_recv_exact()` para asegurar recepción completa de datos
- Logging detallado en el servidor con rotación automática de archivos
- Manejo de señales (SIGINT/SIGTERM) en el servidor para cierre limpio

### Changed
- Mejorados mensajes de error con contexto claro
- Exportadas nuevas excepciones en `__init__.py`
- Servidor ahora registra todas las operaciones y errores

### Fixed
- Prevención de corrupción de datos en transmisiones parciales

---

## [0.2.0] - 2026-02-05

### Changed
- **BREAKING**: Migrated from ROS 2 architecture to direct TCP socket communication
- Replaced `create3_lidar_client` (ROS 2) with `lidarclient` (pure Python TCP client)
- Server now uses `rplidar-roboticia` library instead of ROS 2 nodes

### Added
- New `lidarclient` Python package for TCP-based LIDAR data access
- Server TCP script (`servidor_lidar_tcp.py`) for Raspberry Pi 4
- Example scripts:
  - `examples/simplescan.py`: Basic single revolution capture
  - `examples/continuousstream.py`: Continuous streaming with statistics
  - `examples/printscanstub.py`: ROS 2 LaserScan-compatible format
- Automated CI/CD with ruff linting and pytest

### Removed
- ROS 2 dependencies (rclpy, sensor_msgs)
- `src/create3_lidar_client` package (ROS 2 implementation)
- Launch files and ROS 2 configuration

---

## [0.0.1] - 2024-XX-XX

### Added
- Initial repository structure
- Test branch protection
