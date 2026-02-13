"""
=============================================================================
EJEMPLO 1: Tu Primera Medicion LIDAR - Tutorial Paso a Paso
=============================================================================

OBJETIVO:
    Capturar y analizar una revolucion completa del sensor RPLIDAR A1.
    Este es el punto de partida para aprender a trabajar con datos LIDAR.

REQUISITOS PREVIOS:
    - Haber configurado config.ini con la IP de tu LIDAR asignado
    - Entender que es una "revolucion" (giro completo de 360 del sensor)

CONCEPTOS CLAVE:
    - El LIDAR mide distancias en todas las direcciones (360)
    - Una "revolucion" = un giro completo = ~300-700 mediciones
    - Cada medicion es una tupla: (calidad, angulo, distancia)
    - Solo las mediciones con distance > 0 son validas

TIEMPO ESTIMADO: 10 minutos

PROXIMO PASO:
    Una vez domines este ejemplo, continua con:
    - continuous_stream.py: Stream continuo de revoluciones
    - print_scan_stub.py: Formato compatible con ROS 2
=============================================================================
"""

from lidarclient import LidarClient
from lidarclient.config import ConfigError, load_config

def main():
    """
    Funcion principal que ejecuta un escaneo LIDAR simple.
    
    Flujo:
        1. Cargar configuracion desde config.ini
        2. Conectar al servidor LIDAR con reintentos automaticos
        3. Obtener una revolucion completa
        4. Analizar y mostrar estadisticas basicas
        5. Desconectar limpiamente
    """
    
    # =========================================================================
    # PASO 1: Cargar Configuracion desde config.ini
    # =========================================================================
    # El archivo config.ini contiene todos los parametros de conexion:
    # - host: IP del servidor LIDAR (ej: 192.168.1.103)
    # - port: Puerto TCP (default: 5000)
    # - timeout: Tiempo maximo de espera (default: 5.0s)
    # - max_retries: Numero de reintentos si falla la conexion
    # - retry_delay: Segundos entre reintentos
    # - scan_mode: Standard o Express
    
    print("Cargando configuracion desde config.ini...")
    try:
        config = load_config()
    except ConfigError as e:
        print(f"Error de configuracion: {e}")
        print("\nSolucion:")
        print("  1. Verifica que existe el archivo config.ini")
        print("  2. Si no existe: cp config.ini.example config.ini")
        print("  3. Edita config.ini con la IP de tu LIDAR")
        return
    
    print(f"Configuracion cargada correctamente")
    print(f"  - Servidor: {config['host']}:{config['port']}")
    print(f"  - Modo: {config['scan_mode']}")
    print(f"  - Timeout: {config['timeout']}s")
    
    # =========================================================================
    # PASO 2: Crear Cliente LIDAR
    # =========================================================================
    # El cliente maneja toda la comunicacion TCP con el servidor.
    # Se encarga de serializar/deserializar datos y manejar errores de red.
    
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
        # PASO 3: Conectar al Servidor con Reintentos Automaticos
        # =====================================================================
        # connect_with_retry() intenta conectar varias veces (max_retries)
        # esperando retry_delay segundos entre intentos.
        # Esto es util si el servidor tarda en arrancar o hay problemas de red.
        
        print("\nConectando al servidor LIDAR...")
        client.connect_with_retry()
        print(f"Conectado exitosamente a {config['host']}:{config['port']}")
        
        # =====================================================================
        # PASO 4: Obtener una Revolucion Completa
        # =====================================================================
        # get_scan() espera hasta recibir una revolucion completa del LIDAR.
        # El tiempo de espera depende del modo:
        # - Standard: ~0.2s (360 puntos)
        # - Express: ~0.1s (720 puntos)
        
        print("\nSolicitando revolucion...")
        scan = client.get_scan()
        
        # =====================================================================
        # PASO 5: Analizar Datos Recibidos
        # =====================================================================
        # scan es una lista de tuplas: [(quality, angle, distance), ...]
        # - quality: int (0-15) en Standard, None en Express
        # - angle: float (0-360) en grados
        # - distance: float en milimetros (0 = sin medicion valida)
        
        print("\nRevolucion completa recibida")
        print(f"Total de puntos: {len(scan)}")
        
        # Filtrar solo mediciones validas (distance > 0)
        # Los puntos con distance=0 indican que el LIDAR no detecto ningun objeto
        # en esa direccion (puede estar fuera de rango o ser transparente).
        valid_points = [point for point in scan if point[2] > 0]
        valid_percentage = (len(valid_points) / len(scan) * 100) if scan else 0
        
        print(f"Puntos validos: {len(valid_points)} ({valid_percentage:.1f}%)")
        
        # =====================================================================
        # PASO 6: Calcular Estadisticas Basicas
        # =====================================================================
        
        if valid_points:
            # Extraer solo las distancias para calcular min/max
            distances = [d for _, _, d in valid_points]
            
            min_dist = min(distances)
            max_dist = max(distances)
            avg_dist = sum(distances) / len(distances)
            
            print(f"\nEstadisticas de distancia:")
            print(f"  Minima: {min_dist:.1f} mm ({min_dist/1000:.2f} m)")
            print(f"  Maxima: {max_dist:.1f} mm ({max_dist/1000:.2f} m)")
            print(f"  Promedio: {avg_dist:.1f} mm ({avg_dist/1000:.2f} m)")
            
            # ================================================================
            # PASO 7: Mostrar Primeros 5 Puntos (para entender el formato)
            # ================================================================
            
            print("\nPrimeros 5 puntos validos:")
            for i, (quality, angle, distance) in enumerate(valid_points[:5], 1):
                # Manejar calidad None en modo EXPRESS
                # En Express, quality es None porque el sensor no envia ese dato
                # para poder capturar mas puntos por segundo.
                quality_str = f"{quality:2d}" if quality is not None else "--"
                print(
                    f"{i}. Calidad {quality_str}/15, "
                    f"Angulo {angle:6.2f}, "
                    f"Distancia {distance:7.2f} mm"
                )
            
            # Encontrar el objeto mas cercano
            closest = min(valid_points, key=lambda p: p[2])
            print(f"\nObjeto mas cercano:")
            print(f"  Distancia: {closest[2]:.1f} mm ({closest[2]/1000:.2f} m)")
            print(f"  Angulo: {closest[1]:.1f}")
            
        else:
            print("\nAdvertencia: No se detectaron objetos validos en esta revolucion.")
            print("Posibles causas:")
            print("  - El LIDAR esta apuntando a un area vacia")
            print("  - Los objetos estan fuera del rango de medicion (>12m)")
            print("  - Problema de conexion con el sensor")
        
        # =====================================================================
        # PASO 8: Desconectar Limpiamente
        # =====================================================================
        
        client.disconnect()
        print("\nDesconectado del servidor")
        print("Escaneo completado con exito")
    
    except KeyboardInterrupt:
        print("\nInterrupcion detectada (Ctrl+C)")
        client.disconnect()
        print("Desconectado del servidor")
    
    except Exception as e:
        print(f"\nError durante el escaneo: {e}")
        print("\nSoluciones posibles:")
        print("  1. Verifica que el servidor esta corriendo:")
        print("     ssh pi@<IP> 'sudo systemctl status rplidar-server.service'")
        print("  2. Verifica la conexion de red: ping <IP>")
        print("  3. Verifica que el puerto 5000 esta abierto")
        client.disconnect()


