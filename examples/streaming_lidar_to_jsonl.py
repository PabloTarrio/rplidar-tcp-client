#!/usr/bin/env python3

import argparse
import configparser
import json
import pickle
import socket
import sys
from datetime import datetime, timezone
from pathlib import Path


def iso_now():
    return datetime.now(timezone.utc).isoformat()


def parse_args():
    parser = argparse.ArgumentParser(
        description=("Stream LIDAR revoluciones a JSONL (una revolución por linea).")
    )
    parser.add_argument(
        "--config",
        default="config.ini",
        help="Path a config.ini (REQUERIDO).",
    )
    parser.add_argument("--out", required=True, help="Salida .jsonl path.")
    parser.add_argument(
        "--revs",
        type=int,
        default=None,
        help=("Número de revoluciones a capturar; si se omite, corre hasta Ctrl+C."),
    )

    parser.add_argument(
        "--host",
        default=None,
        help="Override config.ini [lidar] host.",
    )
    parser.add_argument(
        "--port",
        type=int,
        default=None,
        help="Override config.ini [lidar] port.",
    )
    parser.add_argument(
        "--mode",
        default=None,
        help="Override config.ini [lidar] scan_mode.",
    )

    return parser.parse_args()


def load_config_or_die(config_path: str) -> configparser.ConfigParser:
    path = Path(config_path)
    if not path.is_file():
        msg = f"config.ini requerido y no encontrado: {path}"
        raise FileNotFoundError(msg)

    cfg = configparser.ConfigParser()
    cfg.read(path, encoding="utf-8")

    if "lidar" not in cfg:
        raise KeyError("Falta la sección [lidar] en config.ini")

    return cfg


def resolve(cli_value, cfg_section, key: str, fallback):
    if cli_value is not None:
        return cli_value

    if cfg_section is not None:
        value = cfg_section.get(key, fallback="").strip()
        if value != "":
            return value

    return fallback


def recv_exact(sock: socket.socket, n: int) -> bytes:
    data = bytearray()
    while len(data) < n:
        chunk = sock.recv(n - len(data))
        if not chunk:
            raise ConnectionError("Socket cerrado mientras se recibían datos")
        data.extend(chunk)
    return bytes(data)


def recv_pickle_frame(sock: socket.socket):
    header = recv_exact(sock, 4)
    size = int.from_bytes(header, byteorder="big")
    payload = recv_exact(sock, size)
    return pickle.loads(payload)


def main():
    args = parse_args()
    cfg = load_config_or_die(args.config)
    lidar = cfg["lidar"]

    host = resolve(args.host, lidar, "host", "192.168.1.101")
    port = int(resolve(args.port, lidar, "port", "5000"))
    mode = str(resolve(args.mode, lidar, "scan_mode", "express")).lower()

    meta = {
        "timestamp_iso": iso_now(),
        "scan_mode": mode,
        "host": host,
        "port": port,
    }

    print(f"Conectando a {host}:{port}...", file=sys.stderr)
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect((host, port))
    print(f"Conectado a {host}:{port}", file=sys.stderr)

    mode_wire = mode.strip().upper()
    if mode_wire == "NORMAL":
        mode_wire = "STANDARD"
    if mode_wire not in ("STANDARD", "EXPRESS"):
        mode_wire = "EXPRESS"

    sock.sendall(mode_wire.encode("utf-8"))
    print(f"Modo enviado: {mode_wire}", file=sys.stderr)

    rev_index = 0
    try:
        with open(args.out, "w", encoding="utf-8") as f:
            try:
                while True:
                    scan_data = recv_pickle_frame(sock)

                    points = []
                    for meas in scan_data:
                        if not isinstance(meas, (tuple, list)) or len(meas) < 3:
                            continue

                        quality, angle, dist = meas[0], meas[1], meas[2]
                        if angle is None or dist is None:
                            continue

                        try:
                            angle_f = float(angle)
                            dist_i = int(dist)
                        except (TypeError, ValueError):
                            continue

                        q = None if quality is None else int(quality)

                        points.append(
                            {
                                "point_index": len(points),
                                "angle_deg": angle_f,
                                "distance_mm": dist_i,
                                "quality": q,
                            }
                        )

                    rev = {
                        "meta": meta,
                        "rev_index": rev_index,
                        "timestamp_iso": iso_now(),
                        "points": points,
                    }

                    f.write(
                        json.dumps(
                            rev,
                            ensure_ascii=False,
                            separators=(",", ":"),
                        )
                        + "\n"
                    )
                    f.flush()

                    rev_index += 1
                    if args.revs is not None and rev_index >= args.revs:
                        break

            except KeyboardInterrupt:
                print("\nInterrumpido por Ctrl+C, cerrando...", file=sys.stderr)

    finally:
        sock.close()

    print(
        f"OK: escrito {rev_index} revoluciones en {args.out}",
        file=sys.stderr,
    )


if __name__ == "__main__":
    main()
