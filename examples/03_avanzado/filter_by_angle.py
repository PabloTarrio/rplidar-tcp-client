"""
Ejemplo avanzado: Filtrado por sector angular.

Este script demuestra como filtrar puntos del LIDAR segun su angulo,
permitiendo definir sectores especificos de interes.

CONCEPTO: Angulo en el LIDAR
=============================
El RPLIDAR A1 reporta angulos en grados (0-360):
  - 0 grados:   Frente del LIDAR (marca roja del sensor)
  - 90 grados:  Derecha del LIDAR
  - 180 grados: Atras del LIDAR
  - 270 grados: Izquierda del LIDAR
  - Rotacion:   Sentido horario (visto desde arriba)

CASOS DE USO:
=============
1. Navegacion direccional: Detectar solo obstaculos al frente (330-30 grados)
2. Vision lateral: Monitorizar solo los lados (80-100 y 260-280 grados)
3. Deteccion trasera: Alertar de obstaculos atras (160-200 grados)
4. Campo de vision: Simular sensor con angulo limitado (ejemplo: 180 grados)
5. Zonas ciegas: Ignorar sectores bloqueados por la estructura del robot

EJERCICIOS SUGERIDOS:
=====================
1. Modifica FRONT_SECTOR para cambiar el campo de vision frontal
2. Define multiples sectores y cuenta puntos en cada uno
3. Detecta el punto mas cercano solo en el sector frontal
4. Crea una alerta si hay obstaculos en los laterales
5. Simula un sensor de vision limitada (90 o 180 grados)
"""

from lidarclient import LidarClient
from lidarclient.config import ConfigError, load_config


def normalize_angle(angle):
    """
    Normaliza un angulo al rango [0, 360).

    Args:
        angle: Angulo en grados (puede ser negativo o > 360)

    Returns:
        float: Angulo normalizado entre 0 y 360

    Ejemplo:
        >>> normalize_angle(-10)
        350.0
        >>> normalize_angle(370)
        10.0
    """
    return angle % 360


def is_angle_in_sector(angle, sector_start, sector_end):
    """
    Verifica si un angulo esta dentro de un sector.

    Maneja correctamente sectores que cruzan el 0 (ejemplo: 350-10 grados).

    Args:
        angle: Angulo a verificar (0-360)
        sector_start: Inicio del sector en grados
        sector_end: Fin del sector en grados

    Returns:
        bool: True si el angulo esta en el sector

    Ejemplo:
        >>> is_angle_in_sector(5, 350, 10)  # Sector que cruza 0
        True
        >>> is_angle_in_sector(45, 30, 60)  # Sector normal
        True
    """
    # Normalizar angulos
    angle = normalize_angle(angle)
    sector_start = normalize_angle(sector_start)
    sector_end = normalize_angle(sector_end)

    # Caso 1: Sector normal (no cruza 0)
    if sector_start <= sector_end:
        return sector_start <= angle <= sector_end

    # Caso 2: Sector que cruza 0 grados (ejemplo: 350-10)
    else:
        return angle >= sector_start or angle <= sector_end


def filter_by_angle(scan, sector_start, sector_end):
    """
    Filtra los puntos de una revolucion segun sector angular.

    Args:
        scan: Lista de tuplas (quality, angle, distance) de una revolucion
        sector_start: Angulo inicial del sector en grados (0-360)
        sector_end: Angulo final del sector en grados (0-360)

    Returns:
        tuple: (puntos_en_sector, puntos_fuera_sector)
            - puntos_en_sector: Puntos dentro del sector definido
            - puntos_fuera_sector: Puntos fuera del sector

    Ejemplo:
        >>> scan = [(15, 5.0, 1000), (15, 90.0, 1500), (15, 350.0, 800)]
        >>> en_sector, fuera = filter_by_angle(scan, 350, 10)
        >>> len(en_sector)  # Puntos a 5 y 350 grados estan en sector
        2
    """
    puntos_en_sector = []
    puntos_fuera_sector = []

    for point in scan:
        quality, angle, distance = point

        # Ignorar puntos sin medicion valida
        if distance == 0:
            continue

        # Verificar si el angulo esta en el sector
        if is_angle_in_sector(angle, sector_start, sector_end):
            puntos_en_sector.append(point)
        else:
            puntos_fuera_sector.append(point)

    return puntos_en_sector, puntos_fuera_sector


