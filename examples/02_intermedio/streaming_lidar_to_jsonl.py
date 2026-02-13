#!/usr/bin/env python3
"""
=============================================================================
EJEMPLO 9: Stream Continuo de Revoluciones a Archivo JSONL
=============================================================================

OBJETIVO:
    Capturar revoluciones del LIDAR continuamente y guardarlas en formato
    JSONL (JSON Lines: una revolucion por linea), ideal para logging de
    sesiones largas sin cargar todo en memoria.

REQUISITOS PREVIOS:
    - Haber completado lidar_to_json.py
    - Entender diferencia entre JSON y JSONL
    - Conocer conceptos de streaming y procesamiento incremental

CONCEPTOS QUE APRENDERAS:
    - Diferencia entre JSON (archivo completo) y JSONL (stream de lineas)
    - Comunicacion TCP directa con sockets Python (sin LidarClient)
    - Protocolo de comunicacion del servidor LIDAR (pickle sobre TCP)
    - Escritura incremental con flush() para persistencia inmediata
    - Override de configuracion via argumentos CLI
    - Procesamiento de datos en tiempo real sin buffers grandes

CASOS DE USO PRACTICOS:
    - Logging continuo de datos LIDAR en produccion
    - Generar datasets grandes sin consumir memoria
    - Procesamiento posterior linea a linea (streaming analytics)
    - Monitoreo de largo plazo (horas/dias)
    - Integracion con pipelines de datos (Kafka, Spark Streaming)
    - Debugging de comportamiento temporal del LIDAR

FORMATO JSONL vs JSON:
    JSON estandar:
        {"revolutions": [rev1, rev2, rev3]}  # Todo en memoria
    
    JSONL (JSON Lines):
        {"rev": rev1}
        {"rev": rev2}
        {"rev": rev3}
        # Cada linea es JSON independiente, procesable incrementalmente

VENTAJAS JSONL:
    + Escritura incremental: no espera al final
    + Memoria constante: no acumula datos en RAM
    + Procesable linea a linea: cat file.jsonl | jq
    + Resistente a interrupciones: datos ya escritos se preservan
    + Ideal para streams infinitos

DESVENTAJAS JSONL:
    - No es JSON valido (no parseable con json.load() directo)
    - Requiere procesamiento linea por linea
    - Sin metadatos globales de sesion al inicio

DIFERENCIA CON OTROS EJEMPLOS:
    - Este script NO usa LidarClient, implementa comunicacion TCP directa
    - Muestra el protocolo de bajo nivel del servidor LIDAR
    - Mas control pero mas complejidad

TIEMPO ESTIMADO: 20 minutos
=============================================================================
"""

import argparse
import configparser
import json
import pickle
import socket
import sys
from datetime import datetime, timezone
from pathlib import Path


def iso_now():
    """
    Genera timestamp ISO 8601 en UTC.
    
    Returns:
        String con formato: 2026-02-13T16:30:45.123456+00:00
    
    Nota:
        Usamos UTC para timestamps consistentes independientes de zona horaria.
        ISO 8601 es el estandar internacional para fechas/horas.
    """
    return datetime.now(timezone.utc).isoformat()


def parse_args():
    """
    Parsea argumentos de linea de comandos.
    
    Argumentos:
        --config PATH: Ruta a config.ini (default: config.ini)
        --out PATH: Archivo JSONL de salida (REQUERIDO)
        --revs N: Numero de revoluciones a capturar (omitir = infinito)
        --host IP: Override de host del config.ini
        --port N: Override de port del config.ini
        --mode MODE: Override de scan_mode del config.ini
    
    Returns:
        Namespace con argumentos parseados
    
    Ejemplos de uso:
        # Stream finito: 100 revoluciones
        python streaming_lidar_to_jsonl.py --config config.ini --out data.jsonl --revs 100
        
        # Stream infinito hasta Ctrl+C
        python streaming_lidar_to_jsonl.py --config config.ini --out data.jsonl
        
        # Override de configuracion
        python streaming_lidar_to_jsonl.py --config config.ini --out data.jsonl --host 192.168.1.105 --mode express
    """
    
    parser = argparse.ArgumentParser(
        description="Stream continuo de revoluciones LIDAR a formato JSONL."
    )
    
    parser.add_argument(
        "--config",
        default="config.ini",
        help="Path a config.ini (default: config.ini).",
    )
    
    parser.add_argument(
        "--out",
        required=True,
        help="Ruta del archivo .jsonl de salida (REQUERIDO).",
    )
    
    parser.add_argument(
        "--revs",
        type=int,
        default=None,
        help="Numero de revoluciones a capturar; si se omite, corre hasta Ctrl+C.",
    )
    
    # Overrides opcionales de configuracion
    parser.add_argument(
        "--host",
        default=None,
        help="Override de host del config.ini [lidar] host.",
    )
    
    parser.add_argument(
        "--port",
        type=int,
        default=None,
        help="Override de port del config.ini [lidar] port.",
    )
    
    parser.add_argument(
        "--mode",
        default=None,
        help="Override de scan_mode del config.ini [lidar] scan_mode.",
    )
    
    return parser.parse_args()


