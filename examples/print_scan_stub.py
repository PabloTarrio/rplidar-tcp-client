"""
Ejemplo de stream continuo con formato compatible ROS 2 LaserScan.

Este script obtiene revoluciones del LIDAR de forma continua y muestra
estadísticas en formato similar a los mensajes sensor_msgs/LaserScan de ROS 2:
- Número total de mediciones (ranges)
- Mediciones válidas (finite)
- Rango de distancias (min/max en metros)
- Rango angular (angle_min/max en radianes)

Útil para:
- Migrar código existente de ROS 2 a TCP
- Debugging y verificación de cobertura angular
- Monitorizar calidad de mediciones en tiempo real
"""

import math

from lidar_client import LidarClient


def on_scan(scan):
    """
    Procesa una revolución del LIDAR y muestra estadísticas.

    Simula el comportamiento de un callback ROS 2 que recibe mensajes
    sensor_msgs/LaserScan, pero usando datos directos del LIDAR vía TCP.

    Args:
        scan: Lista de tuplas (quality, angle, distance)
              - quality: 0-15 (confianza de la medición)
              - angle: 0-360 grados
              - distance: milímetros (0 = sin medición)
    """
    # Convertir a lista de distancias en metros (formato ROS estándar)
    ranges = [distance / 1000.0 for _, _, distance in scan]

    # Calcular ángulos en radianes (formato ROS estándar)
    angles = [angle for _, angle, _ in scan]
    angle_min = math.radians(min(angles)) if angles else 0.0
    angle_max = math.radians(max(angles)) if angles else 0.0

    # Filtrar solo mediciones válidas (distancia > 0)
    finite = [r for r in ranges if math.isfinite(r) and r > 0]

    if finite:
        print(
            f"ranges={len(ranges)} finite={len(finite)} "
            f"min={min(finite):.3f}m max={max(finite):.3f}m "
            f"angle_min={angle_min:.3f} rad "
            f"angle_max={angle_max:.3f} rad"
        )
    else:
        print(
            f"ranges={len(ranges)} finite=0 "
            f"angle_min={angle_min:.3f} rad "
            f"angle_max={angle_max:.3f} rad"
        )


def main():
    """
    Conecta al servidor LIDAR y procesa revoluciones continuamente.

    Reemplaza el comportamiento de un nodo ROS 2 que se suscribe al
    topic /scan, pero usando conexión TCP directa sin ROS.
    """
    # Ajusta la IP a la de tu Raspberry Pi
    with LidarClient("192.168.1.100", port=5000) as client:
        try:
            print("Conectado al servidor LIDAR")
            print("Mostrando estadísticas de escaneo (formato LaserScan)")
            print("Presiona Ctrl+C para detener\n")

            while True:
                scan = client.get_scan()
                on_scan(scan)

        except KeyboardInterrupt:
            print("\nDetenido por usuario")


if __name__ == "__main__":
    main()
