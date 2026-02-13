"""
=============================================================================
EJEMPLO 4: Formato Compatible con ROS 2 LaserScan
=============================================================================

OBJETIVO:
    Mostrar datos del LIDAR en formato similar a sensor_msgs/LaserScan de ROS 2,
    facilitando la migracion de codigo o integracion con sistemas ROS existentes.

REQUISITOS PREVIOS:
    - Haber completado continuous_stream.py
    - (Opcional) Familiaridad basica con ROS 2 y el mensaje LaserScan
    - Entender conversiones de unidades (mm a metros, grados a radianes)

CONCEPTOS QUE APRENDERAS:
    - Formato del mensaje sensor_msgs/LaserScan de ROS 2
    - Conversion de milimetros a metros (estandar en robotica)
    - Conversion de grados a radianes (estandar matematico)
    - Filtrado de mediciones finitas vs infinitas
    - Patron callback para procesamiento de datos

CASOS DE USO PRACTICOS:
    - Migrar codigo existente de ROS 2 a TCP sin ROS
    - Debugging de cobertura angular del LIDAR
    - Verificar rangos de medicion antes de procesamiento avanzado
    - Integracion con algoritmos que esperan formato LaserScan
    - Usuarios familiarizados con el ecosistema ROS

NOTA IMPORTANTE:
    Este script NO requiere ROS 2 instalado. Solo simula el formato
    de datos para facilitar la compatibilidad y migracion.

TIEMPO ESTIMADO: 15 minutos

DETENER: Presiona Ctrl+C para finalizar
=============================================================================
"""

import math

from lidarclient import LidarClient
from lidarclient.config import ConfigError, load_config


def on_scan(scan):
    """
    Procesa una revolucion del LIDAR y muestra estadisticas formato LaserScan.
    
    Este callback simula el comportamiento de un suscriptor ROS 2 al topic /scan
    que recibe mensajes sensor_msgs/LaserScan, pero usando datos TCP directos.
    
    Formato sensor_msgs/LaserScan (resumen):
        - ranges: array de distancias en METROS
        - angle_min/max: limites angulares en RADIANES
        - range_min/max: limites de distancia valida
        - time_increment: tiempo entre mediciones
    
    Args:
        scan: Lista de tuplas (quality, angle, distance) del LIDAR
              - quality: int 0-15 (Standard) o None (Express)
              - angle: float 0-360 grados
              - distance: float en milimetros (0 = sin medicion)
    
    Muestra:
        Estadisticas en formato compacto similar a LaserScan:
        ranges=N finite=M min=X.XXm max=Y.YYm angle_min=A.AA rad angle_max=B.BB rad
    """
    
    # =========================================================================
    # PASO 1: Convertir Distancias a Metros (Estandar ROS)
    # =========================================================================
    # En ROS 2, el mensaje LaserScan usa METROS como unidad de distancia.
    # Nuestro LIDAR devuelve milimetros, asi que convertimos: mm / 1000 = m
    #
    # Ejemplo: 1250.5 mm -> 1.2505 m
    
    ranges = [distance / 1000.0 for _, _, distance in scan]
    
    # =========================================================================
    # PASO 2: Extraer Angulos y Convertir a Radianes
    # =========================================================================
    # El LIDAR devuelve angulos en GRADOS (0-360), pero el estandar
    # matematico y ROS usan RADIANES.
    #
    # Conversion: radianes = grados * (pi / 180)
    # Python: math.radians(grados)
    #
    # Calculamos angle_min y angle_max del scan para verificar cobertura.
    
    angles = [angle for _, angle, _ in scan]
    
    if angles:
        # Convertir min/max de grados a radianes
        angle_min = math.radians(min(angles))
        angle_max = math.radians(max(angles))
    else:
        # Scan vacio (raro, pero posible en errores)
        angle_min = 0.0
        angle_max = 0.0
    
    # =========================================================================
    # PASO 3: Filtrar Mediciones Finitas (Validas)
    # =========================================================================
    # En ROS 2 LaserScan, las mediciones pueden ser:
    # - Finitas: valores numericos validos (objeto detectado)
    # - Infinitas: inf o nan (sin deteccion, fuera de rango)
    #
    # Nuestro LIDAR usa distance=0 para "sin medicion", que convertimos
    # a 0.0 metros. Filtramos valores > 0 y finitos.
    #
    # math.isfinite() verifica que no sea inf, -inf o nan
    
    finite = [r for r in ranges if math.isfinite(r) and r > 0]
    
    # =========================================================================
    # PASO 4: Mostrar Estadisticas Formato LaserScan
    # =========================================================================
    # Mostramos informacion clave en formato compacto de una linea:
    # - ranges: total de mediciones en el scan
    # - finite: cuantas son validas (>0 y finitas)
    # - min/max: rango de distancias validas en metros
    # - angle_min/max: cobertura angular en radianes
    #
    # Este formato facilita comparacion directa con mensajes ROS LaserScan.
    
    if finite:
        # Hay mediciones validas: calcular min/max de distancias
        print(
            f"ranges={len(ranges)} finite={len(finite)} "
            f"min={min(finite):.3f}m max={max(finite):.3f}m "
            f"angle_min={angle_min:.3f} rad "
            f"angle_max={angle_max:.3f} rad"
        )
    else:
        # Sin mediciones validas en este scan
        # Posibles causas: area vacia, objetos fuera de rango, error temporal
        print(
            f"ranges={len(ranges)} finite=0 "
            f"angle_min={angle_min:.3f} rad "
            f"angle_max={angle_max:.3f} rad"
        )


