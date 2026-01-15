import math

from create3_lidar_client import ScanClient


def on_scan(msg):
    finite = [r for r in msg.ranges if math.isfinite(r)]
    if finite:
        print(
            f"ranges={len(msg.ranges)} finite={len(finite)} "
            f"min={min(finite):.3f}m max={max(finite):.3f}m "
            f"angle_min={msg.angle_min:.3f} rad angle_max={msg.angle_max:.3f} rad"
        )
    else:
        print(
            f"ranges={len(msg.ranges)} finite=0 "
            f"angle_min={msg.angle_min:.3f} rad angle_max={msg.angle_max:.3f} rad"
        )


def main():
    client = ScanClient()
    client.start(on_scan)
    client.spin()


if __name__ == "__main__":
    main()
