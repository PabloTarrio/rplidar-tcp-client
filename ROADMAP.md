# Roadmap del Proyecto - RPLIDAR A1 TCP Client

Documento vivo que refleja el estado actual y los próximos pasos del proyecto.

---

## Completado

### Fase 1: Configuración Hardware y Software Base

- [x] Instalación Ubuntu 24.04 en Raspberry Pi 4
- [x] Conexión RPLIDAR A1 al puerto USB (`/dev/ttyUSB0`)
- [x] Instalación librería `rplidar-roboticia` en RPi
- [x] Permisos correctos para acceso al puerto serie

### Fase 2: Servidor TCP en Raspberry Pi

- [x] Desarrollo del servidor TCP `servidor_lidar_tcp.py`
- [x] Serialización de revoluciones con pickle
- [x] Envío continuo de múltiples revoluciones
- [x] Manejo de desconexión de clientes
- [x] Código cumpliendo estándares (ruff)

### Fase 3: Librería Cliente Python

- [x] Estructura del proyecto con src-layout
- [x] Clase `LidarClient` con context manager
- [x] Instalación en modo editable (`pip install -e .`)
- [x] Ejemplos funcionales:
  - [x] `simple_scan.py` - Una revolución
  - [x] `continuous_stream.py` - Stream continuo

### Fase 4: Conexión Remota

- [x] Comunicación TCP PC ↔ Raspberry Pi funcionando
- [x] IP configurada (172.16.125.77:5000)
- [x] Transferencia de datos validada

### Fase 5: Documentación

- [x] README.md actualizado con instrucciones completas
- [x] ROADMAP.md creado para seguimiento del proyecto

### Fase 6: Servidor Persistente (Completado 2026-02-06)

- [x] Servidor configurado como servicio systemd
- [x] Arranque automático al iniciar la RPi
- [x] Entorno virtual aislado (cumple PEP 668)
- [x] Documentación completa en `server/README.md`
- [x] Instrucciones de clonación a múltiples RPi
- [x] Logs centralizados con journalctl

### Fase 7: Optimización y Robustez (Completado 2026-02-11)

