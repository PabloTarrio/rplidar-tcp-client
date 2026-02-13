"""
=============================================================================
EJEMPLO 8: Guardar Revoluciones del LIDAR en Archivo JSON
=============================================================================

OBJETIVO:
    Capturar revoluciones del LIDAR y exportarlas a formato JSON estructurado
    con metadatos, util para integracion con aplicaciones web, APIs REST,
    o cualquier sistema que consuma JSON.

REQUISITOS PREVIOS:
    - Haber completado lidar_to_csv.py
    - Conocer formato JSON (JavaScript Object Notation)
    - Entender diferencia entre JSON y CSV (estructurado vs tabular)

CONCEPTOS QUE APRENDERAS:
    - Como exportar datos LIDAR a formato JSON jerarquico
    - Estructura de datos con metadatos + revoluciones + puntos
    - Manejo de valores null en JSON (quality=None en Express)
    - Control de formato JSON (compacto vs indentado)
    - Diferencias entre JSON y JSONL (JSON Lines)

CASOS DE USO PRACTICOS:
    - Integracion con APIs REST y servicios web
    - Intercambio de datos entre aplicaciones JavaScript/TypeScript
    - Configuracion y snapshots de mediciones puntuales
    - Documentacion estructurada de experimentos
    - Procesamiento con jq (herramienta CLI para JSON)
    - Carga en bases de datos NoSQL (MongoDB, CouchDB)

ESTRUCTURA DEL JSON:
    {
      "meta": {
        "timestamp_iso": "2026-02-13T16:30:00Z",
        "scan_mode": "Express",
        "host": "192.168.1.103",
        "port": 5000
      },
      "revolutions": [
        {
          "rev_index": 0,
          "timestamp_iso": "2026-02-13T16:30:01Z",
          "points": [
            {"point_index": 0, "angle_deg": 0.5, "distance_mm": 1250, "quality": null},
            ...
          ]
        },
        ...
      ]
    }

VENTAJAS vs CSV:
    + Jerarquico: revoluciones y puntos claramente agrupados
    + Metadatos: informacion de sesion incluida
    + Tipos: null, bool, numeros nativos (no strings)
    + Legible: indentacion opcional para humans

DESVENTAJAS vs CSV:
    - Mas verboso (mayor tamaño de archivo)
    - Menos compatible con herramientas de analisis tabular (Excel, pandas)
    - Mas lento de parsear para datasets grandes

TIEMPO ESTIMADO: 15 minutos
=============================================================================
"""

from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path

from lidarclient import LidarClient
from lidarclient.config import ConfigError, load_config


def parse_args() -> argparse.Namespace:
    """
    Parsea argumentos de linea de comandos.

    Argumentos soportados:
        --revs N: Numero de revoluciones a capturar (default: 3)
        --out PATH: Ruta del archivo JSON de salida (default: lidar_scans.json)
        --indent N: Espacios de indentacion (default: 2, usa 0 para compacto)

    Returns:
        Namespace con los argumentos parseados

    Ejemplos de uso:
        # JSON indentado (legible)
        python lidar_to_json.py --revs 5 --out datos.json --indent 2

        # JSON compacto (minimo tamaño)
        python lidar_to_json.py --revs 5 --out datos.json --indent 0
    """

    parser = argparse.ArgumentParser(
        description="Guardar datos del LIDAR en formato JSON estructurado."
    )

    parser.add_argument(
        "--revs",
        type=int,
        default=3,
        help="Numero de revoluciones a capturar (default: 3).",
    )

    parser.add_argument(
        "--out",
        type=Path,
        default=Path("lidar_scans.json"),
        help="Ruta de salida del JSON (default: lidar_scans.json).",
    )

    # =========================================================================
    # Argumento: Indentacion JSON
    # =========================================================================
    # - indent > 0: JSON legible con saltos de linea e indentacion
    #   Ventaja: Facil de leer y debuggear
    #   Desventaja: Archivos mas grandes
    #
    # - indent = 0: JSON compacto en una sola linea
    #   Ventaja: Archivos mas pequeños, carga mas rapida
    #   Desventaja: Ilegible para humanos

    parser.add_argument(
        "--indent",
        type=int,
        default=2,
        help="Indentacion del JSON (default: 2). Usa 0 para compacto.",
    )

    return parser.parse_args()


