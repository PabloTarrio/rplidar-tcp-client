# Ejemplos de uso de lidarclient

Esta carpeta contiene ejemplos prácticos de cómo usar la librería `lidarclient` para conectarse al servidor LIDAR TCP en la Raspberry Pi.

## Requisitos previos

Antes de ejecutar cualquier ejemplo:

### 1. Servidor TCP corriendo en la Raspberry Pi

```bash
# En la Raspberry Pi, verificar que el servidor está corriendo
sudo systemctl status rplidar-server.service

# Si no está corriendo, arrancarlo
sudo systemctl start rplidar-server.service
```

### 2. Libreria instalada en tu PC

```bash
# Desde la raíz del proyecto
pip install -e .
```

### 3. Configurar tu LIDAR

IMPORTANTE: Todos los ejemplos leen la configuración desde `config.ini`
```bash
# Copiar plantilla
cp config.ini.example config.ini
# Editar con tu IP asignada
nano config.ini
```

Cambia la lines `host` por la IP de tu LIDAR asignado

```text
[lidar]
host = 192.168.1.103  # Cambia por tu LIDAR
port = 5000
timeout = 5.0
max_retries = 3
retry_delay = 2.0
scan_mode = Express   # Standard o Express
```

LIDAR disponibles en el Laboratorio:

* LIDAR 1: 192.168.1.101
* LIDAR 2: 192.168.1.102
* LIDAR 3: 192.168.1.103
* LIDAR 4: 192.168.1.104
* LIDAR 5: 192.168.1.105
* LIDAR 6: 192.168.1.106

## Ejemplos disponibles

Los ejemplos están organizador en carpetas según su nivel de dificultad para facilitar el aprendizaje progresivo.

---

### Nivel 1: Básico (carpeta `01_basico/`)

Ejemplos fundamentales para familiarizarse con el sensor y la librería.

#### 1. `simple_scan.py` - Tu primera medición LIDAR

**Qué hace:**

Captura una o varias revoluciones del LIDAR y muestra estadísticas básicas (puntos totales, distancias min/max, promedio, objeto más cercano).

**Ideal para:**

- Primeras pruebas de conexión
- Verificar que el sistema funciona correctamente
- Entender el flujo básico: conectar -> capturar -> analizar -> desconectar

**Uso:**

```bash
python examples/01_basico/simple_scan.py
```

**Salida esperada:**

```text
Cargando configuracion desde config.ini...
Configuracion cargada correctamente
  - Servidor: 192.168.1.103:5000
  - Modo: Express
  
Conectando al servidor LIDAR...
Conectado exitosamente a 192.168.1.103:5000

Solicitando revolucion...

Revolucion completa recibida
Total de puntos: 346
Puntos validos: 346 (100.0%)

Estadisticas de distancia:
  Minima: 357.0 mm (0.36 m)
  Maxima: 5221.0 mm (5.22 m)
  Promedio: 1234.5 mm (1.23 m)
  
Objeto mas cercano:
  Distancia: 357.0 mm (0.36 m)
  Angulo: 187.8
```

**Conceptos que aprendes:**

- Como cargar la configuración desde config.ini
- Como conectar al servidor LIDAR con reinitentos automáticos
- Que es una "revolución" (giro completo de 360)
- Estructura básica de los datos: lista de tuplas (quality, angle, distance)
- Como filtrar mediciones básicas (distance > 0)

---

#### 2. `understanding_data.py` - Entender el formato de datos

**Que hace:**
Analiza en profundidad el formato de datos del LIDAR, explicando cada campo (quality, angle, distance) y sus rangos de valores.

**Ideal para:**

* Comprender la diferencia entre modo Standard y Express

* Entender que significa cada campo de la tupla

* Aprender a identificar mediciones invalidas

* Ver ejemplos de como procesar los datos

**Uso:**

```bash
python examples/01_basico/understanding_data.py
```

**Conceptos que aprendes:**

* Diferencia entre modo Standard (con quality) y Express (sin quality)

* Rangos de valores: quality (0-15), angle (0-360), distance (0-12000mm)

* Por que algunos puntos tienen distance=0 (fuera de rango)

* Diferentes formas de acceder a los datos en Python

* Como calcular cobertura angular y densidad de puntos

---

#### 3. `continuous_stream.py` - Stream continuo con estadísticas

