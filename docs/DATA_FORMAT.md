# Formato de Datos del RPLIDAR A1

Documentación completa del formato de datos devueltos por el RPLIDAR A1 a través del cliente TCP

---

Cada revolución del LIDAR se transmite como una lista de tuplas Python:

```python
[
    (quality, angle, distance),
    (quality, angle, distance),
    ...
]
```

## Campos de cada medición

Cada medición individual es una tupla de 3 elementos:

| Campo    | Tipo       | Descripción             | Rango/Valores                   |
| -------- | ---------- | ----------------------- | ------------------------------- |
| quality  | int o None | Calidad de la medición  | 0-15 (Standard), None (Express) |
| angle    | float      | Ángulo en grados        | 0.0 - 359.99°                   |
| distance | float      | Distancia en milímetros | 0.0 - 12000.0 mm                |

## Modos de escaneo:

### 1. Modo Standard

```python
scan = [
    (15, 0.5, 1234.5),
    (14, 1.2, 1245.8),
    (12, 2.0, 1250.0),
    ...
]
```

#### 1.1 Características:

* `quality`: valores de 0 a 15
    
    * 0  = calidad muy baja o medición inválida
    * 15 = calidad máxima

* Menos puntos por revolución (~90-120 puntos)
* Mayor precisión por punto

### 2. Modo Express

```python
scan = [
    (None, 0.5, 1234.5),
    (None, 1.2, 1245.8),
    (None, 2.0, 1250.0),
    ...
]
```

#### 2.1 Características:

* `quality`: siempre `None`
* Más puntos por revolución (~360-400 puntos)
* Mayor densidad de datos
* Modo recomendado para mapeo

## Interpretación de Valores

### Campo `quality`:

En modo Standard:

* 0: Medición inválida, ignorar

* 1-7: Calidad baja, usar con precaución

* 8-11: Calidad media, aceptable

* 12-15: Calidad alta, datos confiables

En modo Express:

* Siempre None

* No hay información de calidad

* Asume que todos los puntos son válidos

#### Ejemplo de filtrado

```python
# Filtrar por calidad mínima en modo Standard
MIN_QUALITY = 8
filtered_scan = [(q, a, d) for q, a, d in scan if q is not None and q >= MIN_QUALITY]

# En modo Express, filtrar por distancia válida
filtered_scan = [(q, a, d) for q, a, d in scan if d > 0]
```

### Campo `angle`:

Representación:

* Grados decimales (0.0 - 359.99°)

* Rotación en sentido horario

* 0° = frente del sensor (marca roja)

Orientación física:

* 0° / 360°: Frente (marca roja del LIDAR)

* 90°: Derecha del LIDAR

* 180°: Atrás del LIDAR

* 270°: Izquierda del LIDAR

#### Ejemplo de sectores:

```python
# Detectar objetos al frente (330° - 30°)
front_points = [
    (q, a, d) for q, a, d in scan 
    if a >= 330 or a <= 30
]

# Detectar objetos a la derecha (80° - 100°)
right_points = [
    (q, a, d) for q, a, d in scan 
    if 80 <= a <= 100
]
```

### Campo `distance`:

Unidad: Milímetros (mm)

#### Rangos:

* 0.0: Medición inválida, no hay objeto detectado

* 150 - 12000: Rango válido del RPLIDAR A1 (15 cm - 12 m)

* Valores fuera de rango: considerar inválidos

#### Conversión de unidades:

```python
# Milímetros a metros
distance_m = distance_mm / 1000.0

# Milímetros a centímetros
distance_cm = distance_mm / 10.0
```
#### Ejemplo de filtrado por distancia:

```python
# Objetos entre 30 cm y 3 m
MIN_DIST = 300   # 30 cm en mm
MAX_DIST = 3000  # 3 m en mm

in_range = [
    (q, a, d) for q, a, d in scan 
    if MIN_DIST <= d <= MAX_DIST
]
```

## Casos especiales

### Mediciones inválidas

1. distance == 0.0 (sin objeto detectado)

2. quality == 0 en modo Standard

3. distance < 150 o distance > 12000 (fuera de rango)

### Ejemplo de limpieza

```python
def is_valid_measurement(quality, angle, distance):
    """
    Verifica si una medición es válida.
    
    Returns:
        bool: True si la medición es válida
    """
    # Distancia debe estar en rango
    if distance < 150 or distance > 12000:
        return False
    
    # En modo Standard, verificar calidad
    if quality is not None and quality == 0:
        return False
    
    return True

# Filtrar mediciones válidas
valid_scan = [(q, a, d) for q, a, d in scan if is_valid_measurement(q, a, d)]
```

### Revoluciones Incompletas