# =============================================================================
# EJERCICIOS SUGERIDOS PARA PRACTICAR:
# =============================================================================
# 
# 1. BASICO: Modifica el codigo para mostrar tambien el objeto mas LEJANO
#    Pista: Usa max() en lugar de min() sobre valid_points
#
# 2. INTERMEDIO: Calcula cuantos objetos hay en el sector frontal (+-30)
#    Pista: Sector frontal va de 330 a 30 (cruza el 0)
#    Solucion:
#      front = [p for p in valid_points if p[1] >= 330 or p[1] <= 30]
#
# 3. AVANZADO: Captura 5 revoluciones en un bucle y compara:
#    - Varia mucho el numero de puntos entre revoluciones?
#    - La distancia promedio es estable?
#    - Cuanto tarda cada revolucion? (usa time.time())
#
# 4. INVESTIGACION: Si estas en modo Standard, filtra solo mediciones
#    con calidad >= 10 y compara las estadisticas
#    Solucion:
#      high_quality = [p for p in valid_points if p[0] is not None and p[0] >= 10]
#
# 5. VISUALIZACION: Guarda los datos en un archivo CSV para analizarlos:
#    - Columnas: angle, distance, quality
#    - Una fila por cada punto valido
#    - Abre el CSV en Excel o LibreOffice para hacer graficos
#
# =============================================================================

if __name__ == "__main__":
    main()
