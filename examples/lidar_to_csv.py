"""
Guardar revoluciones del LIDAR en un CSV

- Lee config.ini (host, port, timeout, max_retries, retry_delay, scan_mode)
- Captura N revoluciones
- Guarda 1 fila por punto en CSV
"""

from __future__ import annotations

import argparse
import csv
from datetime import datetime, timezone
from pathlib import Path

from lidarclient import LidarClient
from lidarclient.config import ConfigError, load_config

# 1 fila por punto del LIDAR.
# Repetimos timestamp_iso y scan_mode en todas las filas de una revolución
# para que sea fácil agrupar luego (por ejemplo en pandas).

CSV_COLUMNS = [
    "timestamp_iso",
    "scan_mode",
    "rev_index",
    "point_index",
    "angle_deg",
    "distance_mm",
    "quality",
]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Guardar datos LIDAR en CSV.")

    parser.add_argument(
        "--revs",
        type=int,
        default=3,
        help="Número de revoluciones a capturar (default: 3)",
    )

    parser.add_argument(
        "--out",
        type=Path,
        default=Path("lidar_scans.csv"),
        help="Ruta de salida del CSV (default: lidar_scans.csv)",
    )

    return parser.parse_args()


def main() -> int:
    try:
        config = load_config()
    except ConfigError as e:
        print(f"Error de configuración: {e}")
        return 2

    client = LidarClient(
        config["host"],
        port=config["port"],
        timeout=config["timeout"],
        max_retries=config["max_retries"],
        retry_delay=config["retry_delay"],
        scan_mode=config["scan_mode"],
    )

    args = parse_args()
    if args.revs <= 0:
        print("Error: --revs debe ser > 0")
        return 2

    out_path = args.out
    out_path.parent.mkdir(parents=True, exist_ok=True)

    try:
        client.connect_with_retry()
        print(f"Conectando a {config['host']}:{config['port']}")
        print(f"Modo de escaneo: {config['scan_mode']}")
        print(f"Capturando {args.revs} revoluciones...")

        with out_path.open("w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=CSV_COLUMNS)
            writer.writeheader()

            total_points = 0

            for rev_index in range(args.revs):
                # Timestamp de esta revolución (UTC).
                # Se repite en todas las filas de la misma rev
                timestamp_iso = datetime.now(timezone.utc).isoformat()
                scan = client.get_scan()

                for point_index, (quality, angle, distance) in enumerate(scan):
                    # En modo Express, 'quality' puede venir como None, así que
                    #       lo guardamos vacío en el CSV.
                    row = {
                        "timestamp_iso": timestamp_iso,
                        "scan_mode": config["scan_mode"],
                        "rev_index": rev_index,
                        "point_index": point_index,
                        "angle_deg": angle,
                        # distance_mm = 0 -> medición no válida en ese punto.
                        "distance_mm": distance,
                        "quality": "" if quality is None else quality,
                    }
                    writer.writerow(row)

                total_points += len(scan)
                print(f"  Rev {rev_index + 1}/{args.revs}:{len(scan)} puntos")

        print(f"\nCSV guardado en: {out_path.resolve()}")
        print(f"Total filas (puntos): {total_points}")
        return 0

    except KeyboardInterrupt:
        print("\nInterrumpido por el usuario")
        return 130
    except Exception as e:
        print(f"Error: {e}")
        return 1
    finally:
        client.disconnect()


if __name__ == "__main__":
    raise SystemExit(main())