**Qué hace:**
Captura revoluciones del LIDAR continuamente en bucle infinito y muestra estadísticas en tiempo real (puntos totales, válidos, distancias min/max/media) hasta presionar Ctrl+C.

**Ideal para:**
- Monitoreo continuo del entorno en tiempo real
- Detectar cambios dinámicos en el espacio escaneado
- Verificar estabilidad del sistema a largo plazo
- Aplicaciones que necesitan datos en streaming (navegación, SLAM)
- Logging de estadísticas para análisis posterior

**Uso:**
```bash
python examples/01_basico/continuous_stream.py
```
**Salida esperada:**

```text
Conectado al servidor LIDAR
Servidor: 192.168.1.103:5000
Modo: Express
Presiona Ctrl+C para detener

Rev #  1: Puntos=346 Validos=346 Dist.Media= 1234.5mm Min= 357.0mm Max= 5221.0mm
Rev #  2: Puntos=347 Validos=345 Dist.Media= 1238.1mm Min= 358.5mm Max= 5218.3mm
Rev #  3: Puntos=346 Validos=346 Dist.Media= 1230.7mm Min= 362.1mm Max= 5215.8mm
```

DDetener: Presiona `Ctrl+C` para finalizar limpiamente

**Conceptos que aprendes:**

* Bucle infinito con while True para captura continua

* Manejo de interrupciones con KeyboardInterrupt (Ctrl+C)

* Calcular estadísticas en tiempo real de forma eficiente

* Uso de time.sleep() para control de frecuencia de captura

* Formato de salida compacto para monitoreo en una línea

* Bloque finally para desconexión limpia garantizada

**Características:**

- Contador de revoluciones procesadas

- Estadísticas actualizadas cada revolución

- Desconexión automática limpia al interrumpir

- Pausa de 100ms entre revoluciones (configurable)

- Manejo robusto de revoluciones sin puntos válidos

**Aplicaciones prácticas:**

* Base para sistemas de navegación autónoma

* Logging continuo de datos del entorno

* Monitoreo de estabilidad del LIDAR

* Detección de cambios (objetos que entran/salen del campo)

---

#### 4. `print_scan_stub.py` - Formato compatible ROS 2 LaserScan

**Qué hace:**
Muestra estadísticas de escaneo en formato similar a `sensor_msgs/LaserScan` de ROS 2, con distancias en metros y ángulos en radianes, facilitando la migración desde/hacia ROS.

**Ideal para:**
- Migrar código existente de ROS 2 a TCP sin instalar ROS
- Usuarios familiarizados con el ecosistema ROS 2
- Debugging de cobertura angular y rangos de medición
- Aplicaciones que esperan formato LaserScan estándar
- Comparar datos con rplidar_ros oficial

**Uso:**
```bash
python examples/01_basico/print_scan_stub.py
```
**Salida esperada:**

```text
Conectado al servidor LIDAR
Servidor: 192.168.1.103:5000
Mostrando estadísticas de escaneo (formato LaserScan)
Presiona Ctrl+C para detener

ranges=346 finite=346 min=0.357m max=5.221m angle_min=0.009 rad angle_max=6.274 rad
ranges=347 finite=345 min=0.358m max=5.218m angle_min=0.008 rad angle_max=6.275 rad
ranges=346 finite=346 min=0.362m max=5.216m angle_min=0.009 rad angle_max=6.273 rad
```

Detener: Presiona `Ctrl+C` para finalizar

**Conceptos que aprendes:**

* Formato del mensaje sensor_msgs/LaserScan de ROS 2

* Conversión de milímetros a metros (estándar en robótica)

* Conversión de grados a radianes (estándar matemático)

* Filtrado de mediciones finitas vs infinitas con math.isfinite()

* Patrón callback para procesamiento de datos

* Compatibilidad entre sistemas sin dependencias ROS

**Campos mostrados (equivalentes a LaserScan):**

* ranges: Número total de mediciones en el scan

* finite: Cuántas mediciones son válidas (distance > 0)

* min/max: Rango de distancias válidas en metros

* angle_min/angle_max: Cobertura angular en radianes

>**Nota importante:** Este script NO requiere ROS 2 instalado. Solo simula el formato de datos para facilitar compatibilidad y migración.

**Comparación con ROS 2:**

