"""
Ejemplo básico: obtener una revolución completa del LIDAR.

Lee la configuración desde config.ini para obtener la IP del servidor LIDAR.
"""

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
    )

    try:
        client.connect_with_retry()
        print(f"Conectado a {config['host']}:{config['port']}")

        # Solicitar una revolución completa
        print("Solicitando revolución...")
        scan = client.get_scan()

        print("\nRevolución completa recibida")
        print(f"Total de puntos: {len(scan)}")

        # Filtrar puntos válidos (distancia > 0)
        valid_points = [point for point in scan if point[2] > 0]
        print(f"Puntos válidos: {len(valid_points)}")

        if valid_points:
            distances = [d for _, _, d in valid_points]
            print(f"Distancia mínima: {min(distances):.1f} mm")
            print(f"Distancia máxima: {max(distances):.1f} mm")

            print("\nPrimeros 5 puntos:")
            for i, (quality, angle, distance) in enumerate(valid_points[:5], 1):
                print(
                    f"{i}. Calidad {quality:2d}, "
                    f"Ángulo {angle:6.2f}°, "
                    f"Distancia {distance:7.2f} mm"
                )

        client.disconnect()

    except Exception as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    main()
