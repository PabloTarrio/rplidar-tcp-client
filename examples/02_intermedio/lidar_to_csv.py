"""
=============================================================================
EJEMPLO 7: Guardar Revoluciones del LIDAR en Archivo CSV
=============================================================================

OBJETIVO:
    Capturar revoluciones del LIDAR y exportarlas a un archivo CSV para
    analisis posterior en herramientas como Excel, LibreOffice o Python pandas.

REQUISITOS PREVIOS:
    - Haber completado ejemplos basicos de captura
    - Conocer formato CSV (Comma-Separated Values)
    - (Opcional) Familiaridad con pandas para analisis de datos

CONCEPTOS QUE APRENDERAS:
    - Como exportar datos LIDAR a formato tabular
    - Uso de csv.DictWriter para escritura estructurada
    - Manejo de argumentos de linea de comandos con argparse
    - Creacion de directorios automatica con pathlib
    - Timestamps ISO 8601 para marcar temporalmente los datos
    - Manejo de valores None en CSV (modo Express)

CASOS DE USO PRACTICOS:
    - Crear datasets para machine learning
    - Analisis estadistico offline con pandas/R
    - Compartir datos con herramientas externas (Excel, MATLAB)
    - Generar reportes de mediciones
    - Debugging: comparar mediciones en diferentes momentos
    - Documentacion de experimentos

FORMATO DEL CSV:
    Columnas: timestamp_iso, scan_mode, rev_index, point_index, angle_deg, distance_mm, quality
    - Una fila por cada punto del LIDAR
    - Timestamp repetido para todos los puntos de la misma revolucion
    - Facil de agrupar/filtrar en pandas por revolucion o timestamp

TIEMPO ESTIMADO: 15 minutos
=============================================================================
"""

from __future__ import annotations

import argparse
import csv
from datetime import datetime, timezone
from pathlib import Path

from lidarclient import LidarClient
from lidarclient.config import ConfigError, load_config


# =============================================================================
# DEFINICION DE COLUMNAS DEL CSV
# =============================================================================
# Estructura del CSV de salida:
#
# - timestamp_iso: Marca temporal ISO 8601 (ej: 2026-02-13T16:30:45.123456+00:00)
#                  Se repite para todos los puntos de la misma revolucion
#                  Permite agrupar revoluciones por tiempo en analisis posterior
#
# - scan_mode: Modo de escaneo usado (Standard o Express)
#              Util si mezclas datos de diferentes modos en un mismo dataset
#
# - rev_index: Indice de la revolucion (0, 1, 2, ...)
#              Identifica a que revolucion pertenece cada punto
#
# - point_index: Indice del punto dentro de la revolucion (0, 1, 2, ...)
#                Preserva el orden original de captura
#
# - angle_deg: Angulo en grados (0.0 - 360.0)
#              Direccion de la medicion
#
# - distance_mm: Distancia en milimetros
#                0 = medicion invalida (sin objeto detectado)
#
# - quality: Calidad de la medicion (0-15 en Standard, vacio en Express)
#            Indica confianza en la medicion

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
    """
    Parsea argumentos de linea de comandos.
    
    Argumentos soportados:
        --revs N: Numero de revoluciones a capturar (default: 3)
        --out PATH: Ruta del archivo CSV de salida (default: lidar_scans.csv)
    
    Returns:
        Namespace con los argumentos parseados
    
    Ejemplo de uso:
        python lidar_to_csv.py --revs 5 --out datos/experimento1.csv
    """
    
    parser = argparse.ArgumentParser(
        description="Guardar datos LIDAR en CSV para analisis posterior."
    )
    
    # =========================================================================
    # Argumento: Numero de Revoluciones
    # =========================================================================
    # Permite especificar cuantas revoluciones capturar.
    # Mas revoluciones = dataset mas grande, util para analisis estadistico.
    
    parser.add_argument(
        "--revs",
        type=int,
        default=3,
        help="Numero de revoluciones a capturar (default: 3)",
    )
    
    # =========================================================================
    # Argumento: Archivo de Salida
    # =========================================================================
    # Usa pathlib.Path para manejo de rutas multiplataforma (Windows/Linux/Mac).
    # Path automaticamente maneja separadores de directorio correctos.
    
    parser.add_argument(
        "--out",
        type=Path,
        default=Path("lidar_scans.csv"),
        help="Ruta de salida del CSV (default: lidar_scans.csv)",
    )
    
    return parser.parse_args()


