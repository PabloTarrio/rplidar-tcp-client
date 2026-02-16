"""
Ejemplo avanzado: Filtrado por calidad de mediciones LIDAR

Este script demuestra cómo filtrar puntos del LIDAR según su valor de
quality, que representa la confianza del sensor en cada medición

CONCEPTO: ¿Qué es quality?
==========================
EL RPLIDAR A1 asigna a cada punto un valor de calidad (0-15):
    - 0:     Sin medición válida o muy baja confianza
    - 1-5:   Calidad baja (superficies reflectantes, ángulos oblicuos)
    - 6-10:  Calidad media (condiciones normales)
    - 11-15: Calidad alta (superficies perpendiculares, buena reflectividad)

NOTA IMPORTANTE sobre modos:
    - Modo Standard: Quality disponible (0-15)
    - Modo Express:  Quality = None(no disponible para mayor velocidad)

CASOS DE USO:
=============
1. Navegación autónoma: Filtrar puntos con quality < 8 para evitar falsos positivos
2. Mapeo de precisión: Usar sólo puntos con quality >= 10
3. Análisis de superficies: Estudiar distribución de calidades por material
4. Debugging: Identificar zonas problemáticas del entorno.

EJERCICIOS SUGERIDOS:
=====================
1. Modifica MIN_QUALITY y observa como cambia el porcentaje de puntos validos
2. Crea un histograma que muestre la distribucion de calidades (0-15)
3. Compara el mismo entorno en modo Standard vs Express
4. Guarda solo puntos de alta calidad en un archivo CSV
5. Detecta objetos que generan consistentemente baja calidad
"""

from lidarclient import LidarClient
from lidarclient.config import ConfigError, load_config


def filter_by_quality(scan, min_quality=8):
    """
    Filtra los puntos de una revolución según calidad mínima

    Args:
        scan: Lista de tuplas (quality, angle, distance) de una revolución
        min_quality: Umbral mínimo de calidad (0-15). Por defecto 8.

    Returns:
        tuple: (puntos_filtrados, puntos_descartados)
            - puntos_filtrados: Lista de puntos que cumplen el criterio
            - puntos_descartados: Lista de puntos que NO cumplen el criterio

    Ejemplo:
        >>> scan = [(10, 45.5, 1200), (3, 90.0, 800), (12, 135.5, 1500)]
        >>> buenos, malos = filter_by_quality(scan, min_quality=8)
        >>> print(len(buenos))  # 2 puntos con quality >= 8
        2
    """

    puntos_filtrados = []
    puntos_descartados = []

    for point in scan:
        quality, angle, distance = point
        # ===========================================================
        # VERIFICACIÓN CRÍTICA: Modo Express no tiene quality
        # ===========================================================
        # En modo Express, quality es None para maximizar velocidad.
        # Debemos manejar este caso para evitar errores
        if quality is None:
            # En Express, no podemos filtrar por calidad
            # Consideramos todos los puntos como válidos si tienen distancia
            if distance > 0:
                puntos_filtrados.append(point)
            else:
                puntos_descartados.append(point)
        else:
            # En modo Standard, aplicamos el filtro de calidad
            if quality >= min_quality and distance > 0:
                puntos_filtrados.append(point)
            else:
                puntos_descartados.append(point)

    return puntos_filtrados, puntos_descartados


def analyze_quality_distribution(scan):
    """
    Analiza la distribución de calidades de una revolución

    Args:
        scan: Lista de tuplas (quality, angle, distance)

    Returns:
        dict: Diccionario con estadísticas de calidad
            - mode: Modo del LIDAR (standard o express)
            - distribution: Dict {quality: count} si está disponible
            - total_points: Total de puntos
            - valid_points: Puntos con distancia > 0
    """
    stats = {
        "mode": None,
        "distribution": {},
        "total_points": len(scan),
        "valid_points": 0,
    }

    if not scan:
        return stats

    # Detectar si quality está disponible
    first_quality = scan[0][0]

    if first_quality is None:
        # Modo Express
        stats["mode"] = "express"
        stats["valid_points"] = sum(1 for _, _, d in scan if d > 0)
    else:
        # Modo Standard
        stats["mode"] = "standard"

        # Contar distribución de calidades
        for quality, _, distance in scan:
            if distance > 0:  # Solo puntos con medición válida
                stats["valid_points"] += 1
                current = stats["distribution"].get(quality, 0)
                stats["distribution"][quality] = current + 1
    return stats