| Campo ROS LaserScan | Equivalente en este script    |
| ------------------- | ----------------------------- |
| ranges[]            | Array de distancias (mm/1000) |
| angle_min           | math.radians(min(angles))     |
| angle_max           | math.radians(max(angles))     |
| range_min/range_max | 0.15m / 12.0m (RPLIDAR A1)    |
| intensities[]       | quality (si disponible)       |

**Aplicaciones prácticas:**

* Prototipado rápido sin instalar ROS 2

* Validación de datos antes de integrar con ROS

* Educación: entender formato LaserScan sin complejidad ROS

---

---

### Nivel 2: Intermedio (carpeta `02_intermedio/`)

Ejemplos de análisis, visualización y exportación de datos.

#### 5. `visualize_realtime.py` - Visualización gráfica en tiempo real

**Qué hace:**
Muestra los datos del LIDAR en un gráfico polar 2D animado que se actualiza en tiempo real, permitiendo visualizar intuitivamente cómo "ve" el sensor su entorno.

**Ideal para:**
- Visualización intuitiva del entorno escaneado
- Debugging visual de cobertura y alcance del LIDAR
- Demostraciones y presentaciones educativas
- Detectar problemas de hardware visualmente
- Entender cómo "ve" el LIDAR (educación, formación)
- Verificar campo de visión antes de experimentos

**Requisitos adicionales:**
```bash
pip install matplotlib numpy

# O si instalaste con dependencias opcionales:
pip install -e .[visualization]
```

**Uso:**
```bash
python examples/02_intermedio/visualize_realtime.py
```
**Salida esperada:**

Se abrirá una ventana gráfica mostrando:

* Gráfico polar circular (el LIDAR está en el centro)

* Puntos dispersos representando objetos detectados

* Mapa de colores por distancia: rojo=cerca, azul=lejos

* Título actualizado con estadísticas por revolución

* Rango radial: 0 - 6000 mm (0 - 6 metros)

* Orientación: 0° arriba (Norte), rotación horaria

**Características:**

* Actualización en tiempo real cada 100ms (~10 FPS)

* Gradiente de color por distancia (colormap jet_r)

* Filtrado automático de mediciones inválidas (distance=0)

* Fondo negro para mejor contraste visual

* Contador de revoluciones procesadas

* Estadísticas en tiempo real: puntos válidos, distancias min/max

**Interpretación del gráfico:**

* Centro: Posición del LIDAR

* Ángulo: Dirección de la medición (0° arriba, sentido horario)

* Distancia radial: Distancia al objeto detectado

* Color rojo: Objetos cercanos (alerta, importante)

* Color azul: Objetos lejanos (menos críticos)

* Ausencia de puntos: Sin objetos detectados en esa dirección

****ntroles:

* Cerrar ventana o presionar Ctrl+C para detener

>**Nota:** Si ejecutas por SSH sin display gráfico, necesitarás X11 forwarding (ssh -X) o ejecutar localmente.

**Conceptos que aprendes:**

* Visualización de datos en coordenadas polares

* Animación en tiempo real con matplotlib.FuncAnimation

* Conversión de grados a radianes con numpy.deg2rad()

* Mapas de colores para representar magnitudes (distancia)

* Configuración de gráficos con proyección polar

* Manejo de señales (SIGINT) para cierre limpio

* Aplicaciones prácticas:

* Verificación rápida de funcionamiento del LIDAR

* Debugging de montaje y orientación del sensor

* Detección visual de obstáculos en desarrollo

* Demostraciones en vivo para educación

---

#### 6. `lidar_diagnostics.py` - Comparación de modos de escaneo

**Qué hace:**
Herramienta de diagnóstico que analiza el rendimiento del LIDAR capturando 3 revoluciones y mostrando estadísticas detalladas del modo de escaneo configurado (Standard o Express).

**Ideal para:**
- Comparar rendimiento entre modo Standard y Express
- Verificar que el LIDAR funciona correctamente
- Diagnosticar problemas de cobertura o densidad
- Validar configuración antes de usar en producción
- Educación: entender especificaciones técnicas del sensor
- Detectar degradación de rendimiento con el tiempo

**Uso:**
```bash
python examples/02_intermedio/lidar_diagnostics.py
```

**Salida esperada:**

