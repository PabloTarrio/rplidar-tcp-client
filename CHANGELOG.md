# Changelog

All notable changes to this project will be documented in this file.

## [0.7.0] - 2026-02-18

### Added

#### Ejemplos Avanzados de Filtrado (PRs #XX, #XX, #XX)
- Nuevo directorio `examples/03_avanzado/` con scripts de filtrado de datos LIDAR
- `filter_by_quality.py`: Filtrado por calidad de mediciones
  - Umbral configurable de calidad mínima (default: 8)
  - Histograma visual de distribución de calidades (0-15)
  - Estadísticas de puntos buenos vs malos en tiempo real
  - Compatible con modo Standard (quality disponible) y Express (quality=None)
  - Función `filter_by_quality()` para clasificar puntos
  - Función `analyze_quality_distribution()` para análisis estadístico
  - Función `print_quality_histogram()` para visualización ASCII
- `filter_by_distance.py`: Filtrado por rango de distancia
  - Rango configurable [min_dist, max_dist] en milímetros
  - Clasificación en 3 categorías: en rango, muy cerca, muy lejos
  - Detección automática de punto más cercano (anti-colisión)
  - Alerta visual para obstáculos críticos (< 30 cm)
  - Análisis por zonas de seguridad cada 10 revoluciones
  - Zonas: CRÍTICA (0-30cm), CERCANA (30cm-1m), MEDIA (1-3m), LEJANA (>3m)
  - Función `filter_by_distance()` para clasificación por rango
  - Función `find_closest_point()` para detección de colisiones
  - Función `analyze_distance_zones()` para análisis multi-zona
- `filter_by_angle.py`: Filtrado por sector angular
  - Sector configurable [start, end] en grados (0-360°)
  - Manejo correcto de sectores que cruzan 0° (ej: 350°-10°)
  - Análisis multi-sector (FRENTE, DERECHA, ATRÁS, IZQUIERDA)
  - Detección de punto más cercano dentro del sector
  - Alerta visual para obstáculos frontales cercanos (< 50 cm)
  - Distribución visual por sectores cada 10 revoluciones
  - Función `normalize_angle()` para normalización angular
  - Función `is_angle_in_sector()` con soporte para wrap-around
  - Función `filter_by_angle()` para filtrado por sector simple
  - Función `filter_by_multiple_sectors()` para análisis multi-sector

#### Documentación Pedagógica Completa
- Todos los scripts avanzados incluyen:
  - Explicación detallada de conceptos (quality, distancia, ángulos)
  - 4-5 casos de uso reales documentados por script
  - 5 ejercicios sugeridos para estudiantes por script
  - Comentarios paso a paso en el código
  - Notas sobre diferencias entre modo Standard y Express
- Actualización completa de `examples/README.md`
  - Nueva sección "Nivel 3: Avanzado" con documentación de los 3 filtros
  - Salidas esperadas de ejemplo para cada script
  - Interpretación de valores y resultados
  - Configuración de parámetros según aplicación
  - Sección "Características comunes de ejemplos avanzados"
- Actualización de `README.md` principal
  - Estructura de carpetas actualizada con `03_avanzado/`
  - Sección "Ejemplos por categoría" con Nivel 3 completo
  - Referencias cruzadas mejoradas entre documentación

### Changed
- Código cumple con ruff (límite de 88 caracteres por línea)
- Formato consistente en todos los ejemplos avanzados




## [0.6.0] - 2026-02-13

### Added
- Scripts de guardado de datos del LIDAR
  - `examples/lidar_to_csv.py`: Guardar una o varias revoluciones en formato CSV
  - `examples/lidar_to_json.py`: Guardar una o varias revoluciones en formato JSON
  - `examples/streaming_lidar_to_jsonl.py`: Stream continuo a JSONL (una revolución por línea)
- Argumentos de línea de comandos para personalización
  - `--config`: Path al archivo de configuración
  - `--out`: Archivo de salida
  - `--revs`: Número de revoluciones a capturar (omitir para modo continuo hasta Ctrl+C)
  - `--indent`: Indentación del JSON (solo `lidar_to_json.py`)
  - `--host`, `--port`, `--mode`: Override de parámetros de configuración
- Documentación de los nuevos ejemplos
  - Sección completa en `examples/README.md` con casos de uso
  - Estructura del proyecto actualizada en `README.md`

## [0.5.0] - 2026-02-12

### Added

#### Visualización en Tiempo Real (PR #64)
- Nuevo script `examples/visualize_realtime.py`
  - Plot polar 2D con matplotlib y animación en tiempo real (FuncAnimation)
  - Mapa de colores por distancia (jet_r: rojo cerca, azul lejos)
  - Fondo negro con texto blanco para mejor visualización nocturna
  - Estadísticas actualizadas por revolución en el título
  - Filtrado automático de mediciones inválidas (distance = 0)
  - Orientación correcta: 0° arriba, rotación horaria
- Dependencias opcionales `[visualization]` en `pyproject.toml`
  - matplotlib>=3.5.0
  - numpy>=1.21.0
  - Instalación: `pip install rplidar-tcp-client[visualization]`
- Documentación visual completa
  - Capturas de pantalla en `examples/images/`
  - Guía detallada con controles e interpretación en `examples/README.md`

#### Modo de Escaneo Configurable (PR #65)
- Soporte para seleccionar entre modo **Standard** y **Express**
  - Nuevo parámetro `scan_mode` en `LidarClient` (default: `'Express'`)
  - Validación de valores permitidos: `'Standard'` o `'Express'`
  - Cliente envía el modo seleccionado al servidor vía TCP
- Implementación dinámica en servidor (`servidor_lidar_tcp.py`)
  - Recepción del modo de escaneo desde cada cliente
  - Selección automática entre `iter_scans()` (Standard) y `iter_express_scans()` (Express)
  - Logging del modo activo para debugging
- Parámetro `scan_mode` en `config.ini.example`
  - Nueva opción con documentación de valores válidos
  - Explicación de diferencias entre Standard y Express
- Nuevo script de diagnóstico: `examples/lidar_diagnostics.py`
  - Herramienta para analizar rendimiento del LIDAR
  - Captura 3 revoluciones con estadísticas detalladas
  - Muestra: puntos, cobertura angular, densidad, frecuencia, tiempos
  - Manejo correcto de `quality = None` en modo Express
  - Descarta automáticamente primera revolución (warmup)

### Changed
- Todos los ejemplos actualizados para pasar `scan_mode` desde configuración
  - `simple_scan.py`, `continuous_stream.py`, `print_scan_stub.py`, `visualize_realtime.py`
- Documentación actualizada con co

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

-

## [0.0.1] - 2024-XX-XX

### Added
- Initial repository structure
- Test branch protection
