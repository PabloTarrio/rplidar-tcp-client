#!/usr/bin/env python3
"""
Servidor TCP para RPLIDAR A1 en Raspberry Pi 4.

Este script se ejecuta en la Raspberry Pi y:
1. Se conecta al RPLIDAR A1 vía puerto serie
2. Captura revoluciones completas del sensor
3. Envía los datos serializados a clientes TCP conectados
"""

import pickle
import socket
import time

from rplidar import RPLidar

# Configuración
LIDAR_PORT = "/dev/ttyUSB0"
TCP_HOST = "0.0.0.0"  # Escucha en todas las interfaces
TCP_PORT = 5000

print("=" * 60)
print("SERVIDOR LIDAR TCP (modo continuo)")
print("=" * 60)

# Conectar al LIDAR
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
            # Obtener generador de escaneos
            scan_generator = lidar.iter_scans()
            
            # Capturar una revolución
            scan_data = next(scan_generator)
            print(f"✓ Capturados {len(scan_data)} puntos")
            
            # Serializar y enviar
            datos_serializados = pickle.dumps(scan_data)
            tamano = len(datos_serializados)
            
            # Enviar primero el tamaño (4 bytes)
            cliente.sendall(tamano.to_bytes(4, byteorder='big'))
            # Luego los datos
            cliente.sendall(datos_serializados)
            
            print(f"✓ Enviados {tamano} bytes al cliente")
            
        except Exception as e:
            print(f"✗ Error: {e}")
        finally:
            cliente.close()
            print("✓ Cliente desconectado")

except KeyboardInterrupt:
    print("\n\n⚠ Interrupción detectada! Deteniendo servidor...")
finally:
    servidor.close()
    lidar.stop()
    lidar.disconnect()
    print("=" * 60)
    print("Servidor cerrado correctamente")
    print("=" * 60)
