"""
Ejemplo avanzado: stream continuo de revoluciones con reconexión automática.

Lee la configuración desde config.ini para obtener la IP del servidor LIDAR.

Presiona Ctrl+C para detener.
"""

import time

from lidarclient import LidarClient
from lidarclient.config import ConfigError, load_config


def main():
    # Cargar configuración desde config.ini
    try:
        config = load_config()
    except ConfigError as e:
        print(f"Error de configuración: {e}")
        return

    # Crear cliente con la configuración cargada
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
        print("Conectado al servidor LIDAR")
        print(f"Servidor: {config['host']}:{config['port']}")
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
                    f"Max={max(distances):7.1f}mm"
                )
            else:
                print(f"Rev #{revolution_count:3d}: Sin puntos válidos")

            time.sleep(0.1)

    except KeyboardInterrupt:
        print("\n\nInterrupción detectada por usuario.")
        print(f"Total revoluciones: {revolution_count}")
    finally:
        client.disconnect()


if __name__ == "__main__":
    main()
