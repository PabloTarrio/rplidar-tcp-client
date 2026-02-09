"""
Librería cliente para RPLIDAR A1 vía TCP.
"""

from .client import (
    LidarClient,
    LidarConnectionError,
    LidarDataError,
    LidarTimeoutError,
)

__version__ = "0.1.0"
__all__ = [
    "LidarClient",
    "LidarConnectionError",
    "LidarTimeoutError",
    "LidarDataError",
]
