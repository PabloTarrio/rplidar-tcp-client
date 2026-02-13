"""
Guardar revoluciones del LIDAR en un JSON (no streaming)

    - Lee config.ini (host, port, timeout, max_retries, retry_delay, scan_mode)
    - Captura N revoluciones
    - Guarda un JSON con metadatos y lista de revoluciones/puntos
"""

from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path

from lidarclient import LidarClient
from lidarclient.config import ConfigError, load_config


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Guardar datos del LIDAR en JSON.")
    parser.add_argument(
        "--revs",
        type=int,
        default=3,
        help="Número de revoluciones a capturar (default: 3).",
    )
    parser.add_argument(
        "--out",
        type=Path,
        default=Path("lidar_scans.json"),
        help="Ruta de salida del JSON (default: lidar_scans.json).",
    )
    parser.add_argument(
        "--indent",
        type=int,
        default=2,
        help="Indentación del JSON (default: 2). Usa 0 para compacto.",
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

    session_timestamp = datetime.now(timezone.utc).isoformat()

    data: dict = {
        "meta": {
            "timestamp_iso": session_timestamp,
            "scan_mode": config["scan_mode"],
            "host": config["host"],
            "port": config["port"],
        },
        "revolutions": [],
    }

    try:
        client.connect_with_retry()
        print(f"Conectado a {config['host']}:{config['port']}")
        print(f"Modo de escaneo: {config['scan_mode']}")
        print(f"Capturando {args.revs} revoluciones...")

        total_points = 0

        for rev_index in range(args.revs):
            rev_timestamp = datetime.now(timezone.utc).isoformat()
            scan = client.get_scan()

            points = []
            for point_index, (quality, angle, distance) in enumerate(scan):
                # En Express, quality puede ser None ->
                #           en JSON se guardará como null.
                points.append(
                    {
                        "point_index": point_index,
                        "angle_deg": angle,
                        "distance_mm": distance,
                        "quality": quality,
                    }
                )

            data["revolutions"].append(
                {
                    "rev_index": rev_index,
                    "timestamp_iso": rev_timestamp,
                    "points": points,
                }
            )

            total_points += len(scan)
            print(f"Rev {rev_index + 1}/{args.revs}: {len(scan)} puntos")

        indent = None if args.indent == 0 else args.indent
        out_path.write_text(json.dumps(data, indent=indent), encoding="utf-8")

        print(f"\nJSON guardado en: {out_path.resolve()}")
        print(f"Total puntos: {total_points}")
        return 0

    except KeyboardInterrupt:
        print("\nInterrumpido por usuario.")
        return 130
    except Exception as e:
        print(f"\nError: {e}")
        return 1
    finally:
        client.disconnect()


if __name__ == "__main__":
    raise SystemExit(main())