- [x] **Buffer del LIDAR** (Commit #55)
  - Inicio de escaneo solo cuando hay cliente conectado
  - Detención automática al desconectar cliente
  - Prevención de saturación del buffer
- [x] **Manejo robusto de errores** (Commit #56)
  - Excepciones personalizadas: `LidarConnectionError`, `LidarTimeoutError`, `LidarDataError`
  - Timeout configurable en el constructor del cliente
  - Validación de tamaño de datos (100 bytes - 50KB)
  - Context manager para gestión automática de recursos
- [x] **Reconexión automática del cliente**
  - Método `connect_with_retry()` con reintentos configurables
  - Parámetros `max_retries` y `retry_delay`
  - Logging informativo de cada intento
- [x] **Configuración flexible con config.ini**
  - Archivo `config.ini.example` como plantilla
  - Parser en `src/lidar_client/config.py`
  - Configuración de: host, port, timeout, max_retries, retry_delay
  - Documentación de los 6 LIDAR del laboratorio
  - Protección con `.gitignore`

### Fase 8: Testing y Calidad (Completado 2026-02-11)

- [x] Tests unitarios con pytest (Commit #58)
- [x] Cobertura de código: 88%
- [x] CI/CD con GitHub Actions
- [x] Linting automático con ruff en cada PR
- [x] Formato de código automático

### Fase 9: Visualización y Modo de Escaneo Configurable (Completado 2026-02-12)

#### Visualización en Tiempo Real (PR #64)

- [x] **Script `visualize_realtime.py`**
  - Plot polar 2D con matplotlib
  - Actualización en tiempo real (FuncAnimation)
  - Mapa de colores por distancia (jet_r: rojo cerca, azul lejos)
  - Fondo negro con texto blanco para mejor visualización
  - Estadísticas por revolución en el título
  - Filtrado automático de mediciones inválidas
- [x] **Dependencias opcionales**
  - Grupo `[visualization]` en `pyproject.toml`
  - matplotlib>=3.5.0, numpy>=1.21.0
  - Instalación: `pip install rplidar-tcp-client[visualization]`
- [x] **Documentación visual**
  - Capturas de pantalla en `examples/images/`
  - Guía completa en `examples/README.md`
  - Controles e interpretación del gráfico

#### Modo de Escaneo Configurable (PR #65)

- [x] **Parámetro `scan_mode` en LidarClient**
  - Soporte para modo Standard y Express
  - Valor por defecto: `Express`
  - Validación de valores permitidos
  - Cliente envía modo al servidor vía TCP
- [x] **Implementación en servidor**
  - Recepción del modo desde el cliente
  - Selección dinámica entre `iter_scans()` y `iter_express_scans()`
  - Logging del modo activo
- [x] **Configuración en `config.ini`**
  - Nueva opción `scan_mode = Express`
  - Documentación de valores válidos (Standard/Express)
- [x] **Actualización de todos los ejemplos**
  - `simple_scan.py`, `continuous_stream.py`, `print_scan_stub.py`, `visualize_realtime.py`
  - Todos leen `scan_mode` desde configuración
- [x] **Nuevo script de diagnóstico**
  - `examples/lidar_diagnostics.py` para comparar modos
  - Estadísticas detalladas: puntos, cobertura, densidad, tiempos
  - Manejo correcto de `quality = None` en modo Express
  - Descarta primera revolución (warmup)
- [x] **Documentación actualizada**
  - README.md con explicación de Standard vs Express
  - examples/README.md con tabla comparativa
  - Ejemplos de procesamiento según el modo

### Fase 10: Guardado de Datos (Completado 2026-02-13)

- [x] **Scripts de exportación**
  - `examples/lidar_to_csv.py` - Guardar una o varias revoluciones en CSV
  - `examples/lidar_to_json.py` - Guardar una o varias revoluciones en JSON
  - `examples/streaming_lidar_to_jsonl.py` - Stream continuo a JSONL (línea por revolución)
- [x] **Argumentos de línea de comandos**
  - `--config`: Path al archivo config.ini
  - `--out`: Archivo de salida
  - `--revs`: Número de revoluciones a capturar (omitir = continuo hasta Ctrl+C)
  - `--indent`: Indentación JSON (lidar_to_json.py)
  - `--host`, `--port`, `--mode`: Override de configuración
- [x] **Documentación**
  - Ejemplos de uso en `examples/README.md`
  - Estructura del proyecto actualizada en `README.md`
  - Crear `CONTRIBUTING.md` con guías de contribución

### Fase 11: Filtrado y Procesamiento Avanzado (Completado 2026-02-18)

- [x] **Filtrado por calidad de mediciones**
  - Script `examples/03_avanzado/filter_by_quality.py`
  - Umbral configurable de calidad mínima (default: 8)
  - Histograma visual de distribución de calidades (0-15)
  - Estadísticas de puntos buenos vs malos en tiempo real
  - Compatible con modo Standard (quality 0-15) y Express (quality=None)
  - Funciones: `filter_by_quality()`, `analyze_quality_distribution()`, `print_quality_histogram()`
- [x] **Filtrado por rango de distancia**
  - Script `examples/03_avanzado/filter_by_distance.py`
  - Rango configurable [min_dist, max_dist] en milímetros
  - Clasificación en 3 categorías: en rango, muy cerca, muy lejos
  - Detección automática de punto más cercano (anti-colisión)
  - Alerta visual para obstáculos críticos (< 30 cm)
  - Análisis por zonas de seguridad: CRÍTICA, CERCANA, MEDIA, LEJANA
  - Funciones: `filter_by_distance()`, `find_closest_point()`, `analyze_distance_zones()`
- [x] **Filtrado por sector angular**
  - Script `examples/03_avanzado/filter_by_angle.py`
  - Sector configurable [start, end] en grados (0-360°)
  - Manejo correcto de sectores que cruzan 0° (ej: 350°-10°)
  - Análisis multi-sector (FRENTE, DERECHA, ATRÁS, IZQUIERDA)
  - Detección de punto más cercano dentro del sector
  - Alerta visual para obstáculos frontales cercanos (< 50 cm)
  - Funciones: `normalize_angle()`, `is_angle_in_sector()`, `filter_by_angle()`, `filter_by_multiple_sectors()`
- [x] **Documentación pedagógica completa**
  - Nueva carpeta `examples/03_avanzado/` con 3 scripts
  - 4-5 casos de uso reales documentados por script
  - 5 ejercicios sugeridos para estudiantes por script
  - Comentarios paso a paso en el código
  - Salidas esperadas de ejemplo
  - Notas sobre diferencias Standard vs Express
- [x] **Actualización de documentación**
  - Sección completa "Nivel 3: Avanzado" en `examples/README.md`
  - Estructura de carpetas actualizada en `README.md` principal
  - Sección "Ejemplos por categoría" con 3 niveles
  - Características comunes de ejemplos avanzados documentadas
  - Badges adicionales en README: Release version, Last commit
  - Documentar formato de datos recibidos (estructura de las tuplas) 

  ### Fase 12: Publicación PyPI y v1.0.0 (Completado 2026-02-19)

- [x] **Publicado en PyPI**: `pip install rplidar-tcp-client`
- [x] **Versión 1.0.0** lista para producción académica
- [x] **Badges profesionales** en README (version, downloads, license, Python)
- [x] **Instalación rápida** documentada (1 minuto)

---

## En Progreso

Actualmente no hay tareas en progreso.

---

## Pendiente

### Documentación y Consolidación

### Funcionalidades Avanzadas

- [ ] Mútiples clientes:
  - [ ] Permitir varias conexiones simultáneas
  - [ ] Broadcasting de datos

### Despliegue y Distribución

- [-] Docker container para el servidor

---

## Ideas Futuras (Backlog)

- Compresión de datos para reducir ancho de banda
- Protocolo alternativo: WebSocket para visualización web
- API REST para consultas HTTP
- Soporte para otros modelos de RPLIDAR (A2, A3, S1)

---

## Notas

- **Fecha última actualización:** 2026-02-19
- **Responsable:** Pablo Tarrio
- **Repositorio:** rplidar-tcp-client
- **Hardware:** Raspberry Pi 4 + RPLIDAR A1

---

Este es un proyecto en desarrollo activo. Si tienes sugerencias o quieres añadir funcionalidades, abre un issue o pull request.