def filter_by_multiple_sectors(scan, sectors):
    """
    Filtra puntos segun multiples sectores definidos.

    Args:
        scan: Lista de tuplas (quality, angle, distance)
        sectors: Lista de tuplas (nombre, start, end)

    Returns:
        dict: {nombre_sector: lista_puntos}

    Ejemplo:
        >>> sectors = [
        ...     ("Frente", 330, 30),
        ...     ("Derecha", 60, 120),
        ...     ("Atras", 150, 210),
        ...     ("Izquierda", 240, 300)
        ... ]
        >>> resultado = filter_by_multiple_sectors(scan, sectors)
    """
    sector_points = {name: [] for name, _, _ in sectors}
    sector_points["Sin_clasificar"] = []

    for point in scan:
        quality, angle, distance = point

        if distance == 0:
            continue

        # Intentar clasificar en alguno de los sectores
        classified = False
        for sector_name, sector_start, sector_end in sectors:
            if is_angle_in_sector(angle, sector_start, sector_end):
                sector_points[sector_name].append(point)
                classified = True
                break

        if not classified:
            sector_points["Sin_clasificar"].append(point)

    return sector_points


def find_closest_in_sector(points):
    """
    Encuentra el punto mas cercano dentro de un conjunto de puntos.

    Args:
        points: Lista de tuplas (quality, angle, distance)

    Returns:
        tuple: (quality, angle, distance) del punto mas cercano
               o None si no hay puntos
    """
    if not points:
        return None

    closest = min(points, key=lambda p: p[2])
    return closest