def load_config_or_die(config_path: str) -> configparser.ConfigParser:
    """
    Carga config.ini o termina el programa si no existe/es invalido.
    
    Args:
        config_path: Ruta al archivo config.ini
    
    Returns:
        ConfigParser con la configuracion cargada
    
    Raises:
        FileNotFoundError: Si config.ini no existe
        KeyError: Si falta la seccion [lidar]
    """
    
    path = Path(config_path)
    if not path.is_file():
        msg = f"config.ini requerido y no encontrado: {path}"
        raise FileNotFoundError(msg)
    
    cfg = configparser.ConfigParser()
    cfg.read(path, encoding="utf-8")
    
    # Validar que existe la seccion [lidar]
    if "lidar" not in cfg:
        raise KeyError("Falta la seccion [lidar] en config.ini")
    
    return cfg


def resolve(cli_value, cfg_section, key: str, fallback):
    """
    Resuelve valor final con prioridad: CLI > config.ini > fallback.
    
    Orden de prioridad:
        1. Valor de linea de comandos (--host, --port, --mode)
        2. Valor en config.ini [lidar]
        3. Valor por defecto (fallback)
    
    Args:
        cli_value: Valor pasado por CLI (puede ser None)
        cfg_section: Seccion del ConfigParser
        key: Clave a buscar en la seccion
        fallback: Valor por defecto si no hay otro
    
    Returns:
        Valor resuelto segun prioridad
    
    Ejemplo:
        # CLI tiene prioridad sobre config.ini
        host = resolve(args.host, cfg['lidar'], 'host', '192.168.1.101')
    """
    
    # Prioridad 1: Argumento de linea de comandos
    if cli_value is not None:
        return cli_value
    
    # Prioridad 2: Valor en config.ini
    if cfg_section is not None:
        value = cfg_section.get(key, fallback="").strip()
        if value != "":
            return value
    
    # Prioridad 3: Fallback por defecto
    return fallback


def recv_exact(sock: socket.socket, n: int) -> bytes:
    """
    Recibe exactamente N bytes del socket, bloqueando hasta completar.
    
    Esta funcion es necesaria porque sock.recv(n) puede devolver MENOS
    de n bytes incluso si hay mas datos disponibles. Debemos llamar
    recv() en bucle hasta acumular exactamente n bytes.
    
    Args:
        sock: Socket TCP conectado
        n: Numero exacto de bytes a recibir
    
    Returns:
        Bytes recibidos (longitud exacta = n)
    
    Raises:
        ConnectionError: Si el socket se cierra antes de recibir n bytes
    
    Uso:
        # Protocolo: primero 4 bytes de longitud, luego payload
        header = recv_exact(sock, 4)
        size = int.from_bytes(header, 'big')
        data = recv_exact(sock, size)
    """
    
    data = bytearray()
    while len(data) < n:
        # Intentar recibir los bytes restantes
        chunk = sock.recv(n - len(data))
        
        # Si recv() devuelve vacio, el socket se cerro
        if not chunk:
            raise ConnectionError("Socket cerrado mientras se recibian datos")
        
        data.extend(chunk)
    
    return bytes(data)


def recv_pickle_frame(sock: socket.socket):
    """
    Recibe un frame del protocolo del servidor LIDAR.
    
    PROTOCOLO DEL SERVIDOR LIDAR:
        1. Enviar modo de escaneo: "STANDARD" o "EXPRESS" (UTF-8)
        2. Recibir frames en bucle:
           - 4 bytes: tamaño del payload (big-endian uint32)
           - N bytes: payload serializado con pickle
           - Deserializar payload -> lista de tuplas (quality, angle, distance)
    
    Este protocolo usa pickle (serializacion binaria de Python) para
    enviar estructuras de datos complejas de forma eficiente.
    
    Args:
        sock: Socket TCP conectado al servidor LIDAR
    
    Returns:
        Lista de tuplas: [(quality, angle, distance), ...]
        - quality: int 0-15 o None
        - angle: float 0-360
        - distance: int en milimetros
    
    Raises:
        ConnectionError: Si el socket se cierra inesperadamente
        pickle.UnpicklingError: Si el payload esta corrupto
    """
    
    # Paso 1: Leer 4 bytes de header (tamaño del frame)
    header = recv_exact(sock, 4)
    size = int.from_bytes(header, byteorder="big")
    
    # Paso 2: Leer exactamente 'size' bytes de payload
    payload = recv_exact(sock, size)
    
    # Paso 3: Deserializar payload con pickle
    # El servidor envia la lista de mediciones serializada con pickle.dumps()
    return pickle.loads(payload)


