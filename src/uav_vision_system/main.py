import time

import cv2

from uav_vision_system.camera.camera_stream import CameraStream
from uav_vision_system.communication.uart_sender import UartSender
from uav_vision_system.config import AppConfig
from uav_vision_system.detectors.landing_apriltag import LandingAprilTagDetector
from uav_vision_system.display.hud import draw_landing_hud


def main() -> None:
    config = AppConfig()

    camera = CameraStream(config.camera)
    detector = LandingAprilTagDetector(config.landing_tag)

    uart = None
    if config.uart.enabled:
        uart = UartSender(
            port=config.uart.port,
            baudrate=config.uart.baudrate,
        )

    last_uart_time = 0.0
    uart_interval = 1.0 / max(config.uart.send_hz, 1)

    try:
        while True:
            ok, frame = camera.read()
            if not ok:
                break

            result = detector.update(frame)
            draw_landing_hud(frame, result)

            now = time.time()
            if uart is not None and now - last_uart_time >= uart_interval:
                uart.send(result)
                last_uart_time = now

            cv2.imshow("UAV Vision System - Landing Demo", frame)

            if cv2.waitKey(1) & 0xFF == ord("q"):
                break

    finally:
        camera.release()
        if uart is not None:
            uart.close()
        cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