Ocasionalmente, una revolución puede tener menos puntos de lo esperado:

* Modo Standard: menos de 80 puntos

* Modo Express: menos de 300 puntos

Causas comunes:

* Inicio del escaneo (primera revolución)

* Obstrucción temporal del sensor

* Superficie muy absorbente (negro mate)

Recomendación:

* Descartar la primera revolución tras conectar

* Validar número mínimo de puntos antes de procesar

### Ejemplo de procesamiento
#### Ejemplo 1: Encontrar punto más cercano
```python
def find_closest_point(scan):
    """
    Encuentra el punto más cercano en una revolución.
    
    Args:
        scan: Lista de tuplas (quality, angle, distance)
    
    Returns:
        tuple: (quality, angle, distance) del punto más cercano
        None: si no hay puntos válidos
    """
    valid_points = [(q, a, d) for q, a, d in scan if d > 0]
    
    if not valid_points:
        return None
    
    return min(valid_points, key=lambda x: x)[1]

# Uso
closest = find_closest_point(scan)
if closest:
    q, angle, dist = closest
    print(f"Objeto más cercano: {dist:.1f} mm a {angle:.1f}°")
```

#### Ejemplo 2: Contar objetos por zona

```python
def count_by_distance_zones(scan):
    """
    Cuenta puntos por zonas de distancia.
    
    Returns:
        dict: Conteo de puntos por zona
    """
    zones = {
        'critica': 0,    # 0-30 cm
        'cercana': 0,    # 30 cm - 1 m
        'media': 0,      # 1-3 m
        'lejana': 0      # 3+ m
    }
    
    for q, a, d in scan:
        if d == 0:
            continue
        elif d < 300:
            zones['critica'] += 1
        elif d < 1000:
            zones['cercana'] += 1
        elif d < 3000:
            zones['media'] += 1
        else:
            zones['lejana'] += 1
    
    return zones
```

#### Ejemplo 3: Calcular la cobertura angular

```python
def calculate_angular_coverage(scan):
    """
    Calcula la cobertura angular de la revolución.
    
    Returns:
        float: Porcentaje de cobertura (0-100%)
    """
    if not scan:
        return 0.0
    
    # Ángulos únicos (redondeados a grados enteros)
    unique_angles = set(int(a) for q, a, d in scan if d > 0)
    
    # Cobertura = (ángulos únicos / 360) * 100
    coverage = (len(unique_angles) / 360.0) * 100.0
    
    return coverage
```

## Serialización y Transmisión

### Formato de Transmisión TCP

El servidor transmite cada revolución usando **pickle** (Python serialization):

```python
# Servidor
import pickle

revolution = [(q1, a1, d1), (q2, a2, d2), ...]
data = pickle.dumps(revolution)
client_socket.sendall(len(data).to_bytes(4, 'big'))  # Tamaño primero
client_socket.sendall(data)                           # Luego datos

# Cliente
size_bytes = socket.recv(4)
size = int.from_bytes(size_bytes, 'big')
data = socket.recv(size)
revolution = pickle.loads(data)
```

### Tamaño de datos

#### Modo Standard (~100 puntos):

* Tamaño aproximado: 2-3 KB por revolución

* Tasa de datos: ~20-30 KB/s a 10 Hz

#### Modo Express (~365 puntos):

* Tamaño aproximado: 8-10 KB por revolución

* Tasa de datos: ~80-100 KB/s a 10 Hz

## Referencias

* Hardware: [SLAMTEC RPLIDAR A1M8](https://www.slamtec.com/en/Lidar/A1)

* Librería servidor: [rplidar-roboticia](https://github.com/Roboticia/RPLidar)

* Protocolo: TCP con serialización [pickle](https://docs.python.org/3/library/pickle.html)

* Documentación oficial: [RPLIDAR SDK](https://www.slamtec.com/en/Support#rplidar-a-series)

## Notas importantes

1. Los ángulos no están ordenados: Los puntos llegan en orden temporal, no angular

2. Timestamp: El formato actual no incluye timestamp, considerar añadirlo en futuras versiones

3. Coordenadas cartesianas: Para convertir a (x, y):

```python
import math
x = distance * math.cos(math.radians(angle))
y = distance * math.sin(math.radians(angle))
```

4. Thread-safety: Si procesas datos en múltiples threads, usa locks apropiados.

    Cuando se usan *múltiples hilos* (threads) que comparten los mismos datos del LIDAR, pueden ocasionarse errores en el acceso concurrente.

    Un "lock" sirve pra garantizar que solo un hilo a la vez accede a una sección crítica de código donde se leen o modifican los datos compartidos (ejemplo: librería `threading`)

---
*Última actualzación: 2026-02-18*

*Versión del proyecto: v0.7.0*