def main() -> int:
    """
    Funcion principal que ejecuta la captura y exportacion a JSON.

    Flujo:
        1. Cargar configuracion desde config.ini
        2. Parsear argumentos de linea de comandos
        3. Crear estructura de datos JSON vacia
        4. Conectar al servidor LIDAR
        5. Capturar N revoluciones, añadiendo cada una a la estructura
        6. Escribir JSON completo al archivo
        7. Mostrar resumen

    Diferencia con CSV:
        - CSV: escritura incremental (fila por fila)
        - JSON: construccion en memoria, escritura unica al final

        Implicacion: JSON requiere mas memoria para datasets grandes.

    Returns:
        Codigo de salida (0=exito, 1=error, 2=config invalida, 130=Ctrl+C)
    """

    # =========================================================================
    # PASO 1: Cargar Configuracion
    # =========================================================================
    try:
        config = load_config()
    except ConfigError as e:
        print(f"Error de configuracion: {e}")
        return 2

    # =========================================================================
    # PASO 2: Crear Cliente LIDAR
    # =========================================================================
    client = LidarClient(
        config["host"],
        port=config["port"],
        timeout=config["timeout"],
        max_retries=config["max_retries"],
        retry_delay=config["retry_delay"],
        scan_mode=config["scan_mode"],
    )

    # =========================================================================
    # PASO 3: Parsear Argumentos
    # =========================================================================
    args = parse_args()

    if args.revs <= 0:
        print("Error: --revs debe ser mayor que 0")
        return 2

    # =========================================================================
    # PASO 4: Preparar Ruta de Salida
    # =========================================================================
    out_path = args.out
    out_path.parent.mkdir(parents=True, exist_ok=True)

    # =========================================================================
    # PASO 5: Timestamp de Sesion (Para Metadatos)
    # =========================================================================
    # Este timestamp marca el inicio de la sesion de captura.
    # Es diferente de los timestamps individuales de cada revolucion.
    # Util para identificar cuando se realizo la captura completa.

    session_timestamp = datetime.now(timezone.utc).isoformat()

    # =========================================================================
    # PASO 6: Inicializar Estructura de Datos JSON
    # =========================================================================
    # Estructura jerarquica de 2 niveles:
    # 1. "meta": Metadatos de la sesion (timestamp, modo, host, port)
    # 2. "revolutions": Lista de revoluciones, cada una con su timestamp y puntos
    #
    # Esta estructura facilita:
    # - Contexto completo de la captura
    # - Agrupacion natural por revolucion
    # - Metadatos accesibles sin parsear todos los datos

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
        # =====================================================================
        # PASO 7: Conectar al Servidor
        # =====================================================================
        client.connect_with_retry()
        print(f"Conectado a {config['host']}:{config['port']}")
        print(f"Modo de escaneo: {config['scan_mode']}")
        print(f"Capturando {args.revs} revoluciones...\n")

        total_points = 0

        # =====================================================================
        # PASO 8: Bucle de Captura de Revoluciones
        # =====================================================================
        for rev_index in range(args.revs):
            # -----------------------------------------------------------------
            # 8.1: Timestamp Individual de esta Revolucion
            # -----------------------------------------------------------------
            # Cada revolucion tiene su propio timestamp, permitiendo
            # analisis temporal preciso entre revoluciones.

            rev_timestamp = datetime.now(timezone.utc).isoformat()

            # -----------------------------------------------------------------
            # 8.2: Capturar Revolucion
            # -----------------------------------------------------------------
            scan = client.get_scan()

            # -----------------------------------------------------------------
            # 8.3: Construir Lista de Puntos
            # -----------------------------------------------------------------
            # Cada punto es un diccionario con sus atributos.
            # En JSON, quality=None se convierte automaticamente en null,
            # que es el valor correcto para "ausencia de valor" en JSON.

            points = []
            for point_index, (quality, angle, distance) in enumerate(scan):
                points.append(
                    {
                        "point_index": point_index,
                        "angle_deg": angle,
                        "distance_mm": distance,
                        "quality": quality,  # None -> null en JSON
                    }
                )

            # -----------------------------------------------------------------
            # 8.4: Añadir Revolucion a la Estructura Principal
            # -----------------------------------------------------------------
            # La revolucion es un diccionario con:
            # - rev_index: indice numerico
            # - timestamp_iso: marca temporal individual
            # - points: lista completa de puntos

            data["revolutions"].append(
                {
                    "rev_index": rev_index,
                    "timestamp_iso": rev_timestamp,
                    "points": points,
                }
            )

            total_points += len(scan)
            print(f"  Rev {rev_index + 1}/{args.revs}: {len(scan)} puntos")

        # =====================================================================
        # PASO 9: Escribir JSON al Archivo
        # =====================================================================
        # json.dumps() convierte la estructura Python a string JSON.
        # - indent=None: JSON compacto (una sola linea)
        # - indent=N: JSON indentado con N espacios por nivel
        #
        # write_text(): escribe string al archivo en una sola operacion atomica

        indent = None if args.indent == 0 else args.indent
        out_path.write_text(json.dumps(data, indent=indent), encoding="utf-8")

        # =====================================================================
        # PASO 10: Mostrar Resumen
        # =====================================================================
        print(f"\nJSON guardado exitosamente en: {out_path.resolve()}")
        print(f"Total de revoluciones: {args.revs}")
        print(f"Total de puntos: {total_points}")

        # Calcular tamaño del archivo
        file_size_kb = out_path.stat().st_size / 1024
        print(f"Tamaño del archivo: {file_size_kb:.2f} KB")

        print("\nPara cargar en Python:")
        print("  import json")
        print(f"  with open('{out_path}') as f:")
        print("      data = json.load(f)")
        print("  print(data['meta'])")
        print("  print(len(data['revolutions']))")

        print("\nPara inspeccionar con jq (CLI):")
        print(f"  jq '.meta' {out_path}")
        print(f"  jq '.revolutions[0].points | length' {out_path}")

        return 0

    except KeyboardInterrupt:
        print("\n\nInterrumpido por usuario.")
        print("Archivo JSON no se creo (captura incompleta)")
        return 130

    except Exception as e:
        print(f"\nError durante la captura: {e}")
        return 1

    finally:
        client.disconnect()


