"""
Comparación entre los diferentes modos de escaneo de
SLAMTEC RPLIDAR A1

Compara Standard Scan vs Express Scan mostrando:
    - Número de puntos por revolución
    - Calidad promedio
    - Cobertura angular
    - Tiempo por revolución
"""

import time

from lidarclient import ConfigError, LidarClient, load_config


def analyze_scan(scan, mode_name):
    """
    Analiza una revolución y muestra estadísticas

    Args:
        scan: Lista de tuplas (calidad, ángulo, distancia)
        mode_name: Nombre del modo para mostrar
    """

    total_points = len(scan)
    valid_points = sum(1 for _, _, d in scan if d > 0)

    if valid_points > 0:
        qualities = [q for q, _, d in scan if d > 0 and q is not None]
        distances = [d for _, _, d in scan if d > 0]
        angles = [a for _, a, d in scan if d > 0]

        valid_pct = valid_points / total_points * 100

        # Calcular calidad promedio solo si hay datos de calidad
        if qualities:
            avg_quality = sum(qualities) / len(qualities)
        else:
            avg_quality = None

        min_angle = min(angles)
        max_angle = max(angles)
        angular_coverage = max_angle - min_angle

        print(f"\n{'=' * 60}")
        print(f"   {mode_name}")
        print(f"{'=' * 60}")
        print(f" Total de puntos:    {total_points}")
        print(f" Puntos válidos:     {valid_points} ({valid_pct:.1f}%)")
        if avg_quality is not None:
            print(f" Calidad promedio:   {avg_quality:.2f} / 15")
        else:
            print(" Calidad promedio:   No disponible (modo Express)")
        print(f" Cobertura angular:  {angular_coverage:.1f}")
        print(f" Distancia mínima:   {min(distances):.1f} mm")
        print(f" Distancia máxima:   {max(distances):.1f} mm")
        print(
            f" Densidad:           {valid_points / angular_coverage:.2f} puntos/grado"
        )
        print(f"{'=' * 60}")
    else:
        print(f"\n{mode_name}: Sin datos válidos")


def main():
    """Función principal"""
    print("\n" + "=" * 60)
    print("   COMPARACIÓN DE MODOS DE ESCANEO RPLIDAR A1")
    print("=" * 60)

    # Cargar configuración
    try:
        config = load_config()
    except ConfigError as e:
        print(f" Error de configuración: {e}")
        return

    # Crear cliente
    client = LidarClient(
        config["host"],
        port=config["port"],
        timeout=config["timeout"],
        max_retries=config["max_retries"],
        retry_delay=config["retry_delay"],
        scan_mode=config["scan_mode"],
    )

    try:
        # Conectar
        print(f"\nConectando a {config['host']}:{config['port']}")
        client.connect()
        print("Conectado\n")

        # Descartar primera revolución (warmup del sistema)
        print("Descartando primera revolución (warmup)...")
        _ = client.get_scan()
        print("Warmup completado\n")

        # Obtener 3 revoluciones para promediar
        print("Capturando 3 revoluciones para análisis...")

        scans = []
        for i in range(3):
            print(f"   Revolución {i + 1}/3...", end="r")
            start_time = time.time()
            scan = client.get_scan()
            elapsed = time.time() - start_time
            scans.append((scan, elapsed))

        print("\n")

        # Analizar cada revolución
        for idx, (scan, elapsed) in enumerate(scans, 1):
            analyze_scan(scan, f"Revolución #{idx} (Tiempo: {elapsed:.3f}s)")

        avg_points = sum(len(s) for s, _ in scans) / len(scans)
        avg_valid = sum(sum(1 for _, _, d in s if d > 0) for s, _ in scans) / len(scans)
        avg_time = sum(t for _, t in scans) / len(scans)

        print(f"\n{'=' * 60}")
        print("  PROMEDIOS DE 3 REVOLUCIONES")
        print(f"{'=' * 60}")
        print(f"  Puntos promedio:      {avg_points:.1f}")
        print(f"  Válidos promedio:     {avg_valid:.1f}")
        print(f"  Tiempo promedio:      {avg_time:.3f}s")
        print(f"  Frecuencia:           {1 / avg_time:.2f} Hz")
        print(f"{'=' * 60}\n")

        # Información adicional
        print("\nINFORMACIÓN SOBRE MODOS DE ESCANEO:")
        print("\n   El servidor actual usa el modo por defecto de rplidar-roboticia.")
        print("    Este modo suele ser 'Express Scan' que proporciona mayor densidad.")
        print("\nNOTA SOBRE LA PRIMERA REVOLUCIÓN:")
        print("     La primera revolución tras conectar siempre tarda más (~1s).")
        print("     Esto es normal: el sistema se sincroniza con el LIDAR")
        print("     Este script descarta automáticamente esa primera revolución")

        print("\n  RPLIDAR A1 especificaciones típicas:")
        print("    - Standard Scan:  ~360 muestras/revolución")
        print("    - Express Scan:   ~720 muestras/revolución")
        print("    - Velocidad:      5-10 Hz (revoluciones/segundo)")

    except KeyboardInterrupt:
        print("\n\nInterrupción detectada")
    except Exception as e:
        print(f"\nError: {e}")
    finally:
        client.disconnect()
        print("\nAnálisis finalizado\n")


if __name__ == "__main__":
    main()
