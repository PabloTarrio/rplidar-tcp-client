"""
Servidor TCP para RPLIDAR A1 en Raspberry Pi 4.

Características:
- Inicia escaneo solo cuando hay clientes conectados
- Soporta modos de escaneo configurables (STANDARD/EXPRESS)
- Por defecto: EXPRESS (mayor densidad de puntos)

Protocolo:
1. Cliente conecta via TCP
2. Cliente envía modo: "STANDARD" o "EXPRESS" (opcional, 5s timeout)
3. Servidor configura LIDAR según el modo recibido
4. Servidor envía revoluciones continuamente
"""

import pickle
import socket
import time

from rplidar import RPLidar

# Configuración
LIDAR_PORT = "/dev/ttyUSB0"
TCP_HOST = "0.0.0.0"
TCP_PORT = 5000

print("=" * 60)
print("SERVIDOR LIDAR TCP (modo continuo con selección de escaneo)")
print("=" * 60)

# Conectar al LIDAR (pero NO iniciar escaneo todavía)
print("\n[1] Conectando al LIDAR...")
lidar = RPLidar(LIDAR_PORT)
time.sleep(2)
print("✓ LIDAR conectado")

# Iniciar servidor TCP
print("\n[2] Iniciando servidor TCP...")
servidor = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
servidor.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
servidor.bind((TCP_HOST, TCP_PORT))
servidor.listen(1)
print(f"✓ Servidor escuchando en puerto {TCP_PORT}")

try:
    while True:
        print("\n[3] Esperando cliente...")
        cliente, direccion = servidor.accept()
        print(f"✓ Cliente conectado desde {direccion}")

        try:
            # Recibir comando de modo de escaneo del cliente
            print("  → Esperando configuración del cliente...")
            cliente.settimeout(5.0)  # Timeout de 5s para recibir comando

            try:
                modo_bytes = cliente.recv(10)  # Recibir hasta 10 bytes
                modo = modo_bytes.decode("utf-8").strip().upper()
                print(f"  → Modo recibido: {modo}")
            except socket.timeout:
                modo = "EXPRESS"  # Por defecto si no responde en 5s
                print("  ⚠ Cliente no envió modo en 5s, usando EXPRESS por defecto")
            except Exception as e:
                modo = "EXPRESS"
                print(f"  ⚠ Error al recibir modo ({e}), usando EXPRESS por defecto")

            cliente.settimeout(None)  # Quitar timeout para operación normal

            # Validar y normalizar modo
            if modo not in ["STANDARD", "EXPRESS", "NORMAL"]:
                print(f"  ⚠ Modo '{modo}' inválido, usando EXPRESS por defecto")
                modo = "EXPRESS"

            # Convertir a formato de rplidar-roboticia
            # "STANDARD"/"NORMAL" → 'normal'
            # "EXPRESS" → 'express'
            scan_type = "normal" if modo in ["STANDARD", "NORMAL"] else "express"

            print(f"  ✓ Modo de escaneo configurado: {modo} (scan_type='{scan_type}')")

            # Iniciar escaneo con el modo seleccionado
            print("  → Iniciando escaneo del LIDAR...")
            scan_generator = lidar.iter_scans(scan_type=scan_type, max_buf_meas=3000)
            revolution_count = 0

            for scan_data in scan_generator:
                revolution_count += 1
                datos_serializados = pickle.dumps(scan_data)
                tamano = len(datos_serializados)

                # Enviar tamaño (4 bytes) + datos
                cliente.sendall(tamano.to_bytes(4, byteorder="big"))
                cliente.sendall(datos_serializados)

                print(
                    f"  Rev #{revolution_count}: {len(scan_data)} puntos, "
                    f"{tamano} bytes [{scan_type}]"
                )

        except (BrokenPipeError, ConnectionResetError):
            print(f"✗ Cliente desconectado después de {revolution_count} revoluciones")
        except Exception as e:
            print(f"✗ Error: {e}")
        finally:
            cliente.close()
            # Detener escaneo cuando el cliente se desconecta
            print("  → Deteniendo escaneo del LIDAR...")
            lidar.stop()
            time.sleep(0.5)  # Pequeña pausa para limpiar buffer

except KeyboardInterrupt:
    print("\n\n⚠ Interrupción detectada! Deteniendo servidor...")
finally:
    servidor.close()
    lidar.stop()
    lidar.disconnect()
    print("=" * 60)
    print("Servidor cerrado correctamente")
    print("=" * 60)
