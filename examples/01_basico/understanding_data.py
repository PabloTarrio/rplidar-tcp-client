"""
=============================================================================
EJEMPLO 1B: Entendiendo los Datos del LIDAR
=============================================================================

OBJETIVO:
    Comprender en profundidad el formato de datos que devuelve el LIDAR
    y como interpretar cada campo (calidad, angulo, distancia).

REQUISITOS PREVIOS:
    - Haber completado simple_scan.py
    - Entender que es una tupla en Python

CONCEPTOS QUE APRENDERAS:
    - Diferencia entre modo Standard y Express
    - Que significa cada campo de la tupla
    - Como identificar mediciones invalidas
    - Por que algunos puntos tienen quality=None

TIEMPO ESTIMADO: 15 minutos
=============================================================================
"""

from lidarclient import LidarClient
from lidarclient.config import ConfigError, load_config


def analyze_data_format(scan, scan_mode):
    """
    Analiza y explica el formato de datos de una revolucion LIDAR.

    Args:
        scan: Lista de tuplas (quality, angle, distance)
        scan_mode: String 'Standard' o 'Express'
    """
    print("\n" + "=" * 77)
    print("ANALISIS DEL FORMATO DE DATOS")
    print("=" * 77)

    # =========================================================================
    # 1. ESTRUCTURA BASICA
    # =========================================================================
    print("\n1. ESTRUCTURA DE LOS DATOS")
    print("-" * 77)
    print(f"   Tipo de dato: {type(scan)}")
    print(f"   Numero de elementos: {len(scan)}")
    print("   Cada elemento es una tupla de 3 valores: (quality, angle, distance)")

    if scan:
        first_point = scan[0]
        print("\n   Ejemplo del primer punto:")
        print(f"     Tupla completa: {first_point}")
        print(f"     - Tipo: {type(first_point)}")
        print(f"     - Longitud: {len(first_point)}")

    # =========================================================================
    # 2. CAMPO QUALITY (Calidad)
    # =========================================================================
    print("\n2. CAMPO QUALITY (Calidad de la medicion)")
    print("-" * 77)

    qualities = [p[0] for p in scan if p[0] is not None]

    if qualities:
        print(f"   Modo: {scan_mode} - Quality DISPONIBLE")
        print("   Rango de valores: 0 (baja confianza) a 15 (maxima confianza)")
        print("\n   Estadisticas de calidad en esta revolucion:")
        print(f"     - Minima: {min(qualities)}")
        print(f"     - Maxima: {max(qualities)}")
        print(f"     - Promedio: {sum(qualities) / len(qualities):.2f}")

        # Distribucion de calidades
        quality_dist = {}
        for q in qualities:
            quality_dist[q] = quality_dist.get(q, 0) + 1

        print("\n   Distribucion de calidades:")
        for q in sorted(quality_dist.keys()):
            bar = "#" * (quality_dist[q] // 10)
            print(f"     Calidad {q:2d}: {quality_dist[q]:4d} puntos {bar}")
    else:
        print(f"   Modo: {scan_mode} - Quality NO DISPONIBLE (None)")
        print("   En modo Express, el LIDAR no envia datos de calidad")
        print("   para poder capturar mas puntos por segundo.")
        print(f"   Todos los valores de quality son: {scan[0][0]}")

    # =========================================================================
    # 3. CAMPO ANGLE (Angulo)
    # =========================================================================
    print("\n3. CAMPO ANGLE (Angulo en grados)")
    print("-" * 77)

    angles = [p[1] for p in scan]
    print("   Rango de valores: 0.0 a 360.0 grados")
    print("   Referencia: 0 = Frente del LIDAR, rotacion horaria")
    print("\n   Estadisticas de angulos en esta revolucion:")
    print(f"     - Minimo: {min(angles):.2f}")
    print(f"     - Maximo: {max(angles):.2f}")
    print(f"     - Cobertura angular: {max(angles) - min(angles):.2f}")

    # Verificar si la cobertura es completa
    coverage = max(angles) - min(angles)
    if coverage > 350:
        print("     - Cobertura: COMPLETA (360)")
    else:
        print(f"     - Cobertura: PARCIAL ({coverage:.1f})")

    # =========================================================================
    # 4. CAMPO DISTANCE (Distancia)
    # =========================================================================
    print("\n4. CAMPO DISTANCE (Distancia en milimetros)")
    print("-" * 77)

    all_distances = [p[2] for p in scan]
    valid_distances = [d for d in all_distances if d > 0]
    invalid_count = len([d for d in all_distances if d == 0])

    print("   Rango de valores: 0 a ~12000 mm (0 a 12 metros)")
    print("   Valor 0: Sin medicion valida (objeto fuera de rango o transparente)")
    print("\n   Estadisticas de distancia:")
    print(f"     - Puntos validos (>0): {len(valid_distances)}")
    print(f"     - Puntos invalidos (=0): {invalid_count}")

    if valid_distances:
        print(f"     - Distancia minima: {min(valid_distances):.1f} mm")
        print(f"     - Distancia maxima: {max(valid_distances):.1f} mm")
        print(
            "     - Distancia promedio:"
            " {sum(valid_distances) / len(valid_distances):.1f} mm"
        )

    # =========================================================================
    # 5. EJEMPLOS DE ACCESO A LOS DATOS
    # =========================================================================
    print("\n5. COMO ACCEDER A LOS DATOS EN PYTHON")
    print("-" * 77)
    print("""
   Forma 1: Desempaquetar la tupla
     for quality, angle, distance in scan:
         print(f"Q={quality}, A={angle}, D={distance}")
   
   Forma 2: Acceder por indice
     for point in scan:
         quality = point[0]
         angle = point[1]
         distance = point[2]
   
   Forma 3: Filtrar con list comprehension
     valid = [p for p in scan if p[2] > 0]
     close = [p for p in scan if 0 < p[2] < 1000]
     front = [p for p in scan if 330 <= p[1] or p[1] <= 30]
    """)


def show_sample_points(scan, count=10):
    """
    Muestra una muestra de puntos para visualizar el formato.

    Args:
        scan: Lista de tuplas (quality, angle, distance)
        count: Numero de puntos a mostrar
    """
    print("\n" + "=" * 77)
    print(f"MUESTRA DE {count} PUNTOS")
    print("=" * 77)
    print("\n  N  | Quality | Angle      | Distance    | Valido")
    print("-" * 77)

    for i, (quality, angle, distance) in enumerate(scan[:count], 1):
        q_str = f"{quality:2d}" if quality is not None else "--"
        valid = "SI" if distance > 0 else "NO"
        print(f" {i:3d} | {q_str:7s} | {angle:6.2f} | {distance:8.1f} mm | {valid}")


def main():
    """
    Funcion principal que captura datos y los analiza en detalle.
    """
    print("=" * 77)
    print("TUTORIAL: ENTENDIENDO LOS DATOS DEL LIDAR")
    print("=" * 77)

    # Cargar configuracion
    try:
        config = load_config()
    except ConfigError as e:
        print(f"\nError de configuracion: {e}")
        return

    print(f"\nConexion: {config['host']}:{config['port']}")
    print(f"Modo de escaneo: {config['scan_mode']}")

    # Crear cliente y conectar
    client = LidarClient(
        config["host"],
        port=config["port"],
        timeout=config["timeout"],
        max_retries=config["max_retries"],
        retry_delay=config["retry_delay"],
        scan_mode=config["scan_mode"],
    )

    try:
        print("\nConectando al servidor LIDAR...")
        client.connect_with_retry()
        print("Conectado correctamente")

        # Obtener revolucion
        print("\nCapturando revolucion...")
        scan = client.get_scan()
        print(f"Revolucion recibida: {len(scan)} puntos")

        # Analizar formato de datos
        analyze_data_format(scan, config["scan_mode"])

        # Mostrar muestra de puntos
        show_sample_points(scan, count=10)

        # Resumen final
        print("\n" + "=" * 77)
        print("RESUMEN")
        print("=" * 77)
        print(f"""
   Cada revolucion es una lista de {len(scan)} tuplas.
   Cada tupla tiene 3 elementos: (quality, angle, distance)
   
   - quality: Confianza de la medicion (0-15 o None)
   - angle: Direccion en grados (0-360)
   - distance: Distancia en milimetros (0 = invalido)
   
   Modo {config["scan_mode"]}:
     - Puntos por revolucion: ~{len(scan)}
     - Calidad disponible: {"SI" if scan[0][0] is not None else "NO"}
        """)

        client.disconnect()
        print("\nTutorial completado con exito")

    except KeyboardInterrupt:
        print("\n\nInterrupcion detectada")
        client.disconnect()

    except Exception as e:
        print(f"\nError: {e}")
        client.disconnect()


# =============================================================================
# EJERCICIOS PARA PRACTICAR:
# =============================================================================
#
# 1. Modifica analyze_data_format() para calcular la "densidad angular":
#    cuantos puntos hay por cada grado de rotacion
#
# 2. Crea una funcion que identifique "huecos" en los datos:
#    rangos de angulos donde no hay mediciones validas (distance=0)
#
# 3. Si estas en modo Standard, crea un histograma de calidades
#    mostrando cuantos puntos hay en cada nivel (0-15)
#
# 4. Compara 2 revoluciones capturadas en diferentes modos (Standard/Express)
#    y documenta las diferencias en formato, cantidad de datos, etc.
#
# =============================================================================

if __name__ == "__main__":
    main()