def main():
    """
    Funcion principal que ejecuta el stream continuo a JSONL.
    
    Flujo:
        1. Parsear argumentos y cargar configuracion
        2. Resolver valores finales (CLI > config > defaults)
        3. Conectar socket TCP al servidor LIDAR
        4. Enviar modo de escaneo (STANDARD o EXPRESS)
        5. Bucle infinito (o hasta N revoluciones):
           a. Recibir frame pickle del servidor
           b. Parsear y validar puntos
           c. Construir objeto JSON de revolucion
           d. Escribir linea JSON al archivo + flush
        6. Cerrar socket y archivo al terminar/interrumpir
    
    Diferencias con LidarClient:
        - Comunicacion TCP directa sin capa de abstraccion
        - Implementacion manual del protocolo pickle
        - Mayor control pero mas complejidad
        - Util para entender como funciona el servidor internamente
    """
    
    # =========================================================================
    # PASO 1: Parsear Argumentos y Cargar Configuracion
    # =========================================================================
    args = parse_args()
    cfg = load_config_or_die(args.config)
    lidar = cfg["lidar"]
    
    # =========================================================================
    # PASO 2: Resolver Valores Finales con Prioridades
    # =========================================================================
    # CLI > config.ini > fallback
    host = resolve(args.host, lidar, "host", "192.168.1.101")
    port = int(resolve(args.port, lidar, "port", "5000"))
    mode = str(resolve(args.mode, lidar, "scan_mode", "express")).lower()
    
    # =========================================================================
    # PASO 3: Preparar Metadatos de Sesion
    # =========================================================================
    # En JSONL, los metadatos se repiten en cada linea (cada revolucion)
    # porque no hay estructura global como en JSON normal.
    meta = {
        "timestamp_iso": iso_now(),
        "scan_mode": mode,
        "host": host,
        "port": port,
    }
    
    # =========================================================================
    # PASO 4: Conectar Socket TCP al Servidor LIDAR
    # =========================================================================
    print(f"Conectando a {host}:{port}...", file=sys.stderr)
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect((host, port))
    print(f"Conectado a {host}:{port}", file=sys.stderr)
    
    # =========================================================================
    # PASO 5: Enviar Modo de Escaneo al Servidor
    # =========================================================================
    # El servidor espera recibir "STANDARD" o "EXPRESS" (mayusculas) al inicio.
    # Normalizamos y validamos el modo antes de enviar.
    
    mode_wire = mode.strip().upper()
    if mode_wire == "NORMAL":
        mode_wire = "STANDARD"  # Normalizar alias
    if mode_wire not in ("STANDARD", "EXPRESS"):
        mode_wire = "EXPRESS"  # Default si es invalido
    
    sock.sendall(mode_wire.encode("utf-8"))
    print(f"Modo enviado: {mode_wire}", file=sys.stderr)
    
    # =========================================================================
    # PASO 6: Bucle de Captura y Escritura JSONL
    # =========================================================================
    rev_index = 0
    
    try:
        # Abrir archivo JSONL para escritura
        with open(args.out, "w", encoding="utf-8") as f:
            try:
                while True:
                    # ---------------------------------------------------------
                    # 6.1: Recibir Frame del Servidor (Revolucion Completa)
                    # ---------------------------------------------------------
                    scan_data = recv_pickle_frame(sock)
                    
                    # ---------------------------------------------------------
                    # 6.2: Parsear y Validar Puntos
                    # ---------------------------------------------------------
                    # El servidor puede enviar datos mal formados o incompletos.
                    # Validamos cada punto antes de incluirlo.
                    
                    points = []
                    for meas in scan_data:
                        # Verificar que es tupla/lista con al menos 3 elementos
                        if not isinstance(meas, (tuple, list)) or len(meas) < 3:
                            continue
                        
                        quality, angle, dist = meas[0], meas[1], meas[2]
                        
                        # Verificar que angle y distance no sean None
                        if angle is None or dist is None:
                            continue
                        
                        # Convertir a tipos correctos con manejo de errores
                        try:
                            angle_f = float(angle)
                            dist_i = int(dist)
                        except (TypeError, ValueError):
                            continue
                        
                        # Quality puede ser None (Express mode)
                        q = None if quality is None else int(quality)
                        
                        # Añadir punto validado
                        points.append(
                            {
                                "point_index": len(points),
                                "angle_deg": angle_f,
                                "distance_mm": dist_i,
                                "quality": q,
                            }
                        )
                    
                    # ---------------------------------------------------------
                    # 6.3: Construir Objeto JSON de Revolucion
                    # ---------------------------------------------------------
                    # Cada linea del JSONL es una revolucion completa con:
                    # - meta: metadatos de sesion
                    # - rev_index: numero de revolucion
                    # - timestamp_iso: timestamp individual de esta revolucion
                    # - points: lista de puntos validados
                    
                    rev = {
                        "meta": meta,
                        "rev_index": rev_index,
                        "timestamp_iso": iso_now(),
                        "points": points,
                    }
                    
                    # ---------------------------------------------------------
                    # 6.4: Escribir Linea JSON + Flush
                    # ---------------------------------------------------------
                    # ensure_ascii=False: permite caracteres UTF-8
                    # separators=(",", ":"): formato compacto sin espacios
                    # + "\n": cada revolucion en una linea
                    # flush(): forzar escritura inmediata al disco
                    #
                    # Flush es CRITICO: sin el, los datos quedan en buffer de
                    # memoria y se pierden si el programa se interrumpe.
                    
                    f.write(
                        json.dumps(
                            rev,
                            ensure_ascii=False,
                            separators=(",", ":"),
                        )
                        + "\n"
                    )
                    f.flush()  # Persistencia inmediata
                    
                    rev_index += 1
                    
                    # ---------------------------------------------------------
                    # 6.5: Verificar Limite de Revoluciones
                    # ---------------------------------------------------------
                    if args.revs is not None and rev_index >= args.revs:
                        break  # Salir del bucle si alcanzamos el limite
            
            except KeyboardInterrupt:
                # Ctrl+C: salir limpiamente
                print("\nInterrumpido por Ctrl+C, cerrando...", file=sys.stderr)
    
    finally:
        # =====================================================================
        # PASO 7: Cerrar Socket (Siempre se Ejecuta)
        # =====================================================================
        sock.close()
    
    # =========================================================================
    # PASO 8: Mostrar Resumen Final
    # =========================================================================
    print(
        f"OK: escritas {rev_index} revoluciones en {args.out}",
        file=sys.stderr,
    )
    
    print(f"\nPara procesar el JSONL:")
    print(f"  # Contar revoluciones")
    print(f"  wc -l {args.out}")
    print(f"\n  # Ver primera revolucion")
    print(f"  head -1 {args.out} | jq")
    print(f"\n  # Extraer todas las distancias promedio")
    print(f"  cat {args.out} | jq '.points[].distance_mm' | awk '{{sum+=$1; n++}} END {{print sum/n}}'")
    print(f"\n  # Cargar en Python")
    print(f"  import json")
    print(f"  with open('{args.out}') as f:")
    print(f"      for line in f:")
    print(f"          rev = json.loads(line)")
    print(f"          print(rev['rev_index'], len(rev['points']))")