```text
   COMPARACIÓN DE MODOS DE ESCANEO RPLIDAR A1

Conectando a 192.168.1.103:5000
Conectado

Descartando primera revolución (warmup)...
Warmup completado

Capturando 3 revoluciones para análisis...

============================================================
   Revolución #1 (Tiempo: 0.128s)
============================================================
 Total de puntos:    346
 Puntos válidos:     346 (100.0%)
 Calidad promedio:   No disponible (modo Express)
 Cobertura angular:  359.3°
 Distancia mínima:   357.0 mm
 Distancia máxima:   5221.0 mm
 Densidad:           0.96 puntos/grado
============================================================

[... revoluciones 2 y 3 ...]

============================================================
  PROMEDIOS DE 3 REVOLUCIONES
============================================================
  Puntos promedio:      347.0
  Válidos promedio:     346.7
  Tiempo promedio:      0.126s
  Frecuencia:           7.94 Hz
============================================================
```
**Características:**

* Descarta automáticamente la primera revolución (warmup del sistema)

* Captura 3 revoluciones para análisis estadístico confiable

* Muestra estadísticas detalladas por revolución y promedios

* Calcula frecuencia real de captura (revoluciones/segundo)

* Maneja correctamente ambos modos de escaneo

* Calcula densidad de puntos (puntos por grado de rotación)

**Conceptos que aprendes:**

* Por qué la primera revolución siempre tarda más (~1s de warmup)

* Diferencias prácticas entre Standard y Express

* Cómo medir rendimiento del LIDAR (frecuencia, densidad)

* Calcular cobertura angular (debería estar cerca de 360°)

* Promediar múltiples mediciones para mayor precisión

* Interpretar especificaciones técnicas del sensor

**Interpretación de resultados:**

* Puntos/revolución: Express ~720, Standard ~360

* Frecuencia: Típicamente 5-10 Hz (revoluciones/segundo)

* Cobertura angular: Debería estar cerca de 360° (revolución completa)

* Densidad: Express tiene ~2x densidad que Standard

* Calidad: Solo disponible en modo Standard (0-15)

>**Nota sobre warmup:** La primera revolución tras conectar siempre tarda más (~1 segundo) debido a:
>
>* Sincronización inicial servidor-LIDAR
>* Estabilización del motor del LIDAR
>* Llenado de buffers de red
>
>Este script la descarta automáticamente para mediciones representativas.   

**RPLIDAR A1 - Especificaciones típicas:**

* Standard Scan: ~360 puntos/revolución, incluye datos de calidad (0-15)

* Express Scan: ~720 puntos/revolución, sin datos de calidad

* Velocidad: 5-10 Hz (revoluciones por segundo)

* Rango: 0.15m - 12m

* Precisión: <1% del rango medido

**Comparación de modos:**

| Característica     | Standard             | Express           |
| ------------------ | -------------------- | ----------------- |
| Puntos/revolución  | ~360                 | ~720              |
| Calidad disponible | ✅ Sí (0-15)          | ❌ No (None)       |
| Densidad angular   | ~1 pto/grado         | ~2 ptos/grado     |
| Uso recomendado    | Filtrado por calidad | Máxima resolución |

**Validación después de instalar/configurar LIDAR**

* Comparar rendimiento entre diferentes PCs/redes

* Detectar problemas antes de usarlo en producción

* Documentar especificaciones reales de tu setup

---

#### 7. `lidar_to_csv.py` - Guardar revoluciones en CSV

**Qué hace:**
Captura una o varias revoluciones del LIDAR y las guarda en un archivo CSV para análisis posterior con herramientas como Excel, LibreOffice Calc o Python pandas.

**Ideal para:**
- Crear datasets para análisis estadístico offline
- Exportar datos a herramientas externas (Excel, MATLAB, R)
- Documentar mediciones de experimentos
- Compartir datos en formato tabular universal
- Generar reportes de mediciones
- Debugging: comparar mediciones en diferentes momentos

**Uso:**
```bash
# Capturar 3 revoluciones (default)
python examples/02_intermedio/lidar_to_csv.py --revs 3 --out lidar_scans.csv

# Capturar 10 revoluciones en carpeta específica
python examples/02_intermedio/lidar_to_csv.py --revs 10 --out datos/experimento1.csv
```

**Salida Esperada:**

