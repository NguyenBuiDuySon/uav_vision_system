import cv2

from uav_vision_system.config import CameraConfig


class CameraStream:
    def __init__(self, config: CameraConfig) -> None:
        self.config = config
        self.cap = cv2.VideoCapture(config.camera_id)

        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, config.width)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, config.height)
        self.cap.set(cv2.CAP_PROP_FPS, config.fps)

        if not self.cap.isOpened():
            raise RuntimeError(f"Cannot open camera ID {config.camera_id}")

    def read(self):
        return self.cap.read()

    def release(self) -> None:
        self.cap.release()