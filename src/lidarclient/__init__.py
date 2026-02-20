"""
Librería cliente para RPLIDAR A1 vía TCP.
"""

from .client import (
    LidarClient,
    LidarConnectionError,
    LidarDataError,
    LidarTimeoutError,
)
from .config import ConfigError, load_config

__version__ = "1.0.0"
__all__ = [
    "LidarClient",
    "LidarConnectionError",
    "LidarDataError",
    "LidarTimeoutError",
    "ConfigError",
    "load_config",
]
