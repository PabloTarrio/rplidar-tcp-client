"""
Cliente para conectarse al servidor LIDAR TCP y recibir revoluciones.
"""

import pickle
import socket


class LidarConnectionError(Exception):
    """Excepción para errores de conexión con el servidor LIDAR."""

    pass


class LidarTimeoutError(Exception):
    """Excepción para timeouts de comunicación con el servidor LIDAR."""

    pass


class LidarDataError(Exception):
    """Excepción para errores en los datos recibidos del LIDAR."""

    pass


class LidarClient:
    """
    Cliente TCP para conectarse a un servidor LIDAR.

    Permite recibir revoluciones completas del LIDAR a través de TCP
    con soporte para selección de modo de escaneo (standard/express).

    Modos de escaneo:
        - 'standard': ~150-360 puntos/revolución (menor densidad)
        - 'express': ~700-800 puntos/revolución (mayor densidad, default)
    """

    def __init__(
        self,
        host,
        port=5000,
        timeout=5.0,
        max_retries=0,
        retry_delay=2.0,
        scan_mode="express",
    ):
        """
        Inicializa el cliente LIDAR.

        Args:
            host (str): Dirección IP del servidor
            port (int): Puerto TCP (default: 5000)
            timeout (float): Timeout en segundos (default: 5.0)
            max_retries (int): Número de reintentos de conexión (default: 0)
            retry_delay (float): Segundos entre reintentos (default: 2.0)
            scan_mode (str): Modo de escaneo 'standard' o 'express' (default: 'express')
        """
        self.host = host
        self.port = port
        self.timeout = timeout
        self.max_retries = max_retries
        self.retry_delay = retry_delay
        self.scan_mode = scan_mode.lower()  # Normalizar a minúsculas
        self.socket = None
        self.connected = False

    def connect(self):
        """
        Conecta al servidor LIDAR y envía el modo de escaneo.

        Raises:
            LidarConnectionError: Si no puede conectarse al servidor
            LidarTimeoutError: Si la conexión tarda demasiado
        """
        if self.connected:
            raise LidarConnectionError("Ya estás conectado al servidor")

        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.settimeout(self.timeout)
            self.socket.connect((self.host, self.port))

            # Enviar modo de escaneo al servidor
            modo_upper = self.scan_mode.upper()
            self.socket.sendall(modo_upper.encode("utf-8"))

            self.connected = True
            print(f"Conectado a {self.host}:{self.port}")
            print(f"Modo de escaneo: {modo_upper}")

        except socket.timeout:
            raise LidarTimeoutError(
                f"Timeout al conectar a {self.host}:{self.port} "
                f"(esperó {self.timeout}s)"
            )
        except ConnectionRefusedError:
            raise LidarConnectionError(
                f"Conexión rechazada por {self.host}:{self.port}. "
                "Verifica que el servidor esté corriendo."
            )
        except OSError as e:
            raise LidarConnectionError(
                f"Error al conectar a {self.host}:{self.port}: {e}"
            )

    def connect_with_retry(self):
        """
        Conecta con el servidor LIDAR con reintentos sutomáticos

        Intenta conectare hasta max_retries, esperando retry_delay
        segundos entre cada intento. Si max_retries = 0 se comporta
        igual que connect.

        Raises:
            LidarConnectionError: Si no puede conectare despeus de
                todos los reintentos.
            LidarTimeoutError: Si la conexión tarda demasiado.
        """
        import time

        # Si no hay reintentos configurados, usar connect() normal
        if self.max_retries == 0:
            self.connect()
            return

        # Intentar conectar con intentos
        last_exception = None
        for intento in range(self.max_retries + 1):
            try:
                if intento == 0:
                    print(f"Conectando a {self.host}:{self.port}...")
                else:
                    print(
                        f"[Intento {intento + 1}/{self.max_retries + 1}] "
                        f"Reintentando conexión a {self.host}:{self.port}..."
                    )

                self.connect()
                return  # Éxito, salir de método

            except (LidarConnectionError, LidarTimeoutError) as e:
                last_exception = e

                if intento < self.max_retries:
                    print(
                        f"Falló: {e}\n"
                        f"Esperando {self.retry_delay} segundos "
                        "antes de reintentar..."
                    )
                    time.sleep(self.retry_delay)
                else:
                    # Último intento falló
                    print(f"Falló después de {self.max_retries + 1} intentos")

        # Si llegamos hasta aquí, todos los intentos fallaron
        raise last_exception

    def get_scan(self):
        """
        Recibe una revolución completa del LIDAR.

        Returns:
            list: Lista de tuplas (calidad, ángulo, distancia)
                  - calidad: int (0-15)
                  - ángulo: float (grados, 0-360)
                  - distancia: float (milímetros)

        Raises:
            LidarConnectionError: Si no está conectado o se perdió la conexión
            LidarTimeoutError: Si no recibe datos en el tiempo esperado
            LidarDataError: Si los datos recibidos están corruptos
        """
        if not self.connected:
            raise LidarConnectionError("Debes conectarte primero con connect()")

        try:
            # Recibir tamaño (4 bytes)
            tamano_bytes = self._recv_exact(4)
            tamano = int.from_bytes(tamano_bytes, byteorder="big")

            # Validar tamaño razonable (entre 100 bytes y 50KB)
            if tamano < 100 or tamano > 50000:
                raise LidarDataError(
                    f"Tamaño de datos inválido: {tamano} bytes. "
                    "Posible corrupción de datos."
                )

            # Recibir datos completos
            datos_serializados = self._recv_exact(tamano)

            # Deserializar
            scan_data = pickle.loads(datos_serializados)
            return scan_data

        except socket.timeout:
            raise LidarTimeoutError(
                f"Timeout esperando datos del servidor (timeout={self.timeout}s)"
            )
        except (ConnectionResetError, BrokenPipeError):
            self.connected = False
            raise LidarConnectionError("El servidor cerró la conexión inesperadamente")
        except pickle.UnpicklingError as e:
            raise LidarDataError(f"Error al deserializar datos: {e}")

    def _recv_exact(self, num_bytes):
        """
        Recibe exactamente num_bytes del socket.

        Args:
            num_bytes (int): Número exacto de bytes a recibir

        Returns:
            bytes: Datos recibidos

        Raises:
            LidarConnectionError: Si la conexión se cierra antes de recibir
                todos los bytes
        """
        datos = b""
        while len(datos) < num_bytes:
            paquete = self.socket.recv(num_bytes - len(datos))
            if len(paquete) == 0:
                self.connected = False
                raise LidarConnectionError("Conexión cerrada por el servidor")
            datos += paquete
        return datos

    def disconnect(self):
        """Cierra la conexión con el servidor."""
        if self.connected and self.socket:
            try:
                self.socket.close()
            except Exception:
                pass
            finally:
                self.connected = False
                self.socket = None
                print("Desconectado del servidor")

    def __enter__(self):
        """Soporte para context manager (with)."""
        self.connect()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Cierra automáticamente al salir del with."""
        self.disconnect()
