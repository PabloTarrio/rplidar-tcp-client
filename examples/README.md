# Ejemplos de uso de lidar_client

Esta carpeta contiene ejemplos prácticos de cómo usar la librería `lidar_client` para conectarse al servidor LIDAR TCP en la Raspberry Pi.

## Requisitos previos

Antes de ejecutar cualquier ejemplo:

1. **Servidor TCP corriendo en la Raspberry Pi**:
   ```bash
   # En la Raspberry Pi
   python3 servidor_lidar_tcp.py
   ```

2. **Librería instalada en tu PC:**
    ```bash
    pip install -e .
    ```

3. **Ajustar la IP: En cada ejemplo cambia 192.168.1.100 por la IP de tu Raspberry PI**

## EJEMPLOS DISPONIBLES

1. *simple_scan.py* - Lectura básica - Recomendado para empezar.

    Qué hace: 
    
    Obtiene una sola revolución completa del LIDAR y muestra estadísticas básicas.

    Ideal para:

    * Primeras pruebas de conexión
    * Verificar que el sistema funciona correctamente
    * Entender el formato de datos (calidad, ángulo, distancia)
    
    Uso:
    ```bash
    python examples/simple_scan.py
    ```

    Salida esperada:

    ```bash
    === Revolución completa recibida ===
    Total de puntos: 67
    Puntos válidos: 65
    Distancia mínima: 360.2 mm
    Distancia máxima: 1907.2 mm

    === Primeros 5 puntos ===
    1. Calidad: 15, Ángulo: 187.81°, Distancia: 1907.25 mm
    2. Calidad: 15, Ángulo: 189.23°, Distancia: 1896.25 mm
    ```

2. *continuous_stream.py* - Stream en tiempo real.

    Qué hace: 
    
    Recibe revoluciones continuamente y muestra estadísticas actualizadas en tiempo real.

    Ideal para:

    - Monitoreo continuo del entorno
    - Detectar cambios en el espacio escaneado
    - Verificar estabilidad del sistema.
    - Aplicaciones que necesitan datos en tiempo real.

    Uso:
    ```bash
    python examples/continuous_stream.py
    ```

    Salida esperada:
    ```bash
    Conectado al servidor LIDAR
    Presiona Ctrl+C para detener

    Rev #  1: Puntos= 67 Válidos= 65 Dist.Media= 1234.5mm Min= 360.2mm Max=1907.2mm
    Rev #  2: Puntos= 68 Válidos= 66 Dist.Media= 1238.1mm Min= 358.5mm Max=1912.3mm
    Rev #  3: Puntos= 67 Válidos= 64 Dist.Media= 1230.7mm Min= 362.1mm Max=1905.8mm
    ```
    Detener: Presiona CTRL+C para finalizar

3. *print_scan_stub.py* - Formato compatible ROS2

    Qué hace:

    Stream continuo mostrando estadísticas en formato similar a sensor_msgs/LaserScan de ROS 2 (distancias en metros, ángulos en radianes).

    Ideal para:

    * Migrar código existente de ROS 2 a TCP.
    * Usuarios familiarizados con el ecosistema ROS.
    * Debugging de cobertura angular y rango de mediciones.
    * Aplicaciones que esperan formato LaserScan

    Uso:
    ```bash
    python examples/print_scan_stub.py
    ```
    Salida esperada:
    ```bash
    Conectado al servidor LIDAR
    Mostrando estadísticas de escaneo (formato LaserScan)
    Presiona Ctrl+C para detener

    ranges=67 finite=65 min=0.360m max=1.907m angle_min=3.285 rad angle_max=6.135 rad
    ranges=68 finite=66 min=0.358m max=1.912m angle_min=3.281 rad angle_max=6.139 rad
    ```

    Nota: este ejemplo NO requiere ROS 2 instalado. Solo simula el formato de datos.

    Detener: Presiona CTRL+C para finalizar

## Formato de datos del LIDAR

Todas las revoluciones se devuelven como una lista de tuplas:

```python
scan = client.get_scan()
# scan = [(quality, angle, distance),(quality, angle, distance), ...]
```

* quality (int): Confianza de la medición de (0-15, donde 15 es máxima calidad)
* angle (float): Ángulo en grados (0-360º)
* distance (float): Distancia en milímetros (0 = sin medición válida)

**Ejemplo de procesamiento:**
```python
for quality, angle, distance in scan:
    if distance > 0: # Filtrar mediciones válidas
        print (f"Objeto detectado a {angle:.1f} y {distance:.1f} mm.")
```

**Solución de problemas**

*Error: "Connection refused"*
* Verifica que el servidor TCP esté correindo en la Raspberry Pi
* Comprueba que la IP en el código sea correcta
* Verifica conectividad: ```bash ping <IP_RASPBERRY_PI>```

*Error: "No module named "lidar_client""*
* Instala la librería: ```python pip install -e . ``` (desde la raíz del proyecto)

*Revoluciones con pocos puntos válidos*
* Normal si el LIDAR apunta a una zona vacía o muy lejana
* El RPLidar tiene un rango de medición típico de 0.15 - 12 m.

*El servidor se cierra tras una conexión*
* Asegúrate de usar la versión del servidor con buble continuo
* Verifica que el servidor no tenga errores en los logs.

## Próximos pasos 

Una vez que domines estos ejemplos puedes:
* Crear tus propias aplicaciones de procesamiento de datos LIDAR
* Implementar detección de obstáculos
* Guardar datos en CSV/JSON para análisis offline
* Visualizar el escaneo en tiempo real con matploblib 