# =============================================================================
# EJERCICIOS SUGERIDOS PARA PRACTICAR:
# =============================================================================
#
# 1. BASICO: Añade un contador que imprima cada 10 revoluciones:
#    "Capturadas 10 revoluciones...", "Capturadas 20 revoluciones..."
#    Util para monitoreo de progreso en streams largos.
#
# 2. INTERMEDIO: Implementa reconexion automatica si el socket se cierra.
#    Usa try/except ConnectionError y reintenta conectar cada 5 segundos.
#    Continua escribiendo al mismo archivo JSONL.
#
# 3. AVANZADO: Añade rotacion de archivos: cada N revoluciones o cada X minutos,
#    cierra el archivo actual y abre uno nuevo con timestamp en el nombre.
#    Ejemplo: lidar_20260213_163000.jsonl, lidar_20260213_164000.jsonl
#
# 4. PROCESAMIENTO STREAMING: Crea un script que lea el JSONL en tiempo real
#    (tail -f style) y calcule estadisticas en ventanas deslizantes:
#    - Distancia promedio ultimas 10 revoluciones
#    - Deteccion de anomalias (distancia fuera de rango normal)
#
# 5. INTEGRACION: Modifica el script para enviar cada revolucion a un
#    sistema de mensajeria (Kafka, RabbitMQ, Redis Streams) en lugar de
#    escribir a archivo. Util para arquitecturas de microservicios.
#
# =============================================================================

if __name__ == "__main__":
    main()