def print_quality_histogram(distribution):
    """
    Muestra un histograma visual de la distribución de calidades

    Args:
        distribution: Dict {quality: count} de analyze_quality_distribution()
    """

    if not distribution:
        print("  No hay datos de calidad disponibles (modo Express)")
        return

    print("\n  Histograma de Calidades:")
    print("  " + "=" * 50)

    # Encontrar el máximo para escalar las barras
    max_count = max(distribution.values()) if distribution else 1

    # Mostrar todas las calidades de 0 a 15
    for quality in range(16):
        count = distribution.get(quality, 0)

        # Barra visual (escala a 40 caracteres máximo)
        bar_length = int((count / max_count) * 40) if max_count > 0 else 0
        bar = "█" * bar_length  # Ubuntu: Ctrl+Shift+u ->
        #    2588 tras el caracter u subrayado
        # Windows: Alt+9608
        # Porcentaje
        total = sum(distribution.values())
        percentage = (count / total * 100) if total > 0 else 0

        print(f"  \tQ{quality:2d}  [{count:4d}]  {bar} {percentage:5.1f}%")


def main():
    """
    Función principal: Filtra puntos por calidad en tiempo real
    """
    # ===============================================================
    # PASO 1: Cargar configuración desde config.ini
    # ===============================================================
    try:
        config = load_config()
    except ConfigError as e:
        print(f"Error de configuración: {e}")
        return
    # ===============================================================
    # PASO 2: Configurar umbral de calidad
    # ===============================================================
    MIN_QUALITY = 8
    # Puedes modificar este valor segun tu aplicacion:
    #   - 5:  Filtrado suave (descarta solo lo peor)
    #   - 8:  Filtrado medio (recomendado para navegacion)
    #   - 10: Filtrado estricto (solo alta calidad)

    print("=" * 70)
    print("FILTRADO POR CALIDAD - RPLIDAR A1")
    print("=" * 70)
    print(f"Servidor: {config['host']}:{config['port']}")
    print(f"Modo de escaneo: {config['scan_mode']}")
    print(f"Umbral de calidad: >= {MIN_QUALITY}")
    print("\nPresiona Ctrl+C para detener")
    print("=" * 70)

    # ===============================================================
    # PASO 3: Conectar al servidor LIDAR
    # ===============================================================
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
        print(f"\n>Conectado a {config['host']}:{config['port']}")

        revolution_count = 0

        # ===========================================================
        # PASO 4: Procesar revoluciones continuamente
        # ===========================================================
        while True:
            # Obtener una revolución completa
            scan = client.get_scan()
            revolution_count += 1

            # -------------------------------------------------------
            # Filtrar por calidad
            # -------------------------------------------------------
            buenos, malos = filter_by_quality(scan, min_quality=MIN_QUALITY)

            # -------------------------------------------------------
            # Estadísticas básicas
            # -------------------------------------------------------
            total = len(scan)
            porcentaje_buenos = (len(buenos) / total * 100) if total > 0 else 0
            porcentaje_malos = (len(malos) / total * 100) if total > 0 else 0

            print(f"\nRev #{revolution_count:3d}")
            print(f"  Total:        {total:4d} puntos")
            print(
                f"  Buenos:       {len(buenos):4d} puntos "
                f"({porcentaje_buenos:5.1f}% - Quality >= {MIN_QUALITY})"
            )
            print(
                f"  Malos:        {len(malos):4d} puntos "
                f"({porcentaje_malos:5.1f}% - Quality < {MIN_QUALITY} ) "
                "o distancia = 0"
            )

            # -------------------------------------------------------
            # Calcular distancias solo de puntos buenos
            # -------------------------------------------------------

            if buenos:
                distancias_buenas = [d for _, _, d in buenos]
                dist_min = min(distancias_buenas)
                dist_max = max(distancias_buenas)
                dist_avg = sum(distancias_buenas) / len(distancias_buenas)

                print("\n  Distancias (solo puntos buenos):")
                print(f"    Minima:   {dist_min:7.1f} mm ({dist_min / 1000:.2f} m)")
                print(f"    Maxima:   {dist_max:7.1f} mm ({dist_max / 1000:.2f} m)")
                print(f"    Promedio: {dist_avg:7.1f} mm ({dist_avg / 1000:.2f} m)")

            # -------------------------------------------------------
            # Mostrar análisis de calidad cada 10 revoluciones
            # -------------------------------------------------------
            if revolution_count % 10 == 0:
                print("=" * 70)
                print(f"ANALISIS DE CALIDAD - Revolución {revolution_count}")
                print("=" * 70)

                stats = analyze_quality_distribution(scan)

                print(f"\nModo detectado: {stats['mode'].upper()}")
                print(f"   Total de puntos: {stats['total_points']}")
                print(f"   Puntos validos (distancia > 0): {stats['valid_points']}")

                if stats["mode"] == "standard":
                    print_quality_histogram(stats["distribution"])
                else:
                    print("\n   En modo Express no hay datos de calidad")
                    print("   Todos los puntos con distancia > 0 se consideran validos")

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