```text
Conectando a 192.168.1.103:5000
Modo de escaneo: Express
Capturando 3 revoluciones...

  Rev 1/3: 346 puntos
  Rev 2/3: 347 puntos
  Rev 3/3: 346 puntos

CSV guardado exitosamente en: /ruta/completa/lidar_scans.csv
Total de filas (puntos): 1039
Total de revoluciones: 3

Para analizar en pandas:
  import pandas as pd
  df = pd.read_csv('lidar_scans.csv')
  df['quality'] = pd.to_numeric(df['quality'], errors='coerce')
  print(df.groupby('rev_index')['distance_mm'].describe())
```

**Formato del CSV**

```text
timestamp_iso,scan_mode,rev_index,point_index,angle_deg,distance_mm,quality
2026-02-13T16:30:45.123456+00:00,Express,0,0,0.50,1250.3,
2026-02-13T16:30:45.123456+00:00,Express,0,1,1.25,1248.7,
2026-02-13T16:30:45.123456+00:00,Express,0,2,1.98,1251.2,
...
2026-02-13T16:30:45.234567+00:00,Express,1,0,0.48,1251.1,
```
**Columnas del CSV:**

* timestamp_iso: Marca temporal ISO 8601 (se repite para toda la revolución)

* scan_mode: Modo de escaneo (Standard o Express)

* rev_index: Índice de la revolución (0, 1, 2, ...)

* point_index: Índice del punto dentro de la revolución

* angle_deg: Ángulo en grados (0.0 - 360.0)

* distance_mm: Distancia en milímetros (0 = inválida)

* quality: Calidad 0-15 (Standard) o vacío (Express)

**Conceptos que aprendes:**

* Exportar datos LIDAR a formato tabular

* Uso de csv.DictWriter para escritura estructurada

* Manejo de argumentos CLI con argparse

* Creación automática de directorios con pathlib

* Timestamps ISO 8601 para marcas temporales

* Manejo de valores None en CSV (modo Express)

**Análisis con pandas:**

```python
import pandas as pd
import matplotlib.pyplot as plt

# Cargar CSV
df = pd.read_csv('lidar_scans.csv')

# Convertir quality a numérico (None -> NaN)
df['quality'] = pd.to_numeric(df['quality'], errors='coerce')

# Filtrar puntos válidos
valid = df[df['distance_mm'] > 0]

# Estadísticas por revolución
stats = valid.groupby('rev_index')['distance_mm'].agg(['mean', 'min', 'max', 'count'])
print(stats)

# Graficar distribución de distancias
valid['distance_mm'].hist(bins=50)
plt.xlabel('Distancia (mm)')
plt.ylabel('Frecuencia')
plt.title('Distribución de Distancias')
plt.show()

# Graficar polar (ángulo vs distancia)
rev0 = valid[valid['rev_index'] == 0]
plt.polar(np.deg2rad(rev0['angle_deg']), rev0['distance_mm'], 'o', markersize=2)
plt.show()
```

**Aplicaciones prácticas:**

* Crear datasets para machine learning

* Comparar mediciones antes/después de calibración

* Análisis estadístico de entornos

* Generar reportes automáticos en Excel

* Validar algoritmos de procesamiento

---

#### 8. `lidar_to_json.py` - Guardar revoluciones en JSON

**Qué hace:**
Captura una o varias revoluciones del LIDAR y las guarda en formato JSON estructurado con metadatos, útil para integración con aplicaciones web, APIs REST o cualquier sistema que consuma JSON.

**Ideal para:**
- Integración con APIs REST y servicios web
- Intercambio de datos con aplicaciones JavaScript/TypeScript
- Configuración y snapshots de mediciones puntuales
- Documentación estructurada de experimentos
- Procesamiento con `jq` (herramienta CLI para JSON)
- Carga en bases de datos NoSQL (MongoDB, CouchDB)

**Uso:**
```bash
# JSON indentado (legible)
python examples/02_intermedio/lidar_to_json.py --revs 3 --out lidar_scans.json --indent 2

# JSON compacto (mínimo tamaño)
python examples/02_intermedio/lidar_to_json.py --revs 5 --out datos.json --indent 0
```

**Argumentos:**

* --revs N: Número de revoluciones a capturar (default: 3)

* --out PATH: Ruta del archivo JSON de salida (default: lidar_scans.json)

* --indent N: Espacios de indentación (default: 2, usa 0 para compacto)

**Salida esperada:**