# =============================================================================
# EJERCICIOS SUGERIDOS PARA PRACTICAR:
# =============================================================================
#
# 1. BASICO: Añade un campo "num_revolutions" en "meta" que indique
#    cuantas revoluciones se capturaron. Redundante pero util.
#
# 2. INTERMEDIO: Añade estadisticas por revolucion en "meta":
#    - points_per_revolution: lista de cuantos puntos en cada rev
#    - valid_points_per_revolution: lista de puntos con distance > 0
#    Permite analisis rapido sin parsear todos los puntos.
#
# 3. AVANZADO: Implementa compresion automatica del JSON:
#    import gzip
#    with gzip.open('lidar_scans.json.gz', 'wt') as f:
#        json.dump(data, f)
#    JSON comprime muy bien (reduccion 70-90%).
#
# 4. CONVERSION: Crea un script que convierta JSON -> CSV:
#    Leer JSON, extraer todos los puntos con sus revoluciones,
#    escribir CSV plano. Util para analisis en Excel/pandas.
#
# 5. VALIDACION: Añade un esquema JSON Schema para validar la estructura:
#    import jsonschema
#    Define esquema que valide tipos, rangos, campos requeridos.
#    Garantiza calidad de datos exportados.
#
# =============================================================================

if __name__ == "__main__":
    raise SystemExit(main())
