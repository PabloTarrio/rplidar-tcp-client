#!/usr/bin/env python3
"""
Servidor TCP para RPLIDAR A1 en Raspberry Pi 4.
Versión mejorada: inicia escaneo solo cuando hay clientes conectados.
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
print("SERVIDOR LIDAR TCP (modo continuo)")
print("=" * 60)

# Conectar al LIDAR (pero NO iniciar escaneo todavía)
print("\n[1] Conectando al LIDAR...")
lidar = RPLidar(LIDAR_PORT)
time.sleep(2)
print("LIDAR conectado")

# Iniciar servidor TCP
print("\n[2] Iniciando servidor TCP...")
servidor = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
servidor.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
servidor.bind((TCP_HOST, TCP_PORT))
servidor.listen(1)
print(f"Servidor escuchando en puerto {TCP_PORT}")

try:
    while True:
        print("\n[3] Esperando cliente...")
        cliente, direccion = servidor.accept()
        print(f"Cliente conectado desde {direccion}")

        try:
            # Iniciar escaneo SOLO cuando hay un cliente
            print("Iniciando escaneo del LIDAR...")
            scan_generator = lidar.iter_scans()
            revolution_count = 0

            for scan_data in scan_generator:
                revolution_count += 1
                datos_serializados = pickle.dumps(scan_data)
                tamano = len(datos_serializados)

                # Enviar tamaño (4 bytes) + datos
                cliente.sendall(tamano.to_bytes(4, byteorder="big"))
                cliente.sendall(datos_serializados)

                print(
                    f"Rev #{revolution_count}: {len(scan_data)} puntos, {tamano} bytes"
                )

        except (BrokenPipeError, ConnectionResetError):
            print(f"Cliente desconectado después de {revolution_count} revoluciones")
        except Exception as e:
            print(f"Error: {e}")
        finally:
            cliente.close()
            # Detener escaneo cuando el cliente se desconecta
            print("Deteniendo escaneo del LIDAR...")
            lidar.stop()
            time.sleep(0.5)  # Pequeña pausa para limpiar buffer

except KeyboardInterrupt:
    print("\n\nInterrupción detectada! Deteniendo servidor...")
finally:
    servidor.close()
    lidar.stop()
    lidar.disconnect()
    print("=" * 60)
    print("Servidor cerrado correctamente")
    print("=" * 60)