def main():
    """
    Funcion principal: Filtra puntos por angulo en tiempo real.
    """
    # =====================================================================
    # PASO 1: Cargar configuracion desde config.ini
    # =====================================================================
    try:
        config = load_config()
    except ConfigError as e:
        print(f"Error de configuracion: {e}")
        return

    # =====================================================================
    # PASO 2: Definir sectores de interes
    # =====================================================================
    # Puedes modificar estos valores segun tu aplicacion:
    #
    # Para navegacion frontal:
    #   SECTOR_START = 330  (30 grados a la izquierda del frente)
    #   SECTOR_END = 30     (30 grados a la derecha del frente)
    #   Total: 60 grados de campo de vision frontal
    #
    # Para vision hemisferica frontal (180 grados):
    #   SECTOR_START = 270  (izquierda)
    #   SECTOR_END = 90     (derecha)
    #
    # Para deteccion trasera:
    #   SECTOR_START = 150
    #   SECTOR_END = 210
    #
    SECTOR_START = 330  # grados
    SECTOR_END = 30  # grados

    # Definir sectores multiples para analisis detallado
    MULTI_SECTORS = [
        ("FRENTE", 330, 30),  # ±30 grados del frente
        ("DERECHA", 60, 120),  # Lateral derecho
        ("ATRAS", 150, 210),  # Parte trasera
        ("IZQUIERDA", 240, 300),  # Lateral izquierdo
    ]

    print("=" * 70)
    print("FILTRADO POR ANGULO - RPLIDAR A1")
    print("=" * 70)
    print(f"Servidor: {config['host']}:{config['port']}")
    print(f"Modo de escaneo: {config['scan_mode']}")
    print(f"Sector principal: {SECTOR_START}° - {SECTOR_END}°")

    # Calcular amplitud del sector
    if SECTOR_START <= SECTOR_END:
        amplitud = SECTOR_END - SECTOR_START
    else:
        amplitud = (360 - SECTOR_START) + SECTOR_END

    print(f"Amplitud del sector: {amplitud}°")
    print("\nPresiona Ctrl+C para detener")
    print("=" * 70)

    # =====================================================================
    # PASO 3: Conectar al servidor LIDAR
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
            # Obtener una revolucion completa
            scan = client.get_scan()
            revolution_count += 1

            # -------------------------------------------------------------
            # Filtrar por sector principal
            # -------------------------------------------------------------
            en_sector, fuera_sector = filter_by_angle(scan, SECTOR_START, SECTOR_END)

            # -------------------------------------------------------------
            # Estadisticas basicas
            # -------------------------------------------------------------
            total_validos = len(en_sector) + len(fuera_sector)
            porcentaje_sector = (
                (len(en_sector) / total_validos * 100) if total_validos > 0 else 0
            )

            print(f"\nRev #{revolution_count:3d}")
            print(f"  Total validos:    {total_validos:4d} puntos")
            print(
                f"  En sector:        {len(en_sector):4d} puntos "
                f"({porcentaje_sector:5.1f}%)"
            )
            print(f"  Fuera de sector:  {len(fuera_sector):4d} puntos")

            # -------------------------------------------------------------
            # Punto mas cercano EN EL SECTOR (critico para navegacion)
            # -------------------------------------------------------------
            closest_in_sector = find_closest_in_sector(en_sector)
            if closest_in_sector:
                q, ang, dist = closest_in_sector
                print(
                    "\n  Punto mas cercano en sector [{SECTOR_START}°-{SECTOR_END}°]:"
                )
                print(f"    Distancia: {dist:7.1f} mm ({dist / 1000:.3f} m)")
                print(f"    Angulo:    {ang:6.1f}°")

                # Alerta si esta muy cerca
                if dist < 500:
                    print("    >>> ALERTA: OBSTACULO FRONTAL CERCANO! <<<")
            else:
                print(f"\n  Sin obstaculos en sector [{SECTOR_START}°-{SECTOR_END}°]")

            # -------------------------------------------------------------
            # Estadisticas del sector
            # -------------------------------------------------------------
            if en_sector:
                distancias = [d for _, _, d in en_sector]
                dist_min = min(distancias)
                dist_max = max(distancias)
                dist_avg = sum(distancias) / len(distancias)

                print("\n  Estadisticas del sector:")
                print(
                    f"    Dist. minima:  {dist_min:7.1f} mm ({dist_min / 1000:.2f} m)"
                )
                print(
                    f"    Dist. maxima:  {dist_max:7.1f} mm ({dist_max / 1000:.2f} m)"
                )
                print(
                    f"    Dist. promedio: {dist_avg:7.1f} mm ({dist_avg / 1000:.2f} m)"
                )

            # -------------------------------------------------------------
            # Analisis multi-sector cada 10 revoluciones
            # -------------------------------------------------------------
            if revolution_count % 10 == 0:
                print("\n" + "=" * 70)
                print(f"ANALISIS MULTI-SECTOR - Revolucion {revolution_count}")
                print("=" * 70)

                sector_data = filter_by_multiple_sectors(scan, MULTI_SECTORS)

                print("\n  Distribucion por sectores:")
                for sector_name, sector_start, sector_end in MULTI_SECTORS:
                    points = sector_data[sector_name]
                    count = len(points)
                    percentage = (
                        (count / total_validos * 100) if total_validos > 0 else 0
                    )

                    # Barra visual
                    bar_length = (
                        int((count / total_validos * 40)) if total_validos > 0 else 0
                    )
                    bar = "█" * bar_length

                    print(
                        f"    {sector_name:10s} [{count:4d}] {bar} {percentage:5.1f}%"
                    )
                    print(f"                ({sector_start:3d}° - {sector_end:3d}°)")

                    # Punto mas cercano en este sector
                    closest = find_closest_in_sector(points)
                    if closest:
                        _, _, dist = closest
                        print(f"                Mas cercano: {dist:.0f} mm")

                # Puntos sin clasificar
                unclassified = sector_data["Sin_clasificar"]
                if unclassified:
                    print(
                        f"\n    Sin clasificar: {len(unclassified)} puntos "
                        "(fuera de todos los sectores)"
                    )

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
