"""
Cliente para conectarse al servidor LIDAR TCP y recibir revoluciones.
"""

import pickle
import socket


class LidarClient:
    """
    Cliente para recibir datos del RPLIDAR A1 a través de TCP.
    
    Ejemplo de uso:
        client = LidarClient('192.168.1.100', 5000)
        client.connect()
        scan = client.get_scan()
        print(f"Recibidos {len(scan)} puntos")
        client.disconnect()
    """
    
    def __init__(self, host, port=5000):
        """
        Inicializa el cliente.
        
        Args:
            host (str): Dirección IP de la Raspberry Pi
            port (int): Puerto del servidor (por defecto 5000)
        """
        self.host = host
        self.port = port
        self.socket = None
        self.connected = False
    
    def connect(self):
        """Conecta al servidor LIDAR."""
        if self.connected:
            raise Exception("Ya estás conectado al servidor")
        
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.connect((self.host, self.port))
        self.connected = True
        print(f"✓ Conectado a {self.host}:{self.port}")
    
    def get_scan(self):
        """
        Recibe una revolución completa del LIDAR.
        
        Returns:
            list: Lista de tuplas (calidad, ángulo, distancia)
                  - calidad: int (0-15)
                  - ángulo: float (grados, 0-360)
                  - distancia: float (milímetros)
        """
        if not self.connected:
            raise Exception("Debes conectarte primero con connect()")
        
        # Recibir tamaño (4 bytes)
        tamaño_bytes = self.socket.recv(4)
        if len(tamaño_bytes) == 0:
            raise Exception("Conexión cerrada por el servidor")
        
        tamaño = int.from_bytes(tamaño_bytes, byteorder='big')
        
        # Recibir datos completos
        datos_serializados = b''
        while len(datos_serializados) < tamaño:
            paquete = self.socket.recv(tamaño - len(datos_serializados))
            if len(paquete) == 0:
                raise Exception("Conexión interrumpida")
            datos_serializados += paquete
        
        # Deserializar
        scan_data = pickle.loads(datos_serializados)
        return scan_data
    
    def disconnect(self):
        """Cierra la conexión con el servidor."""
        if self.connected and self.socket:
            self.socket.close()
            self.connected = False
            print("✓ Desconectado del servidor")
    
    def __enter__(self):
        """Soporte para context manager (with)."""
        self.connect()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Cierra automáticamente al salir del with."""
        self.disconnect()
