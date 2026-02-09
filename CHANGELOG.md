# Changelog

All notable changes to this project will be documented in this file.

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
