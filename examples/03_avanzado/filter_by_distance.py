"""
Ejemplo avanzado: Filtrado por rango de distancia.

Este script demuestra como filtrar puntos del LIDAR según su distancia,
permitiendo definir un rango mínimo y máximo de detección.

CONCEPTO: Distancia en el LIDAR
===============================

El RPLIDAR A1 mide distancias en milímetros (mm):
    - Rango válido: 150 mm a 12000 mm (0.15-12 metros)
    - Distancia = 0: Sin medición válida (fuera de rango o superficie
            no reflectante)
    - Precisión: ±1% a ±15% según condiciones


CASOS DE USO
============
    1. Navegación Autónoma: Detectar solo obstáculos cercanos (0.2m - 3m)
    2. Mapeo de habitación: Ignorar objetos muy cercanos o muy lejanos
    3. Zona de seguridad: Alertar si hay objetos a menos de X metros.
    4. Anti-colision: MOnitorizar solo la zona crítica (<0.5m.)

EJERCICIOS SUGERIDOS
====================
    1. Modifica MIN_DIST y MAX_DIST para detectar solo objetos cercanos
    2. Crea una alerta visual cuando hay objetos a menos de 30 cm
    3. Calcula el porcentaje de cobertura en diferentes rangos de distancia
    4. Detecta el punto mas cercano y su angulo en cada revolucion
    5. Guarda en CSV solo puntos dentro de un rango especifico
"""

from lidarclient import LidarClient
from lidarclient.config import ConfigError, load_config


def filter_by_distance(scan, min_dist=200, max_dist=5000):
    """
    Filtra los puntos de una revolucion segun rango de distancia.

    Args:
        scan: Lista de tuplas (quality, angle, distance) de una revolucion
        min_dist: Distancia minima en mm (por defecto 200mm = 20cm)
        max_dist: Distancia maxima en mm (por defecto 5000mm = 5m)

    Returns:
        tuple: (puntos_en_rango, puntos_muy_cerca, puntos_muy_lejos)
            - puntos_en_rango: Puntos dentro del rango [min_dist, max_dist]
            - puntos_muy_cerca: Puntos con distancia < min_dist
            - puntos_muy_lejos: Puntos con distancia > max_dist

    Ejemplo:
        >>> scan = [(15, 45.0, 300), (15, 90.0, 100), (15, 135.0, 6000)]
        >>> en_rango, cerca, lejos = filter_by_distance(
        ...     scan, min_dist=200, max_dist=5000
        ... )
        >>> len(en_rango)  # 1 punto (300mm esta en rango)
        1
    """
    puntos_en_rango = []
    puntos_muy_cerca = []
    puntos_muy_lejos = []

    for point in scan:
        quality, angle, distance = point

        # =================================================================
        # Clasificar puntos segun distancia
        # =================================================================
        if distance == 0:
            # Sin medición válida - se ignora completamente
            continue
        if distance < min_dist:
            # Demasiado cerca - puede ser ruido o partes del robot
            puntos_muy_cerca.append(point)
        if distance > max_dist:
            # Demasiado lejos - fuera del rango de interés
            puntos_muy_lejos.append(point)
        else:
            # Dentro del rango objetivo
            puntos_en_rango.append(point)

    return puntos_en_rango, puntos_muy_cerca, puntos_muy_lejos


def find_closest_point(scan):
    """
    Encuentra el punto mas cercano en una revolucion.

    Args:
        scan: Lista de tuplas (quality, angle, distance)

    Returns:
        tuple: (quality, angle, distance) del punto mas cercano
               o None si no hay puntos validos
    """
    valid_points = [p for p in scan if p[2] > 0]

    if not valid_points:
        return None

    # Encontrar el punto con menor distancia
    closest = min(valid_points, key=lambda p: p[2])
    return closest


def analyze_distance_zones(scan, zones):
    """
    Analiza cuantos puntos hay en diferentes zonas de distancia.

    Args:
        scan: Lista de tuplas (quality, angle, distance)
        zones: Lista de tuplas (nombre, min_dist, max_dist) en mm

    Returns:
        dict: {nombre_zona: cantidad_puntos}

    Ejemplo:
        >>> zones = [
        ...     ("Critica", 0, 300),
        ...     ("Cercana", 300, 1000),
        ...     ("Media", 1000, 3000),
        ...     ("Lejana", 3000, 12000)
        ... ]
        >>> counts = analyze_distance_zones(scan, zones)
    """

    zone_counts = {name: 0 for name, _, _ in zones}

    for quality, angle, distance in scan:
        if distance == 0:
            continue

        # Clasificar en zona correspondiente
        for zone_name, zone_min, zone_max in zones:
            if zone_min <= distance < zone_max:
                zone_counts[zone_name] += 1
                break

    return zone_counts