```text
Conectado a 192.168.1.103:5000
Modo de escaneo: Express
Capturando 3 revoluciones...

  Rev 1/3: 346 puntos
  Rev 2/3: 347 puntos
  Rev 3/3: 346 puntos

JSON guardado exitosamente en: /ruta/completa/lidar_scans.json
Total de revoluciones: 3
Total de puntos: 1039
Tamaño del archivo: 87.45 KB

Para cargar en Python:
  import json
  with open('lidar_scans.json') as f:
      data = json.load(f)
  print(data['meta'])
  print(len(data['revolutions']))

Para inspeccionar con jq (CLI):
  jq '.meta' lidar_scans.json
  jq '.revolutions.points | length' lidar_scans.json
```
**Estructura del JSON:**
```json
{
  "meta": {
    "timestamp_iso": "2026-02-13T16:30:00.123456+00:00",
    "scan_mode": "Express",
    "host": "192.168.1.103",
    "port": 5000
  },
  "revolutions": [
    {
      "rev_index": 0,
      "timestamp_iso": "2026-02-13T16:30:01.234567+00:00",
      "points": [
        {
          "point_index": 0,
          "angle_deg": 0.5,
          "distance_mm": 1250,
          "quality": null
        },
        ...
      ]
    },
    ...
  ]
}
```
**Conceptos que aprendes:**

* Exportar datos LIDAR a formato JSON jerárquico

* Estructura de datos con metadatos + revoluciones + puntos

* Manejo de valores null en JSON (quality=None en Express)

* Control de formato JSON (compacto vs indentado)

* Diferencias entre JSON y JSONL (JSON Lines)

* Construcción en memoria vs escritura incremental

**Ventajas vs CSV:**

* Jerárquico: revoluciones y puntos claramente agrupados

* Metadatos: información de sesión incluida

* Tipos nativos: null, bool, números (no strings)

* Legible: indentación opcional para humanos

**Desventajas vs CSV:**

* Más verboso (mayor tamaño de archivo)

* Menos compatible con herramientas de análisis tabular (Excel, pandas)

* Más lento de parsear para datasets grandes

* Requiere más memoria (se construye todo antes de escribir)

**Procesamiento con jq(CLI)**
```bash
# Ver metadatos
jq '.meta' lidar_scans.json

# Contar revoluciones
jq '.revolutions | length' lidar_scans.json

# Ver primera revolución
jq '.revolutions' lidar_scans.json

# Extraer todas las distancias
jq '.revolutions[].points[].distance_mm' lidar_scans.json

# Calcular distancia promedio
jq '[.revolutions[].points[].distance_mm] | add / length' lidar_scans.json

# Filtrar solo puntos válidos (distance > 0)
jq '.revolutions[].points[] | select(.distance_mm > 0)' lidar_scans.json
```

**Análisis con Python**
```python
import json

# Cargar JSON
with open('lidar_scans.json') as f:
    data = json.load(f)

# Acceder a metadatos
print(f"Modo: {data['meta']['scan_mode']}")
print(f"Host: {data['meta']['host']}")

# Iterar revoluciones
for rev in data['revolutions']:
    valid = [p for p in rev['points'] if p['distance_mm'] > 0]
    print(f"Rev {rev['rev_index']}: {len(valid)} puntos válidos")

# Extraer todas las distancias
all_distances = [
    p['distance_mm']
    for rev in data['revolutions']
    for p in rev['points']
    if p['distance_mm'] > 0
]
print(f"Distancia promedio: {sum(all_distances) / len(all_distances):.1f}mm")
```

**Aplicaciones prácticas:**

* Integración con frontend web (JavaScript/React/Vue)

* Envío a APIs REST como payload

* Almacenamiento en MongoDB u otras bases NoSQL

* Configuración de experimentos reproducibles

* Intercambio de datos entre lenguajes de programación

---

#### 9. streaming_lidar_to_jsonl.py - Stream continuo a JSONL

**Qué hace:**

Captura revoluciones del LIDAR continuamente y las guarda en formato JSONL (JSON Lines: una revolución por línea), ideal para logging de sesiones largas sin cargar todo en memoria.

**Ideal para:**

- Logging continuo de datos LIDAR en producción
- Generar datasets grandes sin consumir memoria RAM
- Procesamiento posterior línea a línea (streaming analytics)
- Monitoreo de largo plazo (horas/días)
- Integración con pipelines de datos (Kafka, Spark Streaming)
- Debugging de comportamiento temporal del LIDAR

**Uso:**

