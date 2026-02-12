"""
Módulo de configuración para el cliente LIDAR

Lee la configuración desde config.ini y proporciona valores por defecto.
"""

import configparser
from pathlib import Path


class ConfigError(Exception):
    """Excepción para errores de configuración"""

    pass


def _get_config_path():
    """
    Busca el archivo config.ini en la raíz del proyecto

    Returns:
        Path: Ruta al archivo config.ini

    Raises:
        ConfigError: Si no encuentra el archivo
    """
    # Buscar config.ini en el directorio de trabajo actual
    config_path = Path("config.ini")

    if not config_path.exists():
        raise ConfigError(
            "No se encontró el archivo 'config.ini'.\n\n"
            "Para crear tu configuración:\n"
            "1. Copia el archivo de ejemplo:\n"
            "   cp config.ini.example config.ini\n\n"
            "2. Edita config.ini con la IP de tu LIDAR asignado\n\n"
            "LIDAR disponibles en el laboratorio:\n"
            "  LIDAR 1: 192.168.1.101\n"
            "  LIDAR 2: 192.168.1.102\n"
            "  LIDAR 3: 192.168.1.103\n"
            "  LIDAR 4: 192.168.1.104\n"
            "  LIDAR 5: 192.168.1.105\n"
            "  LIDAR 6: 192.168.1.106\n"
        )
    return config_path


def load_config():
    """
    Carga la configuración desde config.ini

    Returns:
        dict: Diccionario con la configuración del LIDAR
            - host        (str)  : IP del servidor
            - port        (int)  : Puerto TCP
            - timeout     (float): Timeout en segundos
            - max_retries (int)  : Reintentos de conexión
            - retry_delay (float): Delay entre intentos
            - scan_mode   (str)  : Modo de escaneo ('express' o 'standard')

    Raises:
        ConfigError: Si hay errores en el archivo de configuración
    """

    config_path = _get_config_path()

    parser = configparser.ConfigParser()

    try:
        parser.read(config_path)
    except Exception as e:
        raise ConfigError(f"Error al leer config.ini: {e}")

    # Validar que existe la sección [lidar]
    if "lidar" not in parser:
        raise ConfigError(
            "El archivo config.ini no tiene la sección [lidar].\n"
            "Verifica que el archivo tenga el formato correcto."
        )

    lidar_config = parser["lidar"]

    # Validar que existe el parámetro obligatorio 'host'
    if "host" not in lidar_config:
        raise ConfigError(
            "Falta el parámetro 'host' en config.ini.\n"
            "Añade la IP de tu servidor LIDAR:\n"
            " host = 192.168.1.101"
        )

    # Construir diccionario de configuración con valores por defecto
    try:
        config = {
            "host": lidar_config.get("host"),
            "port": lidar_config.getint("port", fallback=5000),
            "timeout": lidar_config.getfloat("timeout", fallback=5.0),
            "max_retries": lidar_config.getint("max_retries", fallback=3),
            "retry_delay": lidar_config.getfloat("retry_delay", fallback=2.0),
            "scan_mode": lidar_config.get("scan_mode", fallback="express"),
        }

    except ValueError as e:
        raise ConfigError(f"Error en el formato de config.ini: {e}")

    return config


# Valores por defecto si no se usa config.ini
DEFAULT_CONFIG = {
    "host": "192.168.1.101",
    "port": 5000,
    "timeout": 5.0,
    "max_retries": 3,
    "retry_delay": 2.0,
    "scan_mode": "express",
}
