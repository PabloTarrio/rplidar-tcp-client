"""
Ejemplo básico: obtener una revolución completa del LIDAR.
"""

from lidarclient.client import LidarClient


def main():
    # Conectar al servidor (ajusta la IP de tu Raspberry Pi)
    with LidarClient("192.168.1.100", port=5000) as client:
        # Obtener una revolución completa
        scan = client.get_scan()

        print("=== Revolución completa recibida ===")  # Quitado f-string
        print(f"Total de puntos: {len(scan)}")

        # Filtrar puntos válidos (distancia > 0)
        valid_points = [(q, a, d) for q, a, d in scan if d > 0]
        print(f"Puntos válidos: {len(valid_points)}")

        if valid_points:
            distances = [d for _, _, d in valid_points]
            print(f"Distancia mínima: {min(distances):.1f} mm")
            print(f"Distancia máxima: {max(distances):.1f} mm")

        # Mostrar primeros 5 puntos
        print("\n=== Primeros 5 puntos ===")  # Quitado f-string
        for i, (quality, angle, distance) in enumerate(scan[:5], 1):
            # Línea dividida para no superar 88 caracteres
            print(
                f"{i}. Calidad: {quality:2d}, Ángulo: {angle:6.2f}°, "
                f"Distancia: {distance:7.2f} mm"
            )


if __name__ == "__main__":
    main()