def main():
    """
    Conecta al servidor LIDAR y procesa revoluciones continuamente.
    
    Este main() reemplaza el comportamiento de un nodo ROS 2 que se suscribe
    al topic /scan, pero usando conexion TCP directa sin necesidad de instalar
    o configurar ROS 2.
    
    Flujo:
        1. Cargar configuracion (equivalente a parametros ROS)
        2. Crear cliente LIDAR (equivalente a suscriptor /scan)
        3. Bucle infinito llamando a on_scan() por cada revolucion
        4. Ctrl+C para detener limpiamente
    """
    
    # =========================================================================
    # PASO 1: Cargar Configuracion
    # =========================================================================
    # En ROS 2, estos parametros vendrian de launch files o archivos YAML.
    # Aqui los cargamos de config.ini para simplicidad.
    
    try:
        config = load_config()
    except ConfigError as e:
        print(f"Error de configuracion: {e}")
        print("\nEn ROS 2, verificarias los parametros del nodo.")
        print("Aqui, verifica que config.ini existe y es valido.")
        return
    
    # =========================================================================
    # PASO 2: Crear Cliente LIDAR
    # =========================================================================
    # Equivalente a crear un suscriptor ROS 2:
    # self.subscription = self.create_subscription(
    #     LaserScan, '/scan', self.scan_callback, 10)
    
    client = LidarClient(
        config["host"],
        port=config["port"],
        timeout=config["timeout"],
        max_retries=config["max_retries"],
        retry_delay=config["retry_delay"],
        scan_mode=config["scan_mode"],
    )
    
    try:
        # =====================================================================
        # PASO 3: Conectar al Servidor
        # =====================================================================
        # En ROS 2, la conexion seria automatica al arrancar el nodo.
        
        client.connect_with_retry()
        print("Conectado al servidor LIDAR")
        print(f"Servidor: {config['host']}:{config['port']}")
        print("Mostrando estadisticas de escaneo (formato LaserScan)")
        print("Presiona Ctrl+C para detener\n")
        
        # =====================================================================
        # PASO 4: Bucle de Recepcion de Scans
        # =====================================================================
        # En ROS 2, esto seria el spin() del nodo llamando callbacks.
        # Aqui hacemos un bucle infinito llamando on_scan() manualmente.
        
        while True:
            # Obtener revolucion (equivalente a recibir mensaje LaserScan)
            scan = client.get_scan()
            
            # Procesar revolucion (equivalente a callback)
            on_scan(scan)
    
    except KeyboardInterrupt:
        # =====================================================================
        # PASO 5: Manejo de Ctrl+C
        # =====================================================================
        # En ROS 2, esto seria manejado por rclpy.shutdown()
        
        print("\nDetenido por usuario")
    
    finally:
        # =====================================================================
        # PASO 6: Desconexion Limpia
        # =====================================================================
        # En ROS 2, esto seria el destroy_node()
        
        client.disconnect()
        print("Desconectado del servidor")


# =============================================================================
# EJERCICIOS SUGERIDOS PARA PRACTICAR:
# =============================================================================
#
# 1. BASICO: Añade el calculo de angle_increment (incremento angular medio)
#    Formula: (angle_max - angle_min) / numero_de_mediciones
#    Es un campo importante en sensor_msgs/LaserScan
#
# 2. INTERMEDIO: Calcula range_min y range_max (distancia minima/maxima
#    valida del sensor). Para RPLIDAR A1: range_min=0.15m, range_max=12.0m
#    Marca mediciones fuera de rango como invalidas.
#
# 3. AVANZADO: Crea una estructura de datos (clase o dict) que replique
#    exactamente el mensaje sensor_msgs/LaserScan de ROS 2:
#    - header (timestamp, frame_id)
#    - angle_min, angle_max, angle_increment
#    - time_increment, scan_time
#    - range_min, range_max
#    - ranges (array de floats)
#    - intensities (array de floats - usa quality si disponible)
#
# 4. INVESTIGACION: Si tienes ROS 2 instalado, crea un nodo que publique
#    estos datos como mensajes LaserScan reales al topic /scan.
#    Compara con rplidar_ros oficial.
#
# 5. CONVERSION: Modifica on_scan() para devolver un diccionario JSON
#    con todos los campos LaserScan, util para integracion con sistemas
#    que no usan ROS pero esperan ese formato estandar.
#
# =============================================================================

if __name__ == "__main__":
    main()