```bash
# Stream finito: capturar 100 revoluciones
python examples/02_intermedio/streaming_lidar_to_jsonl.py --config config.ini --out stream.jsonl --revs 100

# Stream infinito hasta Ctrl+C
python examples/02_intermedio/streaming_lidar_to_jsonl.py --config config.ini --out stream.jsonl

# Con overrides de configuración
python examples/02_intermedio/streaming_li
```

**Argumentos:**

* --config PATH: Ruta a config.ini (default: config.ini)

* --out PATH: Archivo JSONL de salida (REQUERIDO)

* --revs N: Número de revoluciones (si se omite, corre hasta Ctrl+C)

* --host IP: Override de host del config.ini

* --port N: Override de port del config.ini

* --mode MODE: Override de scan_mode del config.ini

**Salida esperada:**

```text
Conectando a 192.168.1.103:5000...
Conectado a 192.168.1.103:5000
Modo enviado: EXPRESS

[capturando revoluciones silenciosamente...]

^C
Interrumpido por Ctrl+C, cerrando...
OK: escritas 247 revoluciones en stream.jsonl

Para procesar el JSONL:
  # Contar revoluciones
  wc -l stream.jsonl
  
  # Ver primera revolución
  head -1 stream.jsonl | jq
  
  # Extraer distancias promedio
  cat stream.jsonl | jq '.points[].distance_mm' | awk '{sum+=$1; n++} END {print sum/n}'
```

**Formato JSONL vs JSON:**

JSON estándar (todo en un archivo):

```json
{"revolutions": [rev1, rev2, rev3]}
```
x Todo en memoria, no procesable has el final

JSONL (una linea por revolución):

```json
{"rev_index":0,"points":[...]}
{"rev_index":1,"points":[...]}
{"rev_index":2,"points":[...]}
```

Procesable línea a línea, memoria constante

**Ventajas de JSONL:**

* Escritura incremental: no espera al final

* Memoria constante: no acumula datos en RAM

* Procesable línea a línea: cat file.jsonl | jq

* Resistente a interrupciones: datos ya escritos se preservan

* Ideal para streams infinitos o muy largos

**Desventajas de JSONL:**

* No es JSON válido (no parseable con json.load() directo)

* Requiere procesamiento línea por línea

* Sin estructura global de metadatos al inicio

**Conceptos que aprendes:**

* Diferencia entre JSON (archivo completo) y JSONL (stream)

* Comunicación TCP directa con sockets Python (sin LidarClient)

* Protocolo de comunicación del servidor LIDAR (pickle sobre TCP)

* Escritura incremental con flush() para persistencia inmediata

* Override de configuración vía argumentos CLI

* Procesamiento de datos en tiempo real sin buffers grandes

**Diferencia con otros ejemplos:**

Este script NO usa LidarClient, implementa comunicación TCP directa para mostrar el protocolo de bajo nivel del servidor LIDAR. Más control pero más complejidad.

**Protocolo del servidor LIDAR:**

* 1. Conectar socket TCP al servidor
* 2. Enviar modo de escaneo: "STANDARD" o "EXPRESS" (UTF-8)
* 3. Recibir frames en bucle:

  * 4 bytes: tamaño del payload (big-endian uint32)
  * N bytes: payload serializado con pickle
  * Deserializar → lista de tuplas (quality, angle, distance)

**Procesamiento en tiempo real:**

```bash
# Terminal 1: Capturar datos
python streaming_lidar_to_jsonl.py --config config.ini --out stream.jsonl

# Terminal 2: Ver datos mientras se escriben
tail -f stream.jsonl | jq -c '.rev_index, (.points | length)'
```

**Análisis linea a linea con Python:**

```python
import json

# Procesar JSONL línea por línea (no carga todo en memoria)
with open('stream.jsonl') as f:
    for line in f:
        rev = json.loads(line)
        valid = [p for p in rev['points'] if p['distance_mm'] > 0]
        print(f"Rev {rev['rev_index']}: {len(valid)} puntos válidos")
```
**Comandos útiles con jq:**

```bash
# Contar total de revoluciones
wc -l stream.jsonl

# Ver revolución específica (la 5)
sed -n '5p' stream.jsonl | jq

# Extraer solo distancias de todas las revoluciones
cat stream.jsonl | jq -r '.points[].distance_mm'

# Revoluciones con más de 300 puntos válidos
cat stream.jsonl | jq -c 'select((.points | map(select(.distance_mm > 0)) | length) > 300)'

# Calcular distancia promedio global
cat stream.jsonl | jq '.points[].distance_mm' | awk '{sum+=$1; n++} END {print sum/n}'
```

