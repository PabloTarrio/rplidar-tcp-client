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

---

## En Progreso

Actualmente no hay tareas en progreso.

---

## Pendiente

### Documentación y Consolidación

- [ ] Documentar formato de datos recibidos (estructura de las tuplas)
- [ ] Añadir badges al README (Python version, license, etc.)
- [ ] Crear `CONTRIBUTING.md` con guías de contribución

### Optimización del Sistema

- [ ] Manejo robusto de errores:
  - [ ] Reconexión automática del cliente
  - [ ] Timeout configurable
  - [ ] Limpieza del buffer del LIDAR al conectar
- [ ] Configuración flexible:
  - [ ] Archivo de configuración para IP/puerto
  - [ ] Variables de entorno
  - [ ] Argumentos de línea de comandos

### Testing y Calidad

- [ ] Tests unitarios para `LidarClient`
- [ ] Tests de integración servidor-cliente
- [ ] CI/CD: Ejecutar tests automáticamente en PRs
- [ ] Cobertura de código (coverage)

### Integración con Repositorio Existente

- [ ] Evaluar integración con `LIDAR_A1_RPI4` existente
- [ ] Decidir si es independiente o complementario a ROS 2
- [ ] Subir a repositorio organizado

### Funcionalidades Avanzadas

- [ ] Visualización en tiempo real:
  - [ ] Plot 2D de los puntos del LIDAR
  - [ ] Actualización en tiempo real
  - [ ] Librería matplotlib o pygame
- [ ] Guardado de datos:
  - [ ] Exportar a CSV
  - [ ] Exportar a JSON
  - [ ] Timestamp de las revoluciones
- [ ] Filtros y procesamiento:
  - [ ] Filtro por calidad mínima
  - [ ] Filtro por rango de distancia
  - [ ] Filtro por sector angular
- [ ] Mútiples clientes:
  - [ ] Permitir varias conexiones simultáneas
  - [ ] Broadcasting de datos

### Despliegue y Distribución

- [ ] Publicar en PyPI como paquete instalable
- [ ] Crear releases con versiones estables
- [ ] Documentación en Read the Docs
- [ ] Docker container para el servidor

---

## Ideas Futuras (Backlog)

- Compresión de datos para reducir ancho de banda
- Protocolo alternativo: WebSocket para visualización web
- Integración con ROS 2: nodo bridge
- API REST para consultas HTTP
- Soporte para otros modelos de RPLIDAR (A2, A3, S1)

---

## Notas

- **Fecha última actualización:** 2026-02-06
- **Responsable:** Pablo Tarrio
- **Repositorio:** rplidar-tcp-client
- **Hardware:** Raspberry Pi 4 + RPLIDAR A1

---

Este es un proyecto en desarrollo activo. Si tienes sugerencias o quieres añadir funcionalidades, abre un issue o pull request.