def main():
    """
    Funcion principal: Filtra puntos por distancia en tiempo real
    """
    # =====================================================================
    # PASO 1: Cargar configuracion desde config.ini
    # =====================================================================
    try:
        config = load_config()
    except ConfigError as e:
        print(f"Error de configuración: {e}")
        return

    # =====================================================================
    # PASO 2: Configurar rango de distancia
    # =====================================================================
    # Puedes modificar estos valores segun tu aplicacion:
    #
    # Para navegacion autonoma:
    #   MIN_DIST = 200   (20 cm - evita ruido del propio robot)
    #   MAX_DIST = 3000  (3 m - rango de reaccion)
    #
    # Para mapeo de habitacion:
    #   MIN_DIST = 150   (15 cm - minimo del sensor)
    #   MAX_DIST = 8000  (8 m - paredes lejanas)
    #
    # Para deteccion de personas cercanas:
    #   MIN_DIST = 500   (50 cm - distancia de seguridad)
    #   MAX_DIST = 2000  (2 m - rango de interaccion)

    MIN_DIST = 200
    MAX_DIST = 5000

    # Definir zonas de seguridad para análisis
    SAFETY_ZONES = [
        ("CRITICA", 0, 300),  # < 30 cm     -> Alerta Roja
        ("CERCANA", 300, 1000),  # 30 cm - 1 m -> Precaución
        ("MEDIA", 1000, 3000),  # 1 m - 3 m   -> Normal
        ("LEJANA", 3000, 12000),  # > 3 m       -> Informativa
    ]

    print("=" * 70)
    print("        FILTRADO POR DISTANCIA - RPLIDAR A1")
    print("=" * 70)
    print(f"Servidor:           {config['host']}:{config['port']}")
    print(f"Modo de escaneo:    {config['scan_mode']}")
    print(f"Rango de distancia: {MIN_DIST} mm - {MAX_DIST} mm")
    print(f"                    {MIN_DIST / 1000:.2F} m - {MAX_DIST / 1000:.2F} m")
    print("\nPresiona Ctrl+C para detener")
    print("=" * 70)

    # =====================================================================
    # # PASO 3: Conectar al servidor LIDAR
    # =====================================================================
    client = LidarClient(
        config["host"],
        port=config["port"],
        timeout=config["timeout"],
        max_retries=config["max_retries"],
        retry_delay=config["retry_delay"],
        scan_mode=config["scan_mode"],
    )

    try:
        client.connect_with_retry()
        print(f"\nConectado a {config['host']}:{config['port']}")

        revolution_count = 0

        # =================================================================
        # PASO 4: Procesar revoluciones continuamente
        # =================================================================
        while True:
            # Obtener una revolución completa
            scan = client.get_scan()
            revolution_count += 1

            # -------------------------------------------------------------
            # Filtrar por distancia
            # -------------------------------------------------------------
            en_rango, muy_cerca, muy_lejos = filter_by_distance(
                scan, min_dist=MIN_DIST, max_dist=MAX_DIST
            )

            # -------------------------------------------------------------
            # Estadisticas basicas
            # -------------------------------------------------------------
            total = len(scan)
            total_validos = len(en_rango) + len(muy_cerca) + len(muy_lejos)
            invalidos = total - total_validos

            print(f"\nRev #{revolution_count:3d}")
            print(f"  Total:     {total:4d} puntos")
            print(f"  En rango:  {len(en_rango):4d} puntos")
            print(f"  Muy cerca: {len(muy_cerca):4d} puntos (< {MIN_DIST} mm)")
            print(f"  Muy lejos:   {len(muy_lejos):4d} puntos (> {MAX_DIST} mm)")
            print(f"  Invalidos (0):  {invalidos:4d} puntos")

            # -------------------------------------------------------------
            # Encontrar punto mas cercano (CRITICO para anti-colision)
            # -------------------------------------------------------------
            closest = find_closest_point(scan)

            if closest:
                q, ang, dist = closest
                print("\n  Punto mas cercano:")
                print(f"    Distancia: {dist:7.1f} mm ({dist / 1000:.3f} m)")
                print(f"    Angulo:    {ang:6.1f} grados")

                # Alerta si esta muy cerca
                if dist < 300:
                    print("    >>> ALERTA: OBSTACULO CRITICO! <<<")
            # Calcular distancias del rango objetivo
            # -------------------------------------------------------------
            if en_rango:
                distancias = [d for _, _, d in en_rango]
                dist_min = min(distancias)
                dist_max = max(distancias)
                dist_avg = sum(distancias) / len(distancias)

                print("\n  Estadisticas del rango objetivo:")
                print(f"    Minima:   {dist_min:7.1f} mm ({dist_min / 1000:.2f} m)")
                print(f"    Maxima:   {dist_max:7.1f} mm ({dist_max / 1000:.2f} m)")
                print(f"    Promedio: {dist_avg:7.1f} mm ({dist_avg / 1000:.2f} m)")

            # -------------------------------------------------------------
            # Analisis por zonas cada 10 revoluciones
            # -------------------------------------------------------------
            if revolution_count % 10 == 0:
                print("\n" + "=" * 70)
                print(f"ANALISIS DE ZONAS - Revolucion {revolution_count}")
                print("=" * 70)

                zone_counts = analyze_distance_zones(scan, SAFETY_ZONES)

                print("\n  Distribucion por zonas de seguridad:")
                for zone_name, zone_min, zone_max in SAFETY_ZONES:
                    count = zone_counts[zone_name]
                    percentage = (count / total * 100) if total > 0 else 0

                    # Barra visual
                    bar_length = int((count / total * 40)) if total > 0 else 0
                    bar = "█" * bar_length

                    print(f"    {zone_name:8s} [{count:4d}] {bar} {percentage:5.1f}%")
                    print(f"             ({zone_min:5d} - {zone_max:5d} mm)")

                print("=" * 70)

    except KeyboardInterrupt:
        print("\n\nCtrl+C detectada por usuario.")
        print(f"Total de revoluciones procesadas: {revolution_count}")

    except Exception as e:
        print(f"\nError: {e}")

    finally:
        # =================================================================
        # PASO 5: Desconectar limpiamente
        # =================================================================
        client.disconnect()
        print("\nDesconectado correctamente")


if __name__ == "__main__":
    main()
