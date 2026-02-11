"""
Ejemplo avanzado: stream continuo de revoluciones con reconexión automática.

Este ejemplo usa connect_with_retry() para intentar conectarse automáticamente
hasta 3 veces si el servidor no está disponible.

Presiona Ctrl+C para detener.
"""

import time

from lidarclient.client import LidarClient


def main():
    client = LidarClient("192.168.1.100", port=5000, max_retries=3, retry_delay=2.0)

    try:
        client.connect_with_retry()
        print("Conectado al servidor LIDAR")
        print("Presiona Ctrl+C para detener\n")

        revolution_count = 0

        while True:
            # Obtener revolución
            scan = client.get_scan()
            revolution_count += 1

            # Filtrar puntos válidos
            valid = [(q, a, d) for q, a, d in scan if d > 0]

            # Estadísticas básicas
            if valid:
                distances = [d for _, _, d in valid]
                avg_dist = sum(distances) / len(distances)
                print(
                    f"Rev #{revolution_count:3d}: "
                    f"Puntos={len(scan):3d} "
                    f"Válidos={len(valid):3d} "
                    f"Dist.Media={avg_dist:7.1f}mm "
                    f"Min={min(distances):6.1f}mm "
                    f"Max={max(distances):6.1f}mm"
                )
            else:
                print(f"Rev #{revolution_count:3d}: Sin puntos válidos")

            time.sleep(0.1)  # Pequeña pausa para no saturar

    except KeyboardInterrupt:
        print(f"\n\nDetenido por usuario. Total revoluciones: {revolution_count}")
    finally:
        client.disconnect()
        print("Desconectado del servidor")


if __name__ == "__main__":
    main()
