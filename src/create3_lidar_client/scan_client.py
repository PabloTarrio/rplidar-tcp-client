from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, Optional

import rclpy
from rclpy.node import Node
from sensor_msgs.msg import LaserScan

ScanCallback = Callable [[LaserScan], None]

@dataclass
class ScanClientConfig:
  topic: str = "/scan"
  node_name: str = "create3_lidar_client"

class ScanClient:
    def __init__(self, config: ScanClientConfig | None = None) -> None:
        self._config = config or ScanClientConfig()
        self._node: Optional[Node] = None
        self._subscription = None

    def start(self, callback: ScanCallback) -> None:
        rclpy.init()
        self._node = rclpy.create_node(self._config.node_name)
        self._subscription = self._node.create_subscription(
            LaserScan, self._config.topic, callback, 10
        )

    def spin(self) -> None:
        if self._node is None:
            raise RuntimeError("ScanClient not started. Call start() first.")
        rclpy.spin(self._node)

    def close(self) -> None:
        if self._node is not None:
            self._node.destroy_node()
        if rclpy.ok():
            rclpy.shutdown()
        self._node = None
        self._subscription = None
