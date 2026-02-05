# Changelog

All notable changes to this project will be documented in this file.

## [0.2.0] - 2026-02-05

### Changed
- **BREAKING**: Migrated from ROS 2 architecture to direct TCP socket communication
- Replaced `create3_lidar_client` (ROS 2) with `lidarclient` (pure Python TCP client)
- Server now uses `rplidar-roboticia` library instead of ROS 2 nodes

### Added
- New `lidarclient` Python package for TCP-based LIDAR data access
- Server TCP script (`servidor_lidar_tcp.py`) for Raspberry Pi 4
- Example scripts:
  - `examples/simplescan.py`: Basic single revolution capture
  - `examples/continuousstream.py`: Continuous streaming with statistics
  - `examples/printscanstub.py`: ROS 2 LaserScan-compatible format
- Automated CI/CD with ruff linting and pytest

### Removed
- ROS 2 dependencies (rclpy, sensor_msgs)
- `src/create3_lidar_client` package (ROS 2 implementation)
- Launch files and ROS 2 configuration

---

## [0.0.1] - 2024-XX-XX

### Added
- Initial repository structure
- Test branch protection