**Aplicaciones prácticas:**

* Logging 24/7 de datos LIDAR en robots de producción

* Generación de datasets masivos para ML

* Integración con sistemas de mensajería (Kafka, RabbitMQ)

* Análisis temporal de cambios en el entorno

* Monitoreo de estabilidad a largo plazo

>**Nota importante:** Este script usa flush() después de cada línea para garantizar que los >datos se escriban inmediatamente al disco. Sin esto, los datos quedarían >en buffer y se perderían si el programa se interrumpe.

## Formato de datos del LIDAR

Todas las revoluciones se devuelven como una lista de tuplas:

```python
scan = client.get_scan()
# scan = [(quality, angle, distance),(quality, angle, distance), ...]
```

* quality (int | None): Confianza de la medición de
    * Modo Standard: 0-15 (donde 15 es la máxima calidad) 
    * Modo Express: None (no disponible en este modo)
* angle (float): Ángulo en grados (0-360º)
* distance (float): Distancia en milímetros (0 = sin medición válida)

Diferencias entre los modos de escaneo:

| **Caracteristica**     |  **Standard**  |  **Express**    |
|:----------------------:|:--------------:|:---------------:|
| Puntos/revolucion      |  ~360          |  ~720           |
| Datos de calidad       |  Si (0-15)     |  No (None)      |
| Densidad               |  Normal        |  Alta           |
| Velocidad              |  Normal        |  Más rápido     |


### Ejemplo de procesamiento.

```python
# Filtrar solo mediciones válidas
for quality, angle, distance in scan:
    if distance > 0:  # Filtrar mediciones válidas
        print(f"Objeto detectado a {angle:.1f}° y {distance:.1f} mm")

# Procesar calidad (solo en modo Standard)
for quality, angle, distance in scan:
    if distance > 0:
        if quality is not None:  # Modo Standard
            print(f"Calidad: {quality}/15")
        else:  # Modo Express
            print("Calidad: No disponible")
```
## Reconexión automática
Todos los ejemplos usan `connect_with_retry()` que reintenta la conexión automáticamente según la configuración en `config.ini`:

```text
max_retries = 3    # Número de reintentos
retry_delay = 2.0  # Segundos entre reintentos
```

Si el servidor no está disponible, verás:

```text
Conectando a 192.168.1.103:5000...
Falló: Conexión rechazada por 192.168.1.103:5000. Verifica que el servidor esté corriendo.
Esperando 2.0 segundos antes de reintentar...
[Intento 2/4] Reintentando conexión a 192.168.1.103:5000...
...
```

## Solución de problemas

### Error: `No se encontró el archivo 'config.ini'`

Causa: No has creado el archivo de configuración

Solución:
```bash
cp config.ini.example config.ini
nano config.ini  # Edita la IP de tu LIDAR
```

### Error: `Connection refused`

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

### Error: `Timeout esperando datos del servidor`

Causa: el servidor está muy lento o sobrecargado

Solución: Aumenta el `timeout` en `config.ini`:

```text
timeout = 10.0
```

### Revoluciones con poco puntos válidos

Causa: Normal si el LIDAR apunta a una zona vacía o muy lejana

Rango de medición: EL RPLIDAR A1 tiene un rango típico de 0.15 - 12 metros.

### El servidor se desconecta inesperadamente

Solución:

* Verificar logs del servidor: sudo journalctl -u rplidar-server.service -f

* Verificar conexión USB del LIDAR en la RPi: ls -la /dev/ttyUSB0

* Reiniciar servidor: sudo systemctl restart rplidar-server.service

## Próximos pasos

Una vez que domines estos ejemplos puedes:

* Crear tus propias aplicaciones de procesamiento de datos LIDAR

* Implementar detección de obstáculos

* Guardar datos en CSV/JSON para análisis offline

* Visualizar el escaneo en tiempo real con matplotlib

* Integrar con sistemas de navegación robótica

## Referencias

* [Documentación principal](/README.md)
* [Configuración del servidor](/server/README.md)
* [SLAMTEC RPLIDAR A1 Datasheet](https://www.slamtec.com/en/Lidar/A1)