def main() -> int:
    """
    Funcion principal que ejecuta la captura y exportacion a CSV.
    
    Flujo:
        1. Cargar configuracion desde config.ini
        2. Parsear argumentos de linea de comandos
        3. Crear cliente LIDAR y conectar
        4. Crear archivo CSV con encabezados
        5. Capturar N revoluciones escribiendo cada punto como fila
        6. Mostrar resumen de filas escritas
        7. Retornar codigo de salida (0=exito, 1=error, 130=Ctrl+C)
    
    Returns:
        Codigo de salida:
        - 0: Exito
        - 1: Error general
        - 2: Error de configuracion o argumentos invalidos
        - 130: Interrumpido por usuario (Ctrl+C)
    """
    
    # =========================================================================
    # PASO 1: Cargar Configuracion
    # =========================================================================
    try:
        config = load_config()
    except ConfigError as e:
        print(f"Error de configuracion: {e}")
        print("Solucion: Verifica que config.ini existe y es valido")
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
    # PASO 3: Parsear Argumentos de Linea de Comandos
    # =========================================================================
    args = parse_args()
    
    # Validar que el numero de revoluciones es positivo
    if args.revs <= 0:
        print("Error: --revs debe ser mayor que 0")
        print("Ejemplo: python lidar_to_csv.py --revs 5")
        return 2
    
    # =========================================================================
    # PASO 4: Preparar Ruta de Salida
    # =========================================================================
    # Usamos pathlib.Path para manejo robusto de rutas.
    # mkdir(parents=True, exist_ok=True) crea directorios intermedios si no existen.
    # Ejemplo: si out_path es "datos/experimento1/scan.csv", crea "datos/experimento1/"
    
    out_path = args.out
    out_path.parent.mkdir(parents=True, exist_ok=True)
    
    try:
        # =====================================================================
        # PASO 5: Conectar al Servidor LIDAR
        # =====================================================================
        client.connect_with_retry()
        print(f"Conectando a {config['host']}:{config['port']}")
        print(f"Modo de escaneo: {config['scan_mode']}")
        print(f"Capturando {args.revs} revoluciones...\n")
        
        # =====================================================================
        # PASO 6: Abrir Archivo CSV y Escribir Encabezados
        # =====================================================================
        # - newline="": Necesario en Windows para evitar lineas en blanco extra
        # - encoding="utf-8": Asegura compatibilidad internacional
        # - DictWriter: Permite escribir filas como diccionarios (mas legible)
        
        with out_path.open("w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=CSV_COLUMNS)
            
            # Escribir fila de encabezados (nombres de columnas)
            writer.writeheader()
            
            # Contador de puntos totales escritos
            total_points = 0
            
            # =================================================================
            # PASO 7: Bucle de Captura de Revoluciones
            # =================================================================
            for rev_index in range(args.revs):
                # -------------------------------------------------------------
                # 7.1: Generar Timestamp para esta Revolucion
                # -------------------------------------------------------------
                # Usamos UTC (timezone.utc) para timestamps consistentes
                # independientes de la zona horaria local.
                # ISO 8601 es el formato estandar internacional: YYYY-MM-DDTHH:MM:SS.mmmmmm+00:00
                #
                # El timestamp se repite para TODOS los puntos de esta revolucion,
                # permitiendo agrupar facilmente en analisis posterior:
                # df.groupby('timestamp_iso') en pandas
                
                timestamp_iso = datetime.now(timezone.utc).isoformat()
                
                # -------------------------------------------------------------
                # 7.2: Capturar Revolucion Completa
                # -------------------------------------------------------------
                scan = client.get_scan()
                
                # -------------------------------------------------------------
                # 7.3: Escribir Cada Punto como una Fila en el CSV
                # -------------------------------------------------------------
                # Iteramos con enumerate para obtener el indice del punto.
                # Cada punto se convierte en un diccionario que coincide
                # con CSV_COLUMNS.
                
                for point_index, (quality, angle, distance) in enumerate(scan):
                    # ---------------------------------------------------------
                    # Manejo de Quality en Modo Express
                    # ---------------------------------------------------------
                    # En modo Express, quality es None.
                    # Guardamos string vacio "" en CSV en lugar de "None"
                    # para mejor compatibilidad con Excel y pandas.
                    #
                    # En pandas se puede convertir a NaN facilmente:
                    # df['quality'] = pd.to_numeric(df['quality'], errors='coerce')
                    
                    row = {
                        "timestamp_iso": timestamp_iso,
                        "scan_mode": config["scan_mode"],
                        "rev_index": rev_index,
                        "point_index": point_index,
                        "angle_deg": angle,
                        "distance_mm": distance,  # 0 = medicion invalida
                        "quality": "" if quality is None else quality,
                    }
                    
                    # Escribir fila al CSV
                    writer.writerow(row)
                
                # Actualizar contador total
                total_points += len(scan)
                
                # Mostrar progreso
                print(f"  Rev {rev_index + 1}/{args.revs}: {len(scan)} puntos")
        
        # =====================================================================
        # PASO 8: Mostrar Resumen Final
        # =====================================================================
        print(f"\nCSV guardado exitosamente en: {out_path.resolve()}")
        print(f"Total de filas (puntos): {total_points}")
        print(f"Total de revoluciones: {args.revs}")
        print(f"\nPara analizar en pandas:")
        print(f"  import pandas as pd")
        print(f"  df = pd.read_csv('{out_path}')")
        print(f"  df['quality'] = pd.to_numeric(df['quality'], errors='coerce')")
        print(f"  print(df.groupby('rev_index')['distance_mm'].describe())")
        
        return 0  # Codigo de exito
    
    except KeyboardInterrupt:
        # =====================================================================
        # Manejo de Ctrl+C
        # =====================================================================
        print("\n\nInterrumpido por el usuario")
        print("Archivo CSV puede estar incompleto")
        return 130  # Codigo estandar Unix para SIGINT (Ctrl+C)
    
    except Exception as e:
        # =====================================================================
        # Manejo de Errores Generales
        # =====================================================================
        print(f"\nError durante la captura: {e}")
        print("\nSoluciones posibles:")
        print("  - Verifica que el servidor LIDAR esta corriendo")
        print("  - Verifica permisos de escritura en el directorio de salida")
        print("  - Verifica espacio en disco disponible")
        return 1  # Codigo de error general
    
    finally:
        # =====================================================================
        # Desconexion Limpia (Siempre se Ejecuta)
        # =====================================================================
        client.disconnect()


# =============================================================================
# EJERCICIOS SUGERIDOS PARA PRACTICAR:
# =============================================================================
#
# 1. BASICO: Modifica el script para añadir una columna "distance_m"
#    con la distancia en metros (distance_mm / 1000)
#    Facilita el analisis posterior sin conversiones.
#
# 2. INTERMEDIO: Añade una columna "is_valid" (booleano) que sea True
#    si distance_mm > 0, False si no. Util para filtros rapidos.
#    Pista: row["is_valid"] = distance > 0
#
# 3. AVANZADO: Captura con frecuencia fija usando time.sleep() entre
#    revoluciones. Añade columna "elapsed_seconds" midiendo tiempo
#    desde el inicio. Util para analizar series temporales.
#
# 4. ANALISIS: Usa pandas para cargar el CSV y genera:
#    - Histograma de distancias por revolucion
#    - Grafico polar de puntos (angle vs distance)
#    - Estadisticas de calidad por rango de distancias
#
# 5. EXPORTACION AVANZADA: Crea una version que guarde en formato
#    Parquet en lugar de CSV. Parquet es mas eficiente para datasets grandes:
#    import pyarrow.parquet as pq
#    df.to_parquet('lidar_scans.parquet')
#
# =============================================================================

if __name__ == "__main__":
    raise SystemExit(main